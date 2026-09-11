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
