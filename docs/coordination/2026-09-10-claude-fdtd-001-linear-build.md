# 2026-09-10 — [FDTD-001] Claude — Yerel linear Tidy3D `Simulation` **kurucu** katman

## Sahiplik

- Görev: doğrulanmış `LinearSimulationPlan`'dan gerçek, **yerel-only** bir
  `tidy3d.Simulation` nesnesi kuran ayrı modül; nesneyi serialize edip SHA-256
  hash üret. `tidy3d.web` / upload / estimate_cost / run / start / download / ağ
  yok. Fiziksel malzeme veya geometri parametresi seçilmez; sentetik test
  girdileriyle doğrulanır.
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Bir git worktree'sinde (`worktree-fdtd-001-linear-build`) yapıldı; **commit
  yok, push yok, alt-ajan yok, paket kurulmadı, Tidy3D cloud çağrısı yok**. Yeni
  dosyalar ana çalışma kopyasına commit'siz (`??`) kopyalandı.
- Mevcut uncommitted işlere (`fdtd/mrr/*`, `fdtd/provenance/*`,
  `tests/fdtd/test_linear_sim.py`, `tests/fdtd/test_mrr.py`, ...) **dokunulmadı**.
  `fdtd/mrr/__init__.py` ve `fdtd/__init__.py` **değiştirilmedi**.
- `BACKLOG.md`, `BACKLOGLOG.md`, `CHANGELOG.md`, `docs/decisions/`, benchmark
  protokolü, `const.md`, `AGENTS.md`, `CLAUDE.md` **değiştirilmedi**.

## Neden ayrı paket (`fdtd/tidy3d_build/`)

`fdtd/mrr` tasarımı saf planlama katmanıdır: `tests/fdtd/test_mrr.py`
(`NoCloudTest.test_no_network_or_tidy3d_imports_in_source`) `fdtd/mrr/*.py`
altındaki **her** dosyanın `import tidy3d` içermemesini şart koşar ve
`tests/fdtd/test_linear_sim.py` aynı sınırı `linear_sim.py` / `linear_dryrun.py`
/ `__main__.py` için tekrar doğrular. Bu görevdeki modül tanımı gereği `tidy3d`
import eder, dolayısıyla `fdtd/mrr` altına konamaz (ve o test dosyaları
uncommitted olduğu için değiştirilemez). Bu yüzden gerçekleştirme adımı kardeş
bir pakete taşındı: **`fdtd/mrr` planlar, `fdtd/tidy3d_build` kurar.**

## Ne yapar

`fdtd/tidy3d_build/linear_build.py`:

| Fonksiyon | Davranış |
| --- | --- |
| `build_simulation(plan_or_doc, *, run_dry_run=True)` | Plan belgesini (`LinearSimulationPlan`, `.document` dict veya `to_document()`) fail-closed geçitten geçirir, sonra `tidy3d`'yi **lazy** import edip somut `tidy3d.Simulation` döndürür. |
| `serialize_simulation(sim)` | Tidy3D'nin kendi serileştirmesi → `json.loads` → `sort_keys=True, separators=(",",":")` kanonik JSON string. |
| `simulation_digest(sim)` | Kanonik JSON'un SHA-256 hex digest'i. |
| `build(plan_or_doc, ...)` | `BuiltLinearSimulation(simulation, canonical_json, digest, tidy3d_version)` döndürür. |

Token → Tidy3D nesnesi eşlemesi (hepsi düz çeviri, hiçbir değer seçilmez):

