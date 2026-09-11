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
- Sıradaki tek adım: `time-rung-2` (90 ps) tamamlandı, final decay `1.53e-05` — hedefin `~1.53×` üzerinde, hâlâ kapı kapalı. Hasan `time-rung-3` (105 ps, task `fdve-5f199de8-272c-47e1-b6ce-2cf8822ff4e8`, tahmini `5.987 FC`) başlatılmasını onayladı; `2026-09-11`'de başlatıldı, şu an `queued`. Tamamlanınca sonucu indir, field decay'i `1e-5` eşiğine karşı kontrol et, sonucu `docs/decisions/2026-09-10-mrr-linear-rung-0-cloud-preflight.md`'e kaydet.

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
