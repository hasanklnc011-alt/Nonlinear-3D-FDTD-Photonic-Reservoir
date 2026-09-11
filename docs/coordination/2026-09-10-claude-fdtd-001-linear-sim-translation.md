# 2026-09-10 — [FDTD-001] Claude — Yerel linear Tidy3D `Simulation` çeviri katmanı

## Sahiplik

- Görev: FDTD-001 hazırlığı — "tam kanıtlı MRR study girdisini yerel, cloud'suz,
  fizik-icat-etmeyen bir **linear** Tidy3D `Simulation` planına çeviren katman".
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Bir git worktree'sinde (`worktree-fdtd-001-linear-sim`) yapıldı; **commit yok,
  push yok, alt-ajan yok, paket kurulmadı, Tidy3D/cloud çağrısı yok**. Yeni ve
  değişen dosyalar ana çalışma kopyasına `??` (commit'siz) olarak kopyalandı.
- [`fdtd.provenance`](../../fdtd/provenance/README.md) ve
  [`fdtd.mrr`](../../fdtd/mrr/README.md) (geometry/config/study) iskeletlerinin
  **üzerine** kuruludur; o modüller **değiştirilmedi** (yalnız `fdtd/mrr/__init__.py`
  export listesi ve `fdtd/mrr/README.md` genişletildi).

## Ne yapar

`LinearSimulationTranslator`, çağıranın verdiği tam kanıtlı girdiyi tek bir
deterministik, hash'lenebilir sözlüğe (`LinearSimulationPlan`) çevirir. Bu sözlük
**linear** çözüm için `tidy3d.Simulation(...)` kwarg'larıyla 1:1 eşleşir:
`domain`, `grid_spec` (AutoGrid), `run_time_s`, `field_decay_shutoff`,
`boundary_spec`, `symmetry`, `background_medium`, `structures` (her biri somut
`Medium` + `permittivity`/`conductivity`), `sources` (ModeSource + GaussianPulse),
`monitors` (Flux/Field), `inputs` (girdi kopyası) ve `provenance`
(geometry_hash + config_hash + malzeme kanıt digest'leri + `linear_only=True` +
cloud bayrakları hep `False`/boş).

Girdi bir "bundle" JSON'u ya da doğrudan dataclass'larla verilir:

| Blok | İçerik | Kaynak |
| --- | --- | --- |
| `geometry` | `RingResonatorGeometry` alanları (µm) | çağıran (Astra) |
| `config` | `SimulationConfig` (dalga bandı, sınır **tür adları**, simetri, kaynak/monitör **adları**) | çağıran |
| `materials` | `LinearMediumValue[]` — her medyum etiketi için **somut** `relative_permittivity` (>0) + `conductivity` (>=0) + `evidence_digest` (sha256) + `evidence_reference` + `wavelength_range_um` | çağıran (harici kanıt) |
| `background_medium_label` | arka plan medyumu (geometri etiketlerinden biri) | çağıran |
| `excitation` | `center_wavelength_um`, `bandwidth_wavelength_um`, `num_freqs` | çağıran |
| `discretization` | `grid_min_steps_per_wavelength`, `grid_wavelength_um`, `run_time_seconds`, `field_decay_shutoff`, `boundary_num_layers` | çağıran (Astra yakınsama merdiveni rung'ı) |

## Sınır (uygulandı, testlerle aynalandı — `tests/fdtd/test_linear_sim.py`, 51 test)

- **Yalnız linear.** Hiçbir yerde `KerrNonlinearity` / `TwoPhotonAbsorption` /
  `chi(3)` / serbest taşıyıcı terimi üretilmez veya kabul edilmez. `nonlinear`
  (ya da `kerr` / `tpa` / `chi3` / `free_carrier`) anahtarı taşıyan bundle
  `TranslationError` ile reddedilir. `dry_run`, plana sonradan enjekte edilen
  nonlinear içeriği (`linear_only` kontrolü) yakalar.
- **Hiçbir fiziksel değer icat edilmez.** Her linear `permittivity`/`conductivity`
  ve her geometri boyutu girdiden gelmek zorundadır; eksik/biçimsizse
  `MissingLinearEvidenceError` (fail-closed). Her medyum değeri harici bir
  dosyanın SHA-256 digest'i + referans + geçerlilik bandı taşır.
- **Hiçbir fiziksel sabit hard-code edilmez.** Plan çağıranın birim sisteminde
  kalır (µm, s, bağıl geçirgenlik, S/m). `c` (299792458) veya `eps0` (8.854e-12)
  plan çıktısında **yok** (test ile doğrulandı); Hz'e çevrim Tidy3D'nin kendi
  `C_0`'ı ile, gerçek nesneyi kuran kod tarafında yapılır.
- **Mesh/zaman/PML seçilmez.** Ayrıklaştırma çağıranın girdisidir; katman yalnız
  **birleştirir** ve eksikse fail-closed olur — böylece çıktı yarım-form değil,
  kurulabilir bir `Simulation` planıdır. `dry_run` yine de her değeri yeniden
  kontrol eder (savunma derinliği).
- **Cloud yok.** `linear_sim.py`, `linear_dryrun.py`, `__main__.py` hiçbir ağ /
  Tidy3D modülü import etmez (regex kaynak taraması). `import` sonrası
  `tidy3d not in sys.modules`. Planda task id yok, FlexCredit yok, cloud
  bayrakları `False`.
- Sözleşme dosyaları (`AGENTS.md`, `CLAUDE.md`, `const.md`), `BACKLOG.md`,
  `BACKLOGLOG.md`, `CHANGELOG.md`, benchmark protokolü, `reports/` **değiştirilmedi**.

## Neden

`const.md` bilimsel sözleşmesi: ilk ücretli çözüm **doğrusal** rezonans/mesh/
zaman/PML yakınsamasıdır (`reports/FDTD-001-mrr-feasibility.md`, Astra kararı).
`fdtd.mrr` study-builder geometri/config hash'i + eksik-fizik kanıtında
fail-closed manifest üretiyordu ama girdiyi **çalıştırılabilir bir linear
`Simulation` tanımına** çevirmiyordu. Bu katman o boşluğu doldurur: Claude'un
hazırlamasına izin verilen kısmı (deterministik çeviri + serileştirme + hash +
yerel dry-run) üretir, gerçek Tidy3D nesnesinin kurulmasını, maliyet tahminini,
yüklemeyi ve nonlinear kabulü Astra/Codex'e bırakır.

## Teslim edilenler (ana çalışma kopyasına kopyalandı, commit'siz)

```
fdtd/mrr/linear_sim.py       # LinearSimulationTranslator + input dataclass'ları + LinearSimulationPlan
fdtd/mrr/linear_dryrun.py    # dry_run(): 13 kontrollü, deterministik, fail-closed yerel doğrulayıcı
fdtd/mrr/__main__.py         # python -m fdtd.mrr plan|dryrun  (cloud'suz CLI)
fdtd/mrr/__init__.py         # (değişti) yeni sembollerin export'u
fdtd/mrr/README.md           # (değişti) linear çeviri katmanı bölümü
tests/fdtd/test_linear_sim.py   # 51 test
docs/coordination/2026-09-10-claude-fdtd-001-linear-sim-translation.md   # bu dosya
```

### `dry_run` kontrol listesi (sabit sıra)

`schema`, `linear_only`, `no_cloud`, `domain`, `structures_fit`, `media`,
`wavelength_consistency`, `grid_and_time`, `boundaries`, `symmetry`, `sources`,
`monitors`, `provenance`.

Yakalanan tutarsızlıklar: eksik/biçimsiz medyum digest'i; `permittivity <= 0`;
excitation bandı (`center ± bandwidth/2`) config bandının veya herhangi bir
medyum geçerlilik bandının dışında; yapı domain'e sığmıyor (bus uzunluğu >
domain-x, dikey yığın > domain-z, enine genişlik > domain-y); bilinmeyen sınır
türü; PML/absorber için `num_layers < 1`; token biçimi bozuk veya var olmayan
yapıya işaret ediyor; plana enjekte edilmiş nonlinear/cloud içeriği.

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14, NumPy 2.4.6. Stdlib dışı bağımlılık yok, ağ/cloud yok.

```
$ python -m unittest tests.fdtd.test_linear_sim -b
Ran 51 tests in 0.045s
OK

$ python -m unittest discover -s tests/fdtd -t . -b
Ran 133 tests in 0.163s      # 82 mevcut (provenance+mrr) + 51 yeni
OK

$ python -m unittest discover -s tests -t . -b
Ran 215 tests in 20.511s     # 164 mevcut + 51 yeni; regresyon yok
OK
```

Elle uçtan uca duman testi — sentetik placeholder kanıtla üretilmiş bundle
(hiçbir gerçek silisyum sabiti yok; dalga bandı bilinçli olarak ~2 µm sentetik):

```
$ python -m fdtd.mrr plan --input <bundle.json> --out plan.json
wrote plan.json
plan_digest 149924ae4b6ac14151204a62db480d5977a9801fffaed2e5996f53acaad6f49f

$ python -m fdtd.mrr dryrun --plan plan.json ; echo exit=$?
[PASS] schema: schema is fdtd-mrr-linear-simulation-plan/1
[PASS] linear_only: no nonlinear medium / term / marker present
[PASS] no_cloud: no task id, cost, or cloud action recorded
[PASS] domain: domain size and center are well formed
[PASS] structures_fit: 6 structures fit inside the domain
[PASS] media: 7 linear media fully specified and evidenced
[PASS] wavelength_consistency: excitation band inside config and every medium window
[PASS] grid_and_time: grid, run time and shutoff are set
[PASS] boundaries: all three axes carry a known boundary kind
[PASS] symmetry: symmetry = [0, 0, 0]
[PASS] sources: 1 sources well formed
[PASS] monitors: 2 monitors well formed
[PASS] provenance: study id, geometry hash and config hash recorded

LINEAR PLAN DRY RUN OK (13 checks)
exit=0
```

Eksik `discretization.run_time_seconds` verilince: `plan` çıkışı `exit=2`
(`cannot translate bundle: ... run_time_seconds must be a finite number > 0`),
`dryrun --input` çıkışı `exit=2`.

## Açık riskler / sınırlar (Astra kararı)

- **`DiscretizationSpec` + `ExcitationSpec` çağıran girdisi olarak zorunlu
  kılındı.** Bu, "Claude mesh seçmez" kuralını çiğnemez (seçim yok, yalnız
  reddetme), ama bu alanların **değerleri** hâlâ Astra'nın yakınsama
  merdiveninden gelmelidir. Bir rung = bir bundle → bir plan → bir digest.
- **`structures` primitifleri tam Tidy3D `Structure` listesi değildir.** Halka
  `{"kind": "ring", outer/inner radius, thickness}` olarak kalır; Tidy3D'de
  `Cylinder` farkı veya `ClipOperation` ile kurulur. Bus/slab → `Box`. Gerçek
  şekil kurulumu Astra/Codex tidy3d tarafında.
- **Kaynak/monitör düzlemi domain enine kesitine eşit alınır** (normal port
  x'inde, merkez domain merkezinde). ModeSource için Astra düzlemi daraltıp
  port'u domain kenarından içeri çekebilir; uydurulmuş inset yok.
- **Dispersif malzeme kapsam dışı.** Yalnız `non_dispersive` (`Medium(eps_r,
  sigma)`). PoleResidue/Sellmeier fit'i ve n,k→(eps,sigma) çevrimi (frekans/`c`
  gerektirir) Astra kararı.
- **`SimulationConfig`'te config digest'i için hâlâ ayrı alan yok**; plan
  `provenance.config_hash` içinde taşır (önceki handoff'taki öneri hâlâ açık).
- **Örnek/gerçek plan üretilmedi**; `manifests/` altında dizin seçilmedi (Astra).
- `BACKLOG.md` / `BACKLOGLOG.md` / `CHANGELOG.md` bu oturumda **değiştirilmedi**.
  FDTD-001 maddesinin "Değişen dosyalar" + "Sıradaki adım" güncellemesi ve
  CHANGELOG kaydı Astra'ya bırakıldı.

## Sıradaki tek adım

Astra: `python -m unittest discover -s tests -t . -b` (215/215) ve yukarıdaki
`plan` + `dryrun` çıktısını kaydet; linear çeviri katmanının girdi sözleşmesini
(`materials` somut linear değer + kanıt digest'i, `discretization` +
`excitation` çağıran girdisi, `background_medium_label`) FDTD-001 linear
yakınsama kapısının parçası olarak onayla veya revizyon iste; onaylanırsa
kaynaklı silisyum linear malzeme değerlerini (harici dosya + `python -m
fdtd.provenance digest` ile digest) ve ilk mesh/zaman/PML rung setini sağlayıp
ilk gerçek MRR linear `Simulation` planını (`plan_digest`) üret.