| Plan token | Tidy3D nesnesi |
| --- | --- |
| `background_medium` / yapı `medium` (`model="non_dispersive"`) | `td.Medium(permittivity=eps_r, conductivity=sigma)` |
| yapı `kind="ring"` | `td.Structure(td.ClipOperation("difference", td.Cylinder(outer), td.Cylinder(inner)))` |
| yapı `kind="waveguide"` | `td.Structure(td.Box(size=(length,width,thickness)))` |
| yapı `kind="slab"` | `td.Structure(td.Box(size=(inf, inf, z_max-z_min)))`, merkez domain merkezinden + z sınırlarından |
| `boundary_spec` (`PML`/`Absorber`/`Periodic`/`PECBoundary`/`PMCBoundary`) | `td.BoundarySpec` + `td.Boundary.pml/absorber/periodic/pec/pmc` |
| `sources` (`ModeSource` + `GaussianPulse` token'ı) | `td.ModeSource(source_time=td.GaussianPulse(freq0, fwidth), mode_spec=td.ModeSpec(), direction=...)` |
| `monitors` (`flux` / `field`) | `td.FluxMonitor` / `td.FieldMonitor`, `freqs` = banttaki `num_freqs` noktalı lineer tarama |
| `grid_spec` (`AutoGrid`) | `td.GridSpec.auto(min_steps_per_wvl=, wavelength=)` |
| `domain`, `run_time_s`, `field_decay_shutoff`, `symmetry` | `td.Simulation(center=, size=, run_time=, shutoff=, symmetry=)` |

### Hesaplanan tek şeyler (mekanik, fizik seçimi değil)

- Dalga boyu → frekans: `freq0 = C_0 / center`, `fwidth = C_0/λ_lo − C_0/λ_hi`,
  monitör frekansları `num_freqs` noktalı lineer tarama — **Tidy3D'nin kendi
  `td.C_0`'ı** ile (plan bunu bilinçli olarak erteliyor; hiçbir `c` hard-code
  edilmez).
- Slab merkezi: `domain.center_um`'un x/y'si + slab `z_min/z_max` ortası.
- Yapı sırası: slab'lar (plan sırasında) önce, ring/bus sonra. Tidy3D çakışan
  yapılarda "son kazanır" uyguladığı ve plan'ın düzlemsel yığını (substrate /
  buried oxide / cladding) dalga kılavuzu ile aynı `z` bandını kapladığı için
  gereklidir; aynı yapıların sıralaması, hiçbir geometri değerinin değişimi
  değil.

## Sınır (uygulandı, testlerle aynalandı — `tests/fdtd/test_linear_build.py`, 29 test)

- **Cloud yok.** Modül `tidy3d`'yi yalnız `_td()` içinde lazy import eder;
  `import fdtd.tidy3d_build.linear_build` → `tidy3d not in sys.modules` (alt-süreç
  testi). Kaynakta `requests/httpx/urllib/http/socket/ssl/boto3/paramiko/
  websocket/aiohttp/tidy3d.web` importu yok (regex taraması). `build_simulation`
  kurulum sırasında `tidy3d.web`'in import edilmediğini iddia eder; edilmişse
  `LinearBuildError`.
- **Linear only.** `linearity != "linear"`, `provenance.linear_only != True`,
  `provenance.nonlinear` set, ya da herhangi bir nonlinear işaret
  (kerr/tpa/chi3/free_carrier/n2 — `run_dry_run=False` olsa bile taranır) →
  hiçbir Tidy3D nesnesi kurulmadan `LinearBuildError`.
- **Fizik/geometri icadı yok.** Her permittivity, conductivity, uzunluk,
  yarıçap, dalga boyu, katman sayısı, run time, shutoff plan'dan **birebir**
  okunur. Eksik/biçimsiz medyum, sığmayan yapı, vs. → `LinearBuildError`.
- **Fail closed.** Varsayılan olarak plan `fdtd.mrr.linear_dryrun.dry_run`'dan
  yeniden geçirilir; başarısız kontrol → `LinearBuildError`, hiçbir şey kurulmaz.
- **Serialize + hash deterministik.** İki ayrı `build()` → aynı digest;
  kanonik JSON'un yeniden parse edilmesi (`Simulation.model_validate_json`) →
  aynı digest; herhangi bir malzeme/geometri değeri değişince digest değişir.

## Teslim edilenler (ana çalışma kopyasına kopyalandı, commit'siz)

```
fdtd/tidy3d_build/__init__.py          # public API export'u (lazy; tidy3d import etmez)
fdtd/tidy3d_build/linear_build.py      # build_simulation / serialize_simulation / simulation_digest / build
tests/fdtd/_linear_build_driver.py     # alt-süreç sürücüsü (tidy3d'yi yalnız burada import eder)
tests/fdtd/test_linear_build.py        # 29 test (guard testleri in-process, build testleri alt-süreçte)
docs/coordination/2026-09-10-claude-fdtd-001-linear-build.md   # bu dosya
```

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14.7, tidy3d 2.12.0. Ağ/cloud yok.

