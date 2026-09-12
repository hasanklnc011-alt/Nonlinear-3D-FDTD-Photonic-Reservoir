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
- Sıradaki tek adım: **`freq-rung-2` ONAY BEKLİYOR** (`estimate_cost = 14.7500 FC`, beklenen gerçek `~11.6`, önerilen tavan `15`, draft `fdve-0ecc2c8f-e120-4b3c-8793-c9c0dcbda224`, submit EDİLMEDİ). Rezonans dışı güç açığının kaynağı BULUNDU: bus facet'leri Fabry-Pérot kavitesi kuruyor. Kanıt (`0 FC`, ödenmiş mesh-rung-2 verisi): tam bantta baseline `0.51-0.90` salınıyor (`%40` tepe-tepe), periyot `17.96 nm`; facet turu (`2L=32 um`, `n_g~4.2`) `17.66 nm` öngörüyor, halka FSR'si `18.93 nm`, ve iki tarak bant boyunca birbirinden yürüyor (`+3.74 -> -1.07 nm`). Fringe kontrastı `0.27` -> facet başına `~%14` yansıma, Fresnel ile aynı mertebe. Bugüne kadarki TÜM mutlak genlik ölçümleri (dolayısıyla `Q_i`/`Q_e` girişimi) bu dalgalanmanın üstünde alınmış; `Q_loaded ~ 9 650` etkilenmiyor (FP zarfı 18 nm, çizgi 0.16 nm ölçeğinde). DÜZELTME UYGULANDI: geometri schema `/2` + `bus_overhang_um`; bus `20 um` çiziliyor, uç yüzler `x=+-10`'da yani PML içinde. `domain_size_um` kasten `bus_length_um`'e bağlı kaldı -> domain `18.0 um` ve maliyet büyümedi; port düzlemleri `+-8`'de sabit. `bus_overhang_um = 0` iken alan serileştirmeden çıkarılıp şema `/1` beyan ediliyor -> kilitli merdivenin `6844d49c...` hash'i birebir korundu (19 test, literal pin eklendi; depo `286/286 OK`). freq-rung-2 KABUL ÖLÇÜTLERİ: (1) FP fringe belirgin azalmalı, (2) rezonans dışı dört-port toplamı `1.0`'a yaklaşmalı (şu an `0.77-0.88`), (3) `T_through = (1-sqrt(T_drop))^2` tutmalı -> `Q_i`/`Q_e` ilk kez geçerli olur. Bkz. `docs/decisions/2026-09-13-freq-rung-2-plan.md` ve `2026-09-13-facet-fabry-perot.md`. Mesh yakınsaması (14 step/λ) en sona kaldı.

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
