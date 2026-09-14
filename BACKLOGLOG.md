# Backlog Log

Bu dosya backlog maddelerinin kapanış ve devir günlüğüdür. Kayıtlar silinmez; her kayıt tarih, madde ID'si, yapılan iş, doğrulama ve sonucu içerir.

## Kayıt şablonu

```text
### YYYY-MM-DD — [ID] Kısa başlık
- Ajan:
- İşlem: tamamlandı | devredildi | yeniden açıldı
- Değişen dosyalar:
- Doğrulama kanıtı:
- Sonuç / sonraki adım:
```

## Kayıtlar

### 2026-09-13 — [SÖZLEŞME] "Geçici mod: Astra devre dışı" kapatıldı

- Kapanış biçimi: geçici mod kaldırıldı, yerine kalıcı tek-operatör rol
  dağılımı kondu. Astra geri dönüşü beklenmiyor (ChatGPT kredisi bitti).
- Karar kaydı: `docs/decisions/2026-09-13-single-operator-contract.md`
- Değişen dosyalar: `AGENTS.md`, `CLAUDE.md`, `const.md`, `BACKLOG.md`,
  `CHANGELOG.md`
- Korunan sınır: ücretli Tidy3D solve hâlâ yalnız Hasan'ın açık onayıyla.

### 2026-09-10 — [FDTD-001] Yerel lineer Tidy3D Simulation kurucusu
- Ajan: Claude Sonnet 5 high + Astra/Codex
- İşlem: tamamlandı
- Değişen dosyalar: `fdtd/tidy3d_build/linear_build.py`, `fdtd/tidy3d_build/__init__.py`, `tests/fdtd/_linear_build_driver.py`, `tests/fdtd/test_linear_build.py`, `docs/coordination/2026-09-10-claude-fdtd-001-linear-build.md`
- Doğrulama kanıtı: Claude yerel tam depo testini 244/244 OK olarak raporladı; Astra/Codex bağımsız yeniden çalıştırması da `Ran 244 tests in 53.991s — OK` verdi. Kod denetimi lazy `tidy3d` importu, `tidy3d.web`/ağ çağrısı yasağı, lineerlik/provenance fail-closed geçidi, kanonik Simulation JSON+SHA-256 ve plan değerlerinin birebir çevirisini doğruladı.
- Sonuç / sonraki adım: Fiziksel parametre seçilmedi, cloud solve başlatılmadı. Kaynaklı lineer Si/SiO2 artefaktı ve ilk convergence rung'u gerekir.

### 2026-09-10 — [FDTD-001] Silicon MRR study builder
- Ajan: Claude Sonnet 5 + Astra/Codex
- İşlem: tamamlandı
- Değişen dosyalar: `fdtd/mrr/`, `tests/fdtd/test_mrr.py`, `docs/coordination/2026-09-10-claude-fdtd-001-mrr-study-builder.md`
- Doğrulama kanıtı: Tüm depo testleri 164/164 geçti; builder Tidy3D/network import etmeden deterministik geometri/config hash'i ve eksik fizik kanıtında fail-closed manifest üretiyor.
- Sonuç / sonraki adım: Kaynaklı silicon/Kerr/TPA parametreleri ve linear convergence ladder ile ilk cloud maliyet tahminine geçilir.

### 2026-09-10 — [FDTD-001] Provenance validator kapısı
- Ajan: Claude Sonnet 5 + Astra/Codex
- İşlem: tamamlandı
- Değişen dosyalar: `fdtd/provenance/`, `tests/fdtd/`, `docs/decisions/2026-09-10-fdtd-provenance-gate.md`
- Doğrulama kanıtı: `python -m unittest discover -s tests -t . -v` 129/129 geçti; boş şablon 9 eksik kanıtla fail-closed reddedildi.
- Sonuç / sonraki adım: Ücretli solve öncesi provenance/maliyet/near-sama kaydı zorunlu. Astra kaynaklı aday fizibilite raporuna geçer.

