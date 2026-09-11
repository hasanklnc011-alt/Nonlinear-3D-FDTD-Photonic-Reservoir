# 2026-09-10 — [FDTD-001] Claude — Candidate-study provenance validation scaffold

## Sahiplik

- Görev: FDTD-001 backlog maddesinin "Claude yerel config/provenance validator
  iskeletini uygular" adımı. Onaylanan kapsam: yalnız bağımlılık-hafif yerel
  şema + fail-closed doğrulayıcı + odaklı yerel testler + bu handoff.
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Sınır (uygulandı):
  - aday ailesi **seçilmedi** (`candidate_family` her yerde `None`/örnek dışı);
  - hiçbir fiziksel malzeme/nonlinear parametre değeri icat edilmedi — şema
    sadece harici dosya SHA-256 digest'i + yerel `evidence_paths` tutar;
  - Tidy3D çağrısı yok, cloud task submit/download yok, FDTD çözümü yok;
  - benchmark sabitleri / sözleşmeleri / `BACKLOG.md` / `BACKLOGLOG.md` /
    `const.md` / `AGENTS.md` / `CLAUDE.md` / `docs/PROJECT-CHARTER.md`
    **değiştirilmedi**;
  - paket kurulmadı (yalnız Python stdlib), commit/push yok, alt-ajan yok.
