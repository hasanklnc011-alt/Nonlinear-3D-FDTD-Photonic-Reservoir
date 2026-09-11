# 2026-09-10 — [FDTD-001] Claude — `linear_sim.py` port düzlemi *boyutu* düzeltmesi

## Sahiplik

- Görev (Astra dispatch): `fdtd/mrr/linear_sim.py` port düzlemi geometrisini bir
  adım daha düzelt. Port *merkezleri* önceki turda yapı merkezine taşındı
  (`2026-09-10-claude-fdtd-001-port-plane-fix.md`), ancak rung-0b kanıtında
  `ModeSource` / `FluxMonitor` / `FieldMonitor` düzlemleri hâlâ `[0, domain_y,
  domain_z]` boyutundaydı — bütün domain enine kesitini kapsıyor, diğer bus'ın
  gücünü ve alt-taş/kılıf dilimlerini içeri alıyor, linear rezonans kabulünü
  geçersiz kılıyordu.
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Yer: git worktree `worktree-fdtd-001-port-plane-size`. **Cloud yok, Tidy3D
  çağrısı yok, paket kurulmadı, alt-ajan yok, commit/push yok.** Değişen 2 dosya
  ana çalışma kopyasına `??` (commit'siz) olarak kopyalandı; ratification
  Astra'da.
- Sadece `fdtd/mrr/linear_sim.py` + `tests/fdtd/test_linear_sim.py` değişti.
  `fdtd/tidy3d_build/`, cloud/API kodu, `BACKLOG.md`, `BACKLOGLOG.md`,
  `CHANGELOG.md`, `docs/decisions/`, sözleşme dosyaları ve diğer uncommitted iş
  **değiştirilmedi**. Fizik parametresi seçilmedi / uydurulmadı.

## Kök neden

`LinearSimulationTranslator._port_plane` enine düzlem boyutunu domain'den
alıyordu:

```python
size = self.geometry.domain_size_um()
"plane_size_um": [0.0, size[1], size[2]]
```

`domain_size_um()` = geometri + `2*domain_padding_um`. Bu yüzden her kaynak/
monitör "düzlemi" tüm domain'i (her iki bus, halka, substrate/BOX/cladding
dilimleri, padding) kesiyordu. Named bus üzerinden taşınan modal güç izole
edilemedi → fiziksel kabul reddi.

## Düzeltme

`_port_plane` artık enine boyutu **adı geçen bus geometrisinden mekanik olarak**
türetir (fizik sabiti değil; caller'ın verdiği geometri/padding değerleri):

- injection ekseni (`x`): boyut `0.0` — değişmedi.
- transverse (`y`): `bus_waveguide_width_um + 2*domain_padding_um`.
- vertical (`z`): `waveguide_thickness_um + 2*domain_padding_um`.
- düzlem *merkezi*: önceki turdaki gibi named bus'ın `y`/`z` merkezi —
  değişmedi.

`ModeSource`, `FluxMonitor` ve `FieldMonitor` düzlemleri tek yardımcıyı
(`_port_plane`) kullandığı için üçü de aynı kuralı alır.

### Fail-closed doğrulama (yeni `_port_plane_problems`)

`evidence_problems()` → `_port_problems()` içinden çağrılır (geometri iyi
biçimli ve token geçerli ise). Her türetilmiş düzlem için:

- injection ekseni boyutu `0` olmalı; transverse boyutlar sonlu ve `> 0`.
- injection yüzü `x`, `domain_padding_um` sınır marjının dışında kalmalı:
  `|x| <= domain_x/2 - domain_padding_um` (PML/Absorber bu marjda yaşar).
- transverse `y` açıklığı domain kutusunun içinde: `|cy| + sy/2 <= domain_y/2`.
- vertical `z` açıklığı `[0, domain_z]` içinde: `cz - sz/2 >= 0` ve
  `cz + sz/2 <= domain_z`.

İhlal → `MissingLinearEvidenceError` (translate/build_document fail-closed).
Örn. `domain_padding_um > substrate + BOX` ise düzlem `z < 0`'a taşar ve çeviri
reddedilir.

### Önce / sonra (sentetik happy-path bundle, `GEO`)

`bus_waveguide_width_um = 0.45`, `waveguide_thickness_um = 0.3`,
`domain_padding_um = 1.5`; `domain_size_um = [23.0, 18.3, 12.3]`.

| alan | önce | sonra |
| --- | --- | --- |
| `plane_size_um` (y) | `18.3` (tüm domain) | `0.45 + 2*1.5 = 3.45` |
| `plane_size_um` (z) | `12.3` (tüm domain) | `0.3 + 2*1.5 = 3.3` |
| `plane_size_um` (x) | `0.0` | `0.0` |
| `plane_center_um` | değişmedi | değişmedi |

Digest etkisi: `plane_size_um` plan belgesinde; `to_structures()` ve merkezler
değişmediği için yalnız kaynak/monitör düzlem boyutları farklı — happy-path
digest'i bu düzeltmeyle değişir (beklenen; eski rung planları yeniden
üretilecek).

