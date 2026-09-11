# 2026-09-10 — [FDTD-001] Claude — `linear_sim.py` port düzlemi çevirisi düzeltmesi

## Sahiplik

- Görev (Astra dispatch): `fdtd/mrr/linear_sim.py` içindeki port düzlemi
  çevirisini düzelt. Cloud rung-0 kanıtında `flux:bus_through:out` ve
  `flux:bus_drop:out` **ikisi de** `x=8, y=0` üretildi; drop bus gerçek `y`
  merkezine gitmediği için linear sonuç fiziksel kabulde fail-closed reddedildi.
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Yer: git worktree `worktree-fdtd-001-linear-sim`. **Cloud yok, Tidy3D çağrısı
  yok, paket kurulmadı, alt-ajan yok, commit/push yok.** Değişen dosyalar ana
  çalışma kopyasına `??` (commit'siz) olarak kopyalandı; ratification Astra'da.
- Sadece `fdtd/mrr/linear_sim.py` + `tests/fdtd/test_linear_sim.py` değişti.
  `fdtd/tidy3d_build/`, cloud/API kodu, `BACKLOG.md`, `BACKLOGLOG.md`,
  `CHANGELOG.md`, `docs/decisions/`, sözleşme dosyaları ve diğer uncommitted iş
  **değiştirilmedi**. Fizik parametresi seçilmedi.

## Kök neden

`LinearSimulationTranslator._port_plane(port)` tüm kaynak/monitör düzlemlerinin
enine (enjeksiyon ekseni dışı) koordinatlarını sabitliyordu:

```python
"plane_center_um": [x, 0.0, self._stack_top_um() / 2.0]
```

`x` = ±`bus_length_um/2` (doğru, enjeksiyon ekseni), ama `y` her zaman `0.0` ve
`z` her zaman yığın ortası. Add/drop geometride `bus_through` merkez çizgisi
`y = -bus_centre_offset_um`, `bus_drop` ise `y = +bus_centre_offset_um`
(`geometry.py::to_structures`). İki bus monitörü aynı `y=0` çizgisine düşünce
drop bus'ın taşıdığı güç ölçülemedi → fiziksel kabul reddi.

## Düzeltme

`_port_plane` artık token içindeki **yapı adını** alır ve enjeksiyon ekseni
dışındaki koordinatları o yapının (`ring` / `waveguide` primitifi) merkezinden
türetir:

- Yeni yardımcı `LinearSimulationTranslator._port_structure_center_um(structure)`
  → `geometry.to_structures()` içinde adı eşleşen `waveguide` / `ring`
  primitifinin `center_um` değerini döndürür; başka bir şeye işaret eden token
  `TranslationError` ile fail-closed olur (token kapısı `_port_problems` zaten
  önden reddediyor, bu savunma amaçlı bir backstop).
- `_port_plane(structure, port)`:
  - enjeksiyon ekseni (`x`): `center_x ± bus_length_um/2` — semantik değişmedi
    (`center_x = 0.0`), plan hâlâ domain kenarından `domain_padding_um` içeride,
    **PML'e girmiyor**.
  - enine (`y`, `z`): doğrudan yapı merkezinden → `[x, center_y, center_z]`.
- `_source_documents` ve `_monitor_documents` çağrıları `structure` argümanını
  geçirir. `ModeSource`, `FluxMonitor` ve `FieldMonitor` düzlemleri aynı
  yardımcıyı kullandığı için üçü de aynı anda düzeltildi.
- `plane_size_um` = `[0.0, domain_y, domain_z]` (tam enine kesit) — değişmedi.

Çıktı deterministik: `to_structures()` deterministik, `center_x = 0.0` olduğu
için mevcut digest'ler etkilenmez; yalnız `y`/`z` port koordinatları değişir.

### Önce / sonra (sentetik happy-path bundle)

| token | önce | sonra |
| --- | --- | --- |
| `mode:bus_through:in` | `[-10.0, 0.0, 4.65]` | `[-10.0, -7.425, 7.15]` |
| `flux:bus_through:out` | `[10.0, 0.0, 4.65]` | `[10.0, -7.425, 7.15]` |
| `flux:bus_drop:out` | `[10.0, 0.0, 4.65]` | `[10.0, 7.425, 7.15]` |

`bus_centre_offset_um = 7.0 + 0.2 + 0.45/2 = 7.425`;
`z_core = 4.0 + 3.0 + 0.3/2 = 7.15`. Through ve drop `y` artık zıt işaretli.

## Regresyon testleri (`tests/fdtd/test_linear_sim.py::PortPlaneGeometryTest`, 8 test)

- `test_through_and_drop_monitor_y_coordinates_differ` — `through_y != drop_y`,
  biri `< 0`, diğeri `> 0`, ve büyüklükleri `±bus_centre_offset_um`. Bu, cloud
  rung-0 hatasının doğrudan regresyonudur.
- `test_every_port_plane_is_centred_on_its_named_structure` — her port için
  `plane_center` enine koordinatları adı geçen yapının merkezine eşit, `z` =
  silisyum film ortası, enjeksiyon ekseninde merkezden `±bus_length/2`.
- `test_source_on_through_bus_is_on_the_through_centreline`.
- `test_port_planes_stay_out_of_the_pml_region` — her düzlem domain
  yarı-genişliğinden en az bir `domain_padding_um` içeride (x), `|y| < domain_y/2`,
  `0 < z < domain_z`.
- `test_field_monitor_plane_also_follows_its_structure` — `field:bus_drop:out`
  `FieldMonitor` düzlemi de drop merkez çizgisinde ve through'dan farklı.
- `test_port_planes_are_deterministic`.
- `test_single_bus_source_and_monitor_share_one_centreline` — `add_drop=False`
  iken tüm portlar tek (through) çizgide.
- `test_dry_run_still_passes_with_structure_derived_planes`.

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14. Stdlib dışı bağımlılık yok, ağ/cloud yok.

```
$ python -m unittest tests.fdtd.test_linear_sim -b
Ran 59 tests in 0.044s      # 51 mevcut + 8 yeni
OK

$ python -m unittest discover -t . -s . -p "test_*.py" -b
Ran 223 tests in 17.2s      # tam yerel suite, regresyon yok
OK
```

Not: `python -m unittest discover -s tests ...` (yanlış kök) `fdtd` paketini
`tests/fdtd` ile gölgeleyip 4 import hatası verir; bu düzeltmeyle ilgisizdir.
Doğru kök repo köküdür (`-s .`).

## Açık riskler / sınırlar

- `plane_size_um` hâlâ tam domain enine kesitidir. ModeSource için Astra düzlemi
  bus çevresine daraltmak isteyebilir; bu değişiklik yalnız **merkez**
  koordinatını düzeltir, uydurma inset/boyut eklemez.
- `_port_structure_center_um` yalnız `waveguide` / `ring` primitiflerini tanır;
  ileride başka bir port yapısı (ör. taper) eklenirse yardımcı genişletilmeli.
- Mevcut `manifests/fdtd/mrr-linear-001/rung-0.plan.json` eski `y=0` düzlemleriyle
  üretilmiş; yeniden üretimi Astra'ya bırakıldı (bu görevde plan/manifest
  üretilmedi).

## Sıradaki tek adım

Astra: ana çalışma kopyasındaki `??` değişikliği incele; `python -m unittest
discover -t . -s . -p "test_*.py" -b` (223/223) çıktısını kaydet; port düzlemi
çevirisini FDTD-001
linear yakınsama kapısı için onayla; onaylanırsa rung-0 planını yeni port
koordinatlarıyla yeniden üret ve cloud fiziksel kabulünü tekrarla.