### 2026-09-10 — [BM-001] Benchmark ratifikasyonu ve preflight
- Ajan: Astra/Codex + Claude Sonnet 5
- İşlem: tamamlandı
- Değişen dosyalar: `benchmarks/narma10_np/preflight.py`, `benchmarks/narma10_np/cli.py`, `tests/narma10_np/test_preflight.py`, `docs/decisions/2026-09-10-benchmark-ratification.md`
- Doğrulama kanıtı: `python -m unittest discover -s tests -t . -v` 82/82 geçti; `python -m benchmarks.narma10_np preflight` 8/8 kontrol geçti.
- Sonuç / sonraki adım: Klasik NARMA-10, CPython 3.14.7/NumPy 2.4.6 ve dev/blind manifest digestleri ratifiye edildi. FDTD-001 fizibilite/maliyet kapısına geçildi.

### 2026-09-10 — [BM-001] Kanonik benchmark seçimi ve yerel doğrulama
- Ajan: Astra/Codex
- İşlem: devredildi
- Değişen dosyalar: `benchmarks/narma10_np/`, `manifests/narma10/`, `tests/narma10_np/`, `docs/decisions/2026-09-10-benchmark-canonicalization.md`, `CHANGELOG.md`
- Doğrulama kanıtı: `python -m unittest discover -s tests -t . -v` ile 66/66 test geçti; `python -m benchmarks.narma10_np verify-manifests` dev ve blind manifestolarını doğruladı.
- Sonuç / sonraki adım: NumPy hattı kanonik seçildi. Blind manifest ratifikasyonu ve candidate lock ayrı Astra kararı olarak açık kaldı; cloud solve başlatılmadı.

### 2026-09-10 — [BOOT-001] Claude Code oturum açma ve ilk benchmark iskeleti
- Ajan: Astra/Codex
- İşlem: tamamlandı
- Değişen dosyalar: `BACKLOG.md`, `BACKLOGLOG.md`
- Doğrulama kanıtı: `claude --version` = `2.1.267`; `claude auth status` `loggedIn: true`, `authMethod: claude.ai`, `subscriptionType: pro` döndürdü.
- Sonuç / sonraki adım: Önceki `/login` engeli kalktı. Claude Sonnet 5 high, yalnız NARMA-10 benchmark iskeleti ve yerel testler için başlatılabilir.

### 2026-09-10 — [BOOT-001] Claude Code ilk görev denemesi
- Ajan: Astra/Codex
- İşlem: devredildi
- Değişen dosyalar: `AGENTS.md`, `CLAUDE.md`, `BACKLOG.md`
- Doğrulama kanıtı: Claude Code 2.1.226 çalıştı ancak `/login` gerektiğini bildirdi.
- Sonuç / sonraki adım: Kimlik doğrulaması sonrası NARMA-10 benchmark iskeleti başlatılacak.

### 2026-09-10 — Yapısal backlog sistemi
- Ajan: ChatGPT
- İşlem: tamamlandı
- Değişen dosyalar: `AGENTS.md`, `CLAUDE.md`, `BACKLOG.md`, `BACKLOGLOG.md`
- Doğrulama kanıtı: Dosya yapısı ve Git diff kontrolü
- Sonuç / sonraki adım: Yarım kalan her iş artık backlog maddesi olarak izlenecek.

## 2026-09-13 — FDTD-001 eski backlog K0–K5 ile değiştirildi

Aşağıdaki metin tarihsel snapshot; güncel görev değildir.

<details><summary>Önceki backlog (tam metin)</summary>

# Backlog

Bu dosya, tamamlanmadan yarıda kalan işleri görünür tutar. Hiçbir iş sessizce half done bırakılamaz.

## Açık işler

