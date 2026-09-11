# 2026-09-10 — [FDTD-001] Claude — Silicon microring (MRR) study-builder scaffold

## Sahiplik

- Görev: FDTD-001 hazırlığı — "yerel, cloud'suz, fiziksel-parametre-icat-etmeyen
  Tidy3D study-builder iskeleti" (3D silisyum microring adayı için).
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Bir git worktree'sinde (`worktree-fdtd-001-mrr-builder`) yapıldı; commit yok.
  Yeni dosyalar ana çalışma kopyasına kopyalanacak (`??`, commit'siz).
- [`fdtd.provenance`](../../fdtd/provenance/README.md) iskeletinin üzerine
  kuruludur; o şema/validator **değiştirilmedi**.

## Sınır (uygulandı, testlerle aynalandı)

- **Fiziksel değer icat edilmedi.** Silisyum `n`/`k`/`n2`/TPA/`chi(3)` hiçbir
  yerde yok. Malzeme ve nonlinear kanıtı çağıran taraf `MaterialSource` /
  `NonlinearModel` kaydı olarak **dışarıdan** verir; bu kayıtlar yalnız
  referans + sürüm + kaynak türü + harici dosyanın **SHA-256 digest**'ini taşır.
  Eksik/biçimsizse builder **fail-closed** (`MissingEvidenceError`).
- **Aday ailesi seçilmedi.** Manifest'te `candidate_family = None` (Astra kararı).
- **Mesh / zaman / PML merdiveni seçilmedi.** `SimulationConfig` hiçbir
  ayrıklaştırma bilgisi tutmaz (`mesh_is_deferred == True`); `build_manifest()`
  üç merdiveni **boş** ve `flex_credit`'i **boş** üretir.
- **Cloud yok.** Hiçbir modül Tidy3D / socket / http / urllib import etmez
  (kaynak taraması testi). Task submit/download/run yok; `task_ids == []`.
- Sözleşme dosyaları (`AGENTS.md`, `CLAUDE.md`, `const.md`), `BACKLOG.md`,
  `BACKLOGLOG.md`, `CHANGELOG.md`, `docs/PROJECT-CHARTER.md`, benchmark protokolü
  **değiştirilmedi**. Paket kurulmadı (saf stdlib + `fdtd.provenance`).
  Commit/push yok, alt-ajan yok, Tidy3D çağrısı yok.

## Neden

`const.md` bilimsel sözleşmesi + `AGENTS.md` kanıt kuralları: ücretli 3D
nonlinear FDTD solve'dan önce geometri hash'i, doğrulanmış malzeme kaynağı/sürümü
ve doğrulanmış nonlinear model **kayıtlı ve doğrulanabilir** olmalı; mesh/zaman
yakınsaması ve FlexCredit maliyet kapısı Astra kararıdır. Bu iskelet, Claude'un
hazırlamasına izin verilen kısımları (parametrik geometri + konfig, deterministik
serileştirme + hash, kanıt kapısı) doldurur ve gerisini Astra için **bilinçli
olarak eksik** bırakır. Astra tek deterministik komutla
(`python -m fdtd.provenance validate`) neyin eksik olduğunu görür.

## Teslim edilenler (ana çalışma kopyasına kopyalanacak, commit'siz)

```
fdtd/mrr/__init__.py
fdtd/mrr/geometry.py     # RingResonatorGeometry: parametrik geometri + canonical doc + SHA-256 digest
fdtd/mrr/config.py       # SimulationConfig: ayrıklaştırma-içermeyen kurulum + SHA-256 digest
fdtd/mrr/study.py        # MicroringStudyBuilder + StudyIdentity + MissingEvidenceError (fail-closed kapı)
fdtd/mrr/README.md
tests/fdtd/test_mrr.py   # 35 test
docs/coordination/2026-09-10-claude-fdtd-001-mrr-study-builder.md   # bu dosya
```

### `RingResonatorGeometry` (`fdtd/mrr/geometry.py`)

SOI microring add/drop filtresinin **geometrik** tanımı (hepsi µm, varsayılan
yok — çağıran verir):

| alan | anlam |
| --- | --- |
| `ring_outer_radius_um`, `waveguide_width_um`, `waveguide_thickness_um` | halka |
| `bus_waveguide_width_um`, `coupling_gap_um`, `bus_length_um` | bus dalgakılavuzu + kuplaj aralığı |
| `cladding_thickness_um`, `box_thickness_um`, `substrate_thickness_um` | dikey yığın |
| `domain_padding_um` | domain dolgusu (mesh değil) |
| `add_drop` | topoloji bayrağı (tek bus / add-drop) |
| `core_medium`, `cladding_medium`, `box_medium`, `substrate_medium` | **medyum etiketleri** (ad, sabit değil) |

- `.validate()` → boyutsal olarak imkânsız / eksik ise `GeometryError`
  (pozitif olmayan boyut, negatif aralık, `waveguide_width >= ring_radius`,
  boş medyum etiketi, sonsuz değer).
- `.to_document()` → `{schema, units, parameters, derived, structures}`;
  `structures` yalnız uzam + medyum **adı** taşır.
- `.digest()` → `canonical_geometry_digest(to_document())` (sıralı anahtar,
  kompakt ayraç → alan/kwarg sırasından bağımsız, değer değişince değişir).

### `SimulationConfig` (`fdtd/mrr/config.py`)

Bilinçli olarak **ayrıklaştırma içermez**: grid yok, adım/periyot yok, PML
katman sayısı yok, run time yok, tolerans yok — hepsi yakınsama merdiveni =
Astra. Tuttukları: `wavelength_range_um` (çağıranın tasarım bandı, malzeme
sabiti değil), `boundary_types` (`x/y/z` → tür **adı**: `pml/absorber/periodic/
pec/pmc`), `symmetry` (`[-1|0|1]×3`), `sources` / `monitors` (**adlar**).
`.validate()` → `ConfigError`. `.digest()` → canonical SHA-256.
`mesh_is_deferred` / `run_time_is_deferred` her zaman `True`.

### `MicroringStudyBuilder` (`fdtd/mrr/study.py`)

Girdi: `StudyIdentity` + doğrulanmış `geometry` + `config` + **çağıranın
verdiği** `MaterialSource` + `NonlinearModel` (+ opsiyonel `evidence_paths`,
`geometry_artifact`).

- `.geometry_digest()`, `.config_digest()` — deterministik.
- `.evidence_problems()` → dışarıdan gereken ve elde olmayan her şeyin listesi:
  `REQUIRED_MATERIAL_FIELDS` (`name`, `dispersion_model`, `source_kind`,
  `reference`, `version`, `retrieved_utc`, `parameter_digest`,
  `wavelength_range_um`), `REQUIRED_NONLINEAR_FIELDS` (`model_type`,
  `source_kind`, `reference`, `version`, `parameter_digest`,
  `applies_to_medium`); `source_kind ∈ SOURCE_KINDS`; digest = 64-hex;
  `nonlinear.applies_to_medium == material.name`;
  `geometry.core_medium == material.name`; geometri/konfig `problems()`.
- `.require_evidence()` → sorun varsa `MissingEvidenceError` (fail-closed).
- `.build_manifest()` → önce `require_evidence()`, sonra `CandidateStudyManifest`:
  - `study_id` / `created_utc` / `tidy3d_version` = identity'den,
  - `candidate_family = None` (Astra),
  - `material` / `nonlinear` = verilen kayıtlar aynen,
  - `geometry = GeometryProvenance(geometry_hash=<geometry digest>, "sha256", …)`,
  - `ladders = [ConvergenceLadder("mesh"), (…"time"), (…"pml")]` — **boş** (Astra),
  - `flex_credit = FlexCreditBudget()` — **boş** (Astra estimate + `approved_ceiling`),
  - `task_ids = []`, `evidence_paths` = verilen liste,
  - `notes` = `geometry_digest` + `config_digest` + "INCOMPLETE BY DESIGN …".

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14.7. Stdlib dışı bağımlılık yok, ağ/cloud yok.

```
$ python -m unittest tests.fdtd.test_mrr -v
...
Ran 35 tests in 0.009s
OK

$ python -m unittest discover -s tests/fdtd -t .
Ran 82 tests in 0.116s      # 47 mevcut provenance + 35 yeni mrr
OK

$ python -m unittest discover -s tests -t .
Ran 164 tests in 18.932s    # 129 mevcut + 35 yeni; regresyon yok
OK
```

Test kapsamı (`tests/fdtd/test_mrr.py`, 35):

- `GeometryDeterminismTest` (7): digest tekrarlanabilir + hex64; alan/kwarg
  sırasından bağımsız; herhangi bir değer değişimi digest'i değiştirir;
  `to_structures()` deterministik + `add_drop` topolojisine duyarlı; doküman
  şekli; `validate()` imkânsız geometriyi reddeder; ok ise `self` döner.
- `ConfigDeterminismTest` (5): digest tekrarlanabilir; `boundary_types` anahtar
  sırası önemsiz; her değer değişimi digest'i değiştirir; doküman
  "deferred-to-convergence-ladders" der; `validate()` bozuk konfigi reddeder.
- `RequiredEvidenceFailClosedTest` (9): boş `MaterialSource()` / `NonlinearModel()`
  → `MissingEvidenceError` (alan alan raporlu); sha256 olmayan digest reddi;
  sözlük dışı `source_kind` reddi; `geometry.core_medium` ≠ `material.name` reddi;
  `nonlinear.applies_to_medium` ≠ `material.name` reddi; bozuk geometri/konfig
  `evidence_problems()`'e taşınır; tam kanıt → kapı geçer.
- `ManifestShapeTest` (11): schema/identity; `candidate_family is None`;
  merdivenler boş + `tolerance_rel None`; `flex_credit == FlexCreditBudget()`;
  `task_ids == []`; `geometry.geometry_hash == geometry_digest()`; kanıt aynen
  taşınır; notes her iki digest'i + "INCOMPLETE BY DESIGN" içerir; JSON
  round-trip; `validate_study(m).ok is False` ve eksik kontroller
  {`candidate_family`, `convergence.*`, `flex_credit`, `identity`} içerir;
  `tidy3d_version` verilirse manifest'e akar; `evidence_paths` geçişi.
- `NoCloudTest` (3): kaynakta ağ/Tidy3D import'u yok (regex taraması);
  `import fdtd.mrr` sonrası `tidy3d not in sys.modules`; kurulan manifest'te
  cloud artefaktı (task id / actual cost / rung) yok.

Elle duman testi — builder → `build_manifest()` → CLI:

```
$ python -m fdtd.provenance validate --manifest <mrr study.json> ; echo exit=$?
[PASS] schema
[FAIL] identity: manifest.tidy3d_version is missing
[FAIL] candidate_family: candidate_family is not set
[PASS] material.source: Si / PoleResidue from tidy3d_material_library
[PASS] nonlinear.model: KerrNonlinearity on Si from literature
[PASS] geometry.hash: geometry hashed (915c37f7841c0c59...)
[FAIL] convergence.mesh: tolerance_rel None must be a positive number; needs >= 2 rungs, has 0
[FAIL] convergence.time: ...
[FAIL] convergence.pml: ...
[FAIL] flex_credit: estimated_total None must be a positive number; estimate_source is missing; approved_ceiling None ...
[INFO] task_ids: no task ids yet (nothing submitted) - expected pre-solve
[PASS] evidence: 1 evidence file(s) present

STUDY PROVENANCE INCOMPLETE (6 failing: identity, candidate_family, convergence.mesh, convergence.time, convergence.pml, flex_credit)
exit=1
```

Not: yukarıdaki manifest sentetik placeholder kanıtla (harici dosya digest'i)
üretildi; hiçbir gerçek silisyum sabiti kullanılmadı.

## Açık riskler / sınırlar

- **Şema alan seti / kontrol listesi hâlâ Astra onayına tabi** (bkz.
  `2026-09-10-claude-fdtd-001-provenance-scaffold.md`). Bu builder o şemayı
  kullanır; şema değişirse `study.py`'nin `build_manifest()` eşlemesi güncellenir.
- **`SimulationConfig` digest'i manifest'e sadece `notes` içinde metin olarak
  giriyor.** `CandidateStudyManifest`'te config digest'i için ayrı bir alan yok;
  şemaya `config_digest` alanı eklemek Astra kararı (öneri). Şu an builder API'si
  (`config_digest()`) ve bu handoff üzerinden izlenebilir.
- **Geometri primitifleri tam bir Tidy3D `Structure` listesi değildir** —
  uzam + medyum etiketi taşıyan sadeleştirilmiş tanımdır; digest amaçlı yeterli,
  ama gerçek simülasyon kurulumunu Astra/Codex Tidy3D tarafında üretir.
- **`domain_padding_um` mesh değil ama PML kalınlığına yakın bir tasarım
  seçimidir**; sınır katman sayısı yine `pml` merdiveninde kalır. İkisi
  karışırsa Astra netleştirmeli.
- **Örnek/gerçek manifest oluşturulmadı** ve `manifests/` altında dizin
  seçilmedi (Astra'nın dizin/sözleşme kararı).
- `BACKLOG.md` / `BACKLOGLOG.md` / `CHANGELOG.md` bu oturumda **değiştirilmedi**
  (önceki FDTD-001 oturumu izi). FDTD-001 maddesinin "Değişen dosyalar" +
  "Sıradaki adım" güncellemesi ve CHANGELOG kaydı Astra'ya bırakıldı.

## Sıradaki tek adım

Astra: `python -m unittest discover -s tests -t .` (164/164) ve yukarıdaki
`validate` çıktısını kaydet; `fdtd.mrr` geometri/konfig alan setini FDTD-001
fizibilite/maliyet kapısının parçası olarak onayla veya revizyon iste;
onaylanırsa MRR aday ailesi kararını, kaynaklı silisyum malzeme + Kerr/TPA
nonlinear kanıtını (harici dosya + digest), mesh/zaman/PML merdiven hedeflerini
ve `approved_ceiling`'i sağlayıp ilk gerçek MRR study manifestini üret.
