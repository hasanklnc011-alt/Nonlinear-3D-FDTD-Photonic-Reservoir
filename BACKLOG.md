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
- Sıradaki tek adım: `mesh-rung-2` (task `fdve-b2b294bc-e886-4f84-adcc-4430d5a24a0e`) indirildi ve değerlendirildi — gerçek maliyet `11.4329 FC`. **Zaman kapısı GEÇTİ** (final decay `9.99e-06 < 1e-5`, ~118 ps'de erken shutoff; aynı mesh'teki 105 ps'lik mesh-rung-1 ile bant-integre fark through `+0.01%` / drop `+1.21%`, rezonanslar altı hanede aynı). **Mesh kapısı GEÇMEDİ**: 10->12 step/λ tüm rezonansları sistematik kaydırıyor (`+1.89`, `+1.45`, `+1.52`, `+1.56` nm; FSR `18.6-19.5 nm`, yani ~%8). Önceki `%40-60` flux bulgusu büyük ölçüde örnekleme artefaktıymış (gerçek bant-integre fark through `-0.26%`, drop `+7.83%`). Sıradaki adım 14/16 step/λ DEĞİL: aynı kör monitörle daha yüksek mesh yine Q/coupling üretmez. Önce **frekans monitörü düzeltilecek** — 12 step/λ korunur, bant rezonans çevresine daraltılır veya frekans noktası `201 -> ~2000` yapılır (DFT noktası eklemek time-stepping maliyetini değiştirmez; koşu yine ~11-12 FC). Ardından aynı düzeltilmiş monitörle 14 step/λ tekrarlanıp rezonans-kayması yakınsama testi yapılır. Her iki koşu da ayrı Hasan onayı ister.

## Madde şablonu

```text
### [ID] Kısa başlık
- Sahip:
- Açılış tarihi:
- Durum: OPEN | BLOCKED | IN_PROGRESS
- Bağlam:
- Değişen dosyalar:
- Engel veya risk: Ücretli cloud solve yalnız Hasan'ın açık onayıyla ve yazılı `estimate_cost` üst sınırıyla başlatılır. Yerel kurucu yalnız non-dispersive dar-bant proxy kabul eder. **MONİTÖR KUSURU (2026-09-13, YENİ, kapı-engelleyici):** flux monitörleri `1.500-1.600 um` bandında yalnız `201` nokta = `0.500 nm` adım kullanıyor; ölçülen rezonansların FWHM'i bundan küçük (tepe tek örnekten ibaret, komşular 20-70x aşağıda, gerçek `Q > ~3100`). Bu nedenle rung'lar arası genlik karşılaştırmaları geçersiz ve `Q_i`/`Q_e`, extinction ratio, coupling **hiçbir mevcut koşudan çıkarılamaz**. Kusur rung-0'dan beri tüm koşularda mevcut (bkz. `docs/decisions/2026-09-13-mesh-rung-2-evaluation.md`). **FCD/FCA riski YÜKSEK** (bkz. `reports/FDTD-001-mrr-feasibility.md`): Kerr+TPA-only nonlinear aşaması, 6 bağımsız kaynağa göre silicon MRR belleğinin asıl kaynağını (FCD/FCA+termal) dışlıyor. CFL zaman-adımı duvarı Tidy3D terk edilmeden aşılamıyor.
- Sıradaki tek adım: `mesh-rung-2` (task `fdve-b2b294bc-e886-4f84-adcc-4430d5a24a0e`) indirildi ve değerlendirildi — gerçek maliyet `11.4329 FC`. **Zaman kapısı GEÇTİ** (final decay `9.99e-06 < 1e-5`, ~118 ps'de erken shutoff; aynı mesh'teki 105 ps'lik mesh-rung-1 ile bant-integre fark through `+0.01%` / drop `+1.21%`, rezonanslar altı hanede aynı). **Mesh kapısı GEÇMEDİ**: 10->12 step/λ tüm rezonansları sistematik kaydırıyor (`+1.89`, `+1.45`, `+1.52`, `+1.56` nm; FSR `18.6-19.5 nm`, yani ~%8). Önceki `%40-60` flux bulgusu büyük ölçüde örnekleme artefaktıymış (gerçek bant-integre fark through `-0.26%`, drop `+7.83%`). Sıradaki adım 14/16 step/λ DEĞİL: aynı kör monitörle daha yüksek mesh yine Q/coupling üretmez. Önce **frekans monitörü düzeltilecek** — 12 step/λ korunur, bant rezonans çevresine daraltılır veya frekans noktası `201 -> ~2000` yapılır (DFT noktası eklemek time-stepping maliyetini değiştirmez; koşu yine ~11-12 FC). Ardından aynı düzeltilmiş monitörle 14 step/λ tekrarlanıp rezonans-kayması yakınsama testi yapılır. Her iki koşu da ayrı Hasan onayı ister.
```

Tamamlanan maddeler bu dosyada tutulmaz; kapanış izi `BACKLOGLOG.md` dosyasına aktarılır.