### [FDTD-001] Aday aileleri için 3D nonlinear FDTD fizibilite ve maliyet kapısı
- Sahip: Claude (karar + kod + yerel test) — tek operatör sözleşmesi, bkz. AGENTS.md "Rol dağılımı"
- Açılış tarihi: 2026-09-10
- Durum: IN_PROGRESS
- Bağlam: Ratifiye benchmark sonrası üç aday ailesi (MRR, PhC/nanobeam, çok-portlu rezonant saçıcı) için kaynaklı fizik, yerel yakınsama planı ve Tidy3D FlexCredit maliyet kapısı hazırlanacak.
- Değişen dosyalar: `fdtd/provenance/`, `fdtd/mrr/` (parametrik study builder ve lineer plan), `fdtd/tidy3d_build/` (yerel somut Simulation kurucu), `tests/fdtd/`, ilgili karar ve coordination notları.
- Engel veya risk: Ücretli cloud solve yalnız Hasan'ın açık onayıyla ve yazılı `estimate_cost` üst sınırıyla başlatılır. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder. **MONİTÖR KUSURU (2026-09-13, YENİ, kapı-engelleyici):** flux monitörleri `1.500-1.600 um` bandında yalnız `201` nokta = `0.500 nm` adım kullanıyor; ölçülen rezonansların FWHM'i bundan küçük (tepe tek örnekten ibaret, komşular 20-70x aşağıda, gerçek `Q > ~3100`). Bu nedenle rung'lar arası genlik karşılaştırmaları geçersiz ve `Q_i`/`Q_e`, extinction ratio, coupling **hiçbir mevcut koşudan çıkarılamaz**. Kusur rung-0'dan beri tüm koşularda mevcut (bkz. `docs/decisions/2026-09-13-mesh-rung-2-evaluation.md`). **FCD/FCA riski YÜKSEK** (bkz. `reports/FDTD-001-mrr-feasibility.md`): Kerr+TPA-only nonlinear aşaması, 6 bağımsız kaynağa göre silicon MRR belleğinin asıl kaynağını (FCD/FCA+termal) dışlıyor. CFL zaman-adımı duvarı Tidy3D terk edilmeden aşılamıyor.
- Sıradaki tek adım: **mod seçicisini sabitle (polarizasyon + simetri), sonra `Q_e` uyuşmazlığını daralt — ikisi de `0 FC`.** V3/V4 yerel çapraz kontrolleri yapıldı: 1 geçti, 3 sorun açtı. GEÇTİ: FSR çaprazlaması, mode solver `n_g = 4.145` ile öngörülen `19.091 nm` vs ölçülen `18.93` → `%0.85`; `n_eff`/`n_g` için V3 kapandı. SORUN 1: bend `Q_i` gürültü tabanında (`k_eff ~6e-08`, yarıçap `1.7x` büyürken yalnız `%29` değişiyor, üstel değil) → `Q_bend > 3e7` alt sınır. Malzemeler kayıpsız + bend radyasyonu ihmal edilebilir olduğuna göre bu modelde fiziksel intrinsic kayıp yok denecek kadar az; oysa FDTD transmisyonundan `Q_i = 3.8e4-7.1e4` çıkarmıştık, `~1000x` fark. O sayı sayısal kaybın ölçüsüydü. `freq-rung-3`'te kayıp kanallarının yakınsamaması da bununla açıklanıyor. SORUN 2: `Q_e` çapraz yolu düştü, supermode `44 774` vs FDTD `12 180` (`3.7x`); önceki `± %1.3` yalnız mesh belirsizliğiydi. SORUN 3: `n_eff` V4 salınıyor (`2.3702/2.3670/2.2987/2.3638`), mod seçici kararsızlığı. Yakınsamış VE çapraz doğrulanmış tek büyüklükler: `lambda_0`, `n_eff`, `n_g`. AYRICA ADR'de `Q_i`'nin FDTD-yetkili listesinden kaynaklı-girdi listesine taşınması gerekiyor; `const.md`'ye dokunduğu için Hasan onayı gerekir. Bkz. `docs/decisions/2026-09-13-v3v4-local-crosschecks.md`. Yeni FDTD koşusu GEREKMİYOR.

## Madde şablonu