## Regresyon testleri (`tests/fdtd/test_linear_sim.py::PortPlaneSizeTest`, 9 test)

- `test_every_port_plane_size_is_derived_from_bus_geometry` — her port için
  `sx == 0`, `sy == bus_w + 2*pad`, `sz == wg_thick + 2*pad`.
- `test_mode_source_flux_and_field_monitors_all_use_the_same_rule` — üç tür de
  aynı `(0, sy, sz)` boyutunu alır.
- `test_plane_no_longer_spans_the_whole_domain_cross_section` — `sy < domain_y`,
  `sz < domain_z` (cloud rung-0b hatasının doğrudan regresyonu).
- `test_plane_size_tracks_only_the_geometry_it_is_derived_from` — `substrate`
  değişimi boyutu etkilemez; `bus_waveguide_width_um` +0.1 → `sy` +0.1;
  `domain_padding_um` +0.25 → `sy` ve `sz` +0.5.
- `test_derived_plane_stays_inside_the_domain`.
- `test_plane_leaving_the_domain_fails_closed` — `domain_padding_um = 8.0`
  (> substrate+BOX) → `MissingLinearEvidenceError`, "leaves the domain".
- `test_validator_rejects_a_plane_whose_face_is_in_the_boundary_margin` —
  `_port_plane_problems` guard'ının birim testi.
- `test_derived_plane_size_is_deterministic`.
- `test_dry_run_still_passes_with_bus_sized_planes`.

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython. Stdlib dışı bağımlılık yok, ağ/cloud yok. Komutlar
worktree kökünden (`.claude/worktrees/fdtd-001-port-plane-size`) çalıştırıldı;
değişen 2 dosya ana kopyaya bit-aynı kopyalandı.

```
$ python -m unittest tests.fdtd.test_linear_sim -b
Ran 68 tests in 0.055s      # 59 mevcut + 9 yeni
OK

$ python -m unittest discover -t . -s . -p "test_*.py" -b
Ran 261 tests in 68.1s      # tam yerel suite, regresyon yok
OK
```

## Açık riskler / sınırlar

- Enine düzlem, dış tarafta tam olarak domain kenarına kadar uzanır (drop bus
  için `cy + sy/2 == domain_y/2`); yani transverse PML marjını dışarıdan teğet
  geçer. Bu, verilen türetme formülünün (`+ 2*domain_padding_um`) doğrudan
  sonucudur ve talimatla uyumludur. PML µm kalınlığı grid çözünürlüğüne bağlı
  olduğundan (hücre sayısı, bu katmanda yok) transverse "PML içi" kontrolü
  domain sınırına göre yapılır; injection ekseninde (fiziksel olarak önemli
  yön) marj kontrolü tamdır.
- `plane_center_um` mantığı önceki turdan değişmedi.
- Mevcut `manifests/fdtd/mrr-linear-001/*.plan.json` eski tam-domain düzlem
  boyutlarıyla üretilmiş; yeniden üretimi Astra'ya bırakıldı (bu görevde
  plan/manifest üretilmedi).

## Sıradaki tek adım

Astra: ana çalışma kopyasındaki `??` iki dosyayı incele; `python -m unittest
discover -t . -s . -p "test_*.py" -b` (261/261) çıktısını kaydet; port düzlemi
boyut türetmesini FDTD-001 linear yakınsama kapısı için onayla; onaylanırsa
rung-0/rung-0b planını yeni port düzlem boyutlarıyla yeniden üret ve cloud
fiziksel kabulünü tekrarla.
