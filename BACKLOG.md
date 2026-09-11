# Backlog

Bu dosya, tamamlanmadan yarıda kalan işleri görünür tutar. Hiçbir iş sessizce half done bırakılamaz.

## Açık işler

### [FDTD-001] Aday aileleri için 3D nonlinear FDTD fizibilite ve maliyet kapısı
- Sahip: Claude Sonnet 5 (karar + kod + yerel test) — Astra geçici devre dışı, bkz. AGENTS.md/CLAUDE.md "Geçici mod" bölümü
- Açılış tarihi: 2026-09-10
- Durum: IN_PROGRESS
- Bağlam: Ratifiye benchmark sonrası üç aday ailesi (MRR, PhC/nanobeam, çok-portlu rezonant saçıcı) için kaynaklı fizik, yerel yakınsama planı ve Tidy3D FlexCredit maliyet kapısı hazırlanacak.
- Değişen dosyalar: `fdtd/provenance/`, `fdtd/mrr/` (parametrik study builder ve lineer plan), `fdtd/tidy3d_build/` (yerel somut Simulation kurucu), `tests/fdtd/`, ilgili karar ve coordination notları.
- Engel veya risk: Gerçek malzeme/nonlinear parametreleri, sınır/mesh/zaman yakınsaması ve maliyet tahmini kaynak/yerel kanıtla doğrulanmadan ücretli cloud solve başlatılamaz. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder; gerçek malzeme kanıtı olmadan kullanılmayacak. Ücretli solve hâlâ yalnız Hasan'ın açık onayıyla başlatılır. `time-rung-1` (30 ps, gerçek kullanım `1.7888 FC`) final field decay `0.000801` verdi — shutoff eşiği `1e-5`'in hâlâ ~80× üzerinde; zaman yakınsaması kapısı kapalı kaldı (bkz. `docs/decisions/2026-09-10-mrr-linear-rung-0-cloud-preflight.md`).
- Sıradaki tek adım: zaman ve PML yakınsaması geçti (time-rung-3 decay `7.05e-06`; pml-rung-1 16-katman ile through/drop flux 6 hanede aynı, decay `6.93e-06`). Başarı kapısı 3'ün kalan tek parçası mesh yakınsaması. Hasan önce ucuz bir adımla (10→12 step/λ) denenmesini istedi; maliyet tahmini çıkarılıp onaya sunulacak, ücretli solve Hasan onayı olmadan başlatılmayacak.

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