```text
### [ID] Kısa başlık
- Sahip:
- Açılış tarihi:
- Durum: OPEN | BLOCKED | IN_PROGRESS
- Bağlam:
- Değişen dosyalar:
- Engel veya risk: Ücretli cloud solve yalnız Hasan'ın açık onayıyla ve yazılı `estimate_cost` üst sınırıyla başlatılır. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder. **MONİTÖR KUSURU (2026-09-13, YENİ, kapı-engelleyici):** flux monitörleri `1.500-1.600 um` bandında yalnız `201` nokta = `0.500 nm` adım kullanıyor; ölçülen rezonansların FWHM'i bundan küçük (tepe tek örnekten ibaret, komşular 20-70x aşağıda, gerçek `Q > ~3100`). Bu nedenle rung'lar arası genlik karşılaştırmaları geçersiz ve `Q_i`/`Q_e`, extinction ratio, coupling **hiçbir mevcut koşudan çıkarılamaz**. Kusur rung-0'dan beri tüm koşularda mevcut (bkz. `docs/decisions/2026-09-13-mesh-rung-2-evaluation.md`). **FCD/FCA riski YÜKSEK** (bkz. `reports/FDTD-001-mrr-feasibility.md`): Kerr+TPA-only nonlinear aşaması, 6 bağımsız kaynağa göre silicon MRR belleğinin asıl kaynağını (FCD/FCA+termal) dışlıyor. CFL zaman-adımı duvarı Tidy3D terk edilmeden aşılamıyor.
- Sıradaki tek adım: **`freq-rung-1` Hasan onayı bekliyor.** `mesh-rung-2` değerlendirildi (gerçek `11.4329 FC`): zaman kapısı GEÇTİ (`9.99e-06 < 1e-5`), mesh kapısı GEÇMEDİ (10->12 step/λ rezonansları `+1.45..+1.89 nm` kaydırıyor, FSR'nin ~%8'i). Ring-down fit'inden `Q_loaded ~ 27.000`, FWHM `~0.056 nm`; Tidy3D `shutoff` tanımı (E-field intensity oranı) doğrulanarak 2x belirsizlik kapatıldı. `Q_i`/`Q_e` ayrımı rezonans genliği ister, o da `0.5 nm` örneklemeyle ölçülemiyor. `linear_build._monitors` artık monitör başına `sampling` bloğunu kullanıyor (kaynak darbesi ayrıştırıldı; `tests/fdtd/test_monitor_sampling.py`, depo `187/187 OK`). `manifests/fdtd/mrr-linear-001/freq-rung-1.plan.json` hazır: mesh-rung-2 ile aynı geometri/mesh/run_time, monitör tarağı `1.53943-1.54243 um` bandında `1501` nokta (`2 pm` adım, FWHM başına ~28 nokta). `estimate_cost = 14.6803 FC`, önerilen tavan `15 FC`, draft task `fdve-719dd4d0-fed8-4d10-9be8-6c0aab8b047a` (yalnız estimate, CALISTIRILMADI). Bkz. `docs/decisions/2026-09-13-freq-rung-1-plan.md`. Onay gelirse çalıştır; sonra düzeltilmiş tarakla 14 step/λ (`freq-rung-2`, ayrı onay) ile mesh yakınsaması kapatılır.
```

Tamamlanan maddeler bu dosyada tutulmaz; kapanış izi `BACKLOGLOG.md` dosyasına aktarılır.

</details>

K0: kullanıcı onaylı ADR, sözleşme ve durum tutarlılığı uygulandı; Git yayını doğrulanacak.

## 2026-09-14 — K0 rol kapsamı ve Claude devri

- Kullanıcı düzeltmesi: Codex yalnız dokümantasyon; kod ve test uygulaması Claude.
- K0 ana doküman teslimatı: 316803907a2485e8dec9cd27f9ec70bc0810e49d, origin/main üzerinde yayımlandı.
- K1–K5 OPEN; yeni uygulama kodu yazılmadı, ücretli solve başlatılmadı.
- Ön hazırlık: depo dışında C:/Users/hasan/.codex/envs/mrr-recovery-212 ortamına tidy3d[extras]==2.12.0 ve numpy==2.4.6 kuruldu. Ana ortam değiştirilmedi. Subpixel etkinliği ve fizik kapıları henüz doğrulanmadı; kurulum K1 kabul kanıtı değildir.
- Claude için sıra: K1 tekrar üretilebilir tanı; ardından K2 çekirdeği ve benchmark güvenliği. K3 öncesi ilgili kabul kanıtları ve yazılı maliyet/onay zorunlu.

## 2026-09-14 — Plan 2 dokümantasyon devri

- Sahip: Codex (doküman); uygulama sahibi Claude.
- Tamamlandı: ADR, çalışma alanı README, P0–P6 backlog, kapsam/bütçe/sahiplik hizalaması.
- Teknik P0 ve P1–P6 açık; kaynak tablosu, sürüm kilidi, analitik çekirdek bu committe üretilmedi.
- Sonraki adım: Claude ortak K2s ve P0; ardından P1 kaynakları/P2 analitik çekirdek.
