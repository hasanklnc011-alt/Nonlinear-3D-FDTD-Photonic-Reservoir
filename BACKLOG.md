# Backlog

Bu dosya, tamamlanmadan yarıda kalan işleri görünür tutar. Hiçbir iş sessizce half done bırakılamaz.

## Açık işler

### [FDTD-001] Aday aileleri için 3D nonlinear FDTD fizibilite ve maliyet kapısı
- Sahip: Claude Sonnet 5 (karar + kod + yerel test) — Astra geçici devre dışı, bkz. AGENTS.md/CLAUDE.md "Geçici mod" bölümü
- Açılış tarihi: 2026-09-10
- Durum: IN_PROGRESS
- Bağlam: Ratifiye benchmark sonrası üç aday ailesi (MRR, PhC/nanobeam, çok-portlu rezonant saçıcı) için kaynaklı fizik, yerel yakınsama planı ve Tidy3D FlexCredit maliyet kapısı hazırlanacak.
- Değişen dosyalar: `fdtd/provenance/`, `fdtd/mrr/` (parametrik study builder ve lineer plan), `fdtd/tidy3d_build/` (yerel somut Simulation kurucu), `tests/fdtd/`, ilgili karar ve coordination notları.
- Engel veya risk: Gerçek malzeme/nonlinear parametreleri, sınır/mesh/zaman yakınsaması ve maliyet tahmini kaynak/yerel kanıtla doğrulanmadan ücretli cloud solve başlatılamaz. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder; gerçek malzeme kanıtı olmadan kullanılmayacak. Ücretli solve hâlâ yalnız Hasan'ın açık onayıyla başlatılır.
- Sıradaki tek adım: `docs/coordination/2026-09-10-claude-fdtd-001-port-plane-fix.md`'deki port-düzlemi düzeltmesini (through/drop monitör ayrımı) gözden geçir, mevcut committed olmayan değişiklikleri commit et, `rung-0.plan.json`'ı yeni koordinatlarla yeniden üret; Hasan onayı sonrası lineer rung'u yeniden gönder.

## Madde şablonu

```text
### [ID] Kısa başlık
- Sahip:
- Açılış tarihi:
- Durum: OPEN | BLOCKED | IN_PROGRESS
- Bağlam:
- Değişen dosyalar:
- Engel veya risk:
- Sıradaki tek adım:
```

Tamamlanan maddeler bu dosyada tutulmaz; kapanış izi `BACKLOGLOG.md` dosyasına aktarılır.
