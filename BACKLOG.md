# Backlog

Bu dosya, tamamlanmadan yarıda kalan işleri görünür tutar. Hiçbir iş sessizce half done bırakılamaz.

## Açık işler

### [FDTD-001] Aday aileleri için 3D nonlinear FDTD fizibilite ve maliyet kapısı
- Sahip: Claude Sonnet 5 (karar + kod + yerel test) — Astra geçici devre dışı, bkz. AGENTS.md/CLAUDE.md "Geçici mod" bölümü
- Açılış tarihi: 2026-09-10
- Durum: IN_PROGRESS
- Bağlam: Ratifiye benchmark sonrası üç aday ailesi (MRR, PhC/nanobeam, çok-portlu rezonant saçıcı) için kaynaklı fizik, yerel yakınsama planı ve Tidy3D FlexCredit maliyet kapısı hazırlanacak.
- Değişen dosyalar: `fdtd/provenance/`, `fdtd/mrr/` (parametrik study builder ve lineer plan), `fdtd/tidy3d_build/` (yerel somut Simulation kurucu), `tests/fdtd/`, ilgili karar ve coordination notları.
- Engel veya risk: Gerçek malzeme/nonlinear parametreleri, sınır/mesh/zaman yakınsaması ve maliyet tahmini kaynak/yerel kanıtla doğrulanmadan ücretli cloud solve başlatılamaz. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder; gerçek malzeme kanıtı olmadan kullanılmayacak. Ücretli solve hâlâ yalnız Hasan'ın açık onayıyla başlatılır. `time-rung-1` (30 ps, gerçek kullanım `1.7888 FC`) final field decay `0.000801` verdi — shutoff eşiği `1e-5`'in hâlâ ~80× üzerinde; zaman yakınsaması kapısı kapalı kaldı (bkz. `docs/decisions/2026-09-10-mrr-linear-rung-0-cloud-preflight.md`). **2026-09-12 literatür taraması** (bkz. `reports/FDTD-001-mrr-feasibility.md` "FCD/FCA riski" bölümü): planlanan Kerr+TPA-only nonlinear aşaması, artık 6 bağımsız kaynağa göre (3'ü yeni okundu, biri aylardır erişilemeyen Ren et al. 2024) muhtemelen silicon MRR reservoir belleğinin asıl kaynağını (FCD/FCA+termal) dışlıyor — risk seviyesi YÜKSEK'e çıkarıldı. Ayrıca CFL zaman-adımı duvarını gevşetecek hiçbir yöntem Tidy3D'ye native olarak uygulanamıyor (Tidy3D'yi terk etmeden çözülemez).
- Sıradaki tek adım: zaman ve PML yakınsaması geçti, ama mesh yakınsaması BAŞARISIZ çıktı — mesh-rung-1 (12 step/λ, 105 ps) through/drop flux'u time-rung-3'e (10 step/λ) göre `%40-60` değiştirdi ve bu run'da zaman yakınsaması da geçmedi (decay `3.62e-05 > 1e-5`), yani mesh ve zaman eksenleri bağımsız değil. Mesh-rung-2 (12 step/λ, 150 ps, task `fdve-b2b294bc-e886-4f84-adcc-4430d5a24a0e`, tahmini `14.551 FC`) Hasan onayıyla `2026-09-11`'de başlatıldı, şu an `queued`. Tamamlanınca: (1) bu run'da decay `<1e-5`'e indi mi kontrol et, (2) yakınsamışsa flux değerlerini time-rung-3 ile kıyasla — hâlâ büyük farklıysa 14/16 step/λ'yı da kendi zaman-yakınsamış run_time'ıyla dene (ayrı onay gerekir).

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