```
$ python -m unittest discover -s tests/fdtd -t . -b
Ran 162 tests in 44.6s
OK                              # 133 mevcut (provenance+mrr+linear_sim) + 29 yeni

$ python tests/fdtd/run_tests.py
Ran 162 tests
OK

$ python -m unittest discover -s tests -t . -b
Ran 244 tests in 62.5s
OK                              # 215 mevcut + 29 yeni; regresyon yok
```

Elle uçtan uca (sentetik `SYN_*` bundle — hiçbir gerçek silisyum sabiti yok,
band bilinçli olarak ~2 µm):

```
plan digest        : 149924ae4b6ac14151204a62db480d5977a9801fffaed2e5996f53acaad6f49f
tidy3d version     : 2.12.0
simulation type    : tidy3d.components.simulation.Simulation
simulation digest  : 674fde9865c08da99c2bcb664962ef06e6bf2174191d9ba030aa79eca8bb0fdc
canonical json len : 15528
structures         : ['substrate', 'buried_oxide', 'cladding', 'ring_core', 'bus_through', 'bus_drop']
sources            : [('ModeSource', '+')]
monitors           : [('FluxMonitor', 'flux:bus_through:out', 201), ('FluxMonitor', 'flux:bus_drop:out', 201)]
web imported       : False
```

(digest'ler bu ortamdaki tidy3d 2.12.0 serileştirmesine bağlıdır; farklı tidy3d
sürümü farklı digest verir — `BuiltLinearSimulation.tidy3d_version` bunu taşır.)

## Açık riskler / sınırlar (Astra kararı)

- **`fdtd/__init__.py` docstring'i** hâlâ "Nothing in this package imports
  Tidy3D" diyor. Yeni alt-paket `tidy3d`'yi **lazy** import ettiği için
  "import fdtd → tidy3d import edilmez" hâlâ doğru, ama docstring'in daha güçlü
  ifadesi artık "eager import yok" olarak okunmalı. Dosya bu görevde
  değiştirilmedi (uncommitted, başka iş sahibi). Astra: docstring'i güncelle
  veya sınırı netleştir.
- **Kaynak/monitör düzlemi** plan'dan geldiği gibi domain enine kesitine eşit
  alınır (PML içine girer → Tidy3D uyarısı, hata değil). Astra ModeSource
  düzlemini daraltmak isterse bu plan katmanında yapılmalı; kurucu uydurmaz.
- **Yapı sırası kararı** (slab'lar önce) kurucuda; plan primitifleri sırasız
  kabul edilir. Alternatif: plan `structures` listesini zaten doğru öncelik
  sırasında yayınlasın (linear_sim değişikliği — Astra).
- **Dispersif malzeme kapsam dışı** (`non_dispersive` `Medium` yalnız); plan
  da öyle.
- **Gerçek MRR planı/simülasyonu üretilmedi**; yalnız sentetik. `manifests/`
  altında dizin seçilmedi.
- **Simulation nesnesi diske yazılmadı**; `build()` nesneyi + kanonik JSON'u +
  digest'i döndürür, kalıcılaştırma çağırana bırakıldı.
- `BACKLOG.md` / `BACKLOGLOG.md` / `CHANGELOG.md` / `docs/decisions/` bu oturumda
  **değiştirilmedi** (görev talimatı). FDTD-001 madde güncellemesi ve CHANGELOG
  kaydı Astra'ya bırakıldı.

## Sıradaki tek adım

Astra: `python -m unittest discover -s tests -t . -b` (244/244) ve yukarıdaki
uçtan uca çıktıyı kaydet; `fdtd/tidy3d_build` paket yerleşimini ve kurucu
sözleşmesini (plan → gerçek `tidy3d.Simulation` + kanonik JSON + SHA-256,
yerel-only, fail-closed) onayla veya revizyon iste; onaylanırsa kaynaklı
silisyum linear malzeme değerleri + ilk mesh/zaman/PML rung seti ile gerçek MRR
linear plan'ını üret ve `build()` ile ilk gerçek `simulation_digest`'i kaydet.