- İş bir git worktree'sinde yapıldı; yeni dosyalar ana çalışma kopyasına
  kopyalandı (commit'siz, `??`).

## Neden

`const.md` + `docs/PROJECT-CHARTER.md` başarı kapıları 2 ve 3: ücretli solve
öncesi maliyet/kaynak fizibilitesi ve mesh/zaman/PML + nonlinear yakınsaması
**kanıtlı** olmalı; `AGENTS.md` kanıt kuralları task id, sürüm, geometri/malzeme
hash'i, mesh, run time ve tahmini/gerçek FlexCredit kaydını zorunlu kılar. Bu
iskelet o kaydı tipli bir şemaya bağlar ve eksik/biçimsiz/tutarsızsa **fail
closed** eder — böylece Astra bir aday çalışmasını "kanıt tam" diye
işaretlemeden önce tek deterministik komutla kontrol edebilir.

## Teslim edilenler (ana çalışma kopyasında, commit'siz)

```
fdtd/__init__.py
fdtd/provenance/__init__.py
fdtd/provenance/schema.py       # tipli dataclass şeması + hash yardımcıları + JSON round-trip
fdtd/provenance/validate.py     # fail-closed doğrulayıcı, sabit sıralı Check listesi
fdtd/provenance/cli.py          # python -m fdtd.provenance {template,validate,digest}
fdtd/provenance/__main__.py
fdtd/provenance/README.md
tests/fdtd/__init__.py
tests/fdtd/_fixtures.py         # sentetik (fiziksel olmayan) tam manifest fixture'ı
tests/fdtd/test_schema.py       # 19 test
tests/fdtd/test_validate.py     # 28 test
tests/fdtd/run_tests.py
docs/coordination/2026-09-10-claude-fdtd-001-provenance-scaffold.md   # bu dosya
```

Not: `tests/__init__.py` ana kopyada zaten var; worktree'de discovery için
oluşturuldu ama geri kopyalanmadı.

### Şema (`fdtd/provenance/schema.py`)

`CandidateStudyManifest` (schema id `fdtd-candidate-study-provenance/1`), alt
kayıtları:

| kayıt | alanlar (hepsi opsiyonel/`None` = eksik) |
| --- | --- |
| kimlik | `study_id`, `created_utc`, `candidate_family` (**Astra doldurur**), `tidy3d_version`, `notes` |
| `MaterialSource` | `name`, `dispersion_model` (yalnız ad), `source_kind` ∈ `SOURCE_KINDS`, `reference`, `version`, `retrieved_utc`, `parameter_digest` (harici dosyanın sha256'sı), `wavelength_range_um` `[lo, hi]` |
| `NonlinearModel` | `model_type` (yalnız ad), `source_kind`, `reference`, `version`, `parameter_digest`, `applies_to_medium` (= `material.name`), `notes` |
| `GeometryProvenance` | `geometry_hash` (sha256), `hash_algorithm`, `source_artifact`, `units`, `description` |
| `ConvergenceLadder` × `mesh`/`time`/`pml` | `dimension`, `tolerance_rel`, `rungs[]` |
| `ConvergenceRung` | `grid_cells_per_wavelength` \| `steps_per_period` \| `pml_layers`, `run_time_ps`, `field_decay_shutoff`, `observable`, `observable_value`, `task_id`, `flex_credit_estimated`, `flex_credit_actual` |
| `FlexCreditBudget` | `estimated_total`, `actual_total`, `estimate_source`, `estimate_task_ids[]`, `approved_ceiling` (**Astra belirler**) |
| üst düzey | `task_ids[]` (çalışmanın dayandığı tüm Tidy3D id'leri), `evidence_paths[]` (digest'leri destekleyen yerel dosyalar) |

Fiziksel sayılar şemaya hiç girmez. `ConvergenceLadder.converged()` =
`tolerance_rel > 0` **ve** rafinman parametresi kesin artan **ve** son iki
basamak arası bağıl gözlem değişimi ≤ `tolerance_rel`. Yardımcılar:
`sha256_bytes/text/file`, `canonical_geometry_digest` (anahtar sırası
duyarsız), `looks_like_sha256`, `blank_manifest`.

### Doğrulayıcı (`fdtd/provenance/validate.py`)

`validate_study(manifest) -> ValidationReport`. 12 kontrol, sabit sırada:
`schema`, `identity`, `candidate_family`, `material.source`, `nonlinear.model`,
`geometry.hash`, `convergence.mesh`, `convergence.time`, `convergence.pml`,
`flex_credit`, `task_ids`, `evidence`. Beklenmeyen ladder boyutu →
`convergence.extra` FAIL.

Fail-closed davranış (`ok = (FAIL sayısı == 0)`; `require_complete()` aksi halde
`StudyProvenanceIncomplete` fırlatır). Yakalanan tutarsızlıklar:

- zorunlu alan eksik/boş; `source_kind` sözlük dışı; digest 64-hex değil;
- `nonlinear.applies_to_medium` ≠ `material.name`;
- ladder eksik (boyut yok), < 2 basamak, rafinman monoton değil, veya
  yakınsamamış (son değişim > tolerans);
- `flex_credit` tahmini/gerçek maliyeti `approved_ceiling` üstünde, veya
  `estimated_total`/`approved_ceiling` eksik/≤ 0;
- bir basamakta `flex_credit_actual` var ama `task_id` yok;
- rung/estimate task id'si `manifest.task_ids` içinde yok (orphan);
- gerçek sonuç kaydı var ama hiç task id listelenmemiş;
- digest kayıtlı ama `evidence_paths` boş; `evidence_paths` girdisi diskte yok.

Rapor deterministik (timestamp yok); `to_dict()` / `format_text()`.

### CLI

```
python -m fdtd.provenance template --out study.json    # boş form (Astra doldurur)
python -m fdtd.provenance validate --manifest study.json [--json]   # exit 0 iff tam
python -m fdtd.provenance digest <dosya>                # bir kanıt dosyasının sha256'sı
```

`template` çıktısı bilinçli olarak doğrulamayı **geçmez** (boş form).

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14.7. Stdlib dışı bağımlılık yok, ağ/cloud yok.

```
$ python -m unittest discover -s tests/fdtd -t . -v
...
Ran 47 tests in 0.144s
OK

$ python tests/fdtd/run_tests.py
Ran 47 tests in 0.129s
OK

# ana çalışma kopyasında tüm depo test ağacı (narma10_np 82 + fdtd 47):
$ python -m unittest discover -s tests -t .
Ran 129 tests in 19.065s
OK
```

Boş şablon doğrulaması (fail-closed kanıtı):

```
$ python -m fdtd.provenance template --out study.json
$ python -m fdtd.provenance validate --manifest study.json ; echo exit=$?
[PASS] schema: schema is fdtd-candidate-study-provenance/1
[FAIL] identity: manifest.study_id is missing; manifest.created_utc is missing; manifest.tidy3d_version is missing
[FAIL] candidate_family: candidate_family is not set
[FAIL] material.source: material.name is missing; ... ; material.source_kind is missing
[FAIL] nonlinear.model: nonlinear.model_type is missing; ...
[FAIL] geometry.hash: geometry.geometry_hash is missing; geometry.source_artifact is missing; geometry.units is missing
[FAIL] convergence.mesh: tolerance_rel None must be a positive number; rung 0: observable / observable_value missing; ...
[FAIL] convergence.time: ...
[FAIL] convergence.pml: ...
[FAIL] flex_credit: estimated_total None must be a positive number; estimate_source is missing; approved_ceiling None must be a positive number (Astra sets it)
[INFO] task_ids: no task ids yet (nothing submitted) - expected pre-solve
[INFO] evidence: no evidence paths (nothing to back yet)

STUDY PROVENANCE INCOMPLETE (9 failing: identity, candidate_family, material.source, nonlinear.model, geometry.hash, convergence.mesh, convergence.time, convergence.pml, flex_credit)
exit=1
```

Sentetik tam manifest (fixture; fiziksel olmayan placeholder digest'ler,
`candidate_family='synthetic-test-family'`, uydurma gözlem değerleri) →
12/12 PASS, `exit=0` (test `CompleteManifestTest` + CLI testi).

## Açık riskler / sınırlar

- **Şema versiyonlu ama boş.** Gerçek alan değerlerini (aday ailesi, malzeme
  kaynağı/sürümü, nonlinear model kaynağı, tolerans hedefleri, `approved_ceiling`)
  Astra doldurur; bu iskelet onları icat etmez.
- **`converged()` yalnız son iki basamağa bakar** ve tek bir skaler gözlem
  kullanır. Vektör gözlem veya "monoton azalan hata" ölçütü gerekiyorsa Astra
  kararıyla genişletilmeli.
- **`evidence` kontrolü digest'i dosya içeriğiyle karşılaştırmaz**, yalnız
  biçim + `evidence_paths` girdisinin diskte var olması. İçerik-digest eşleşmesi
  ayrı bir kontrol olarak eklenebilir (öneri, bu oturumda yapılmadı).
- **Manifest depolama konumu seçilmedi.** İleride `manifests/fdtd/` altında
  tutulması mantıklı ama bu Astra'nın dizin/sözleşme kararı; bu oturumda dizin
  veya örnek manifest **oluşturulmadı**.
- `BACKLOG.md` / `BACKLOGLOG.md` / `CHANGELOG.md` bu oturumda **değiştirilmedi**
  (sözleşme gereği); FDTD-001 maddesinin "Değişen dosyalar" ve "Sıradaki adım"
  güncellemesi ile CHANGELOG kaydı Astra'ya bırakıldı.
- Testler CPython 3.14.7 ile koşuldu; şema saf stdlib olduğu için sürüm
  hassasiyeti düşük (hash'ler platform bağımsız).

## Sıradaki tek adım

Astra: `python -m unittest discover -s tests -t .` (129/129) ve
`python -m fdtd.provenance validate` boş-şablon çıktısını kaydet; şema alan
setini ve fail-closed kontrol listesini FDTD-001 fizibilite/maliyet kapısının
parçası olarak onayla veya revizyon iste; onaylanırsa aday ailesi + kaynaklı
fiziksel parametreler + `approved_ceiling` ile ilk gerçek çalışma manifestini
oluştur.
