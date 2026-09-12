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
- Sıradaki tek adım: **rezonans dışı `%12-23` güç açığının kaynağını bul.** İki ücretsiz adım tamamlandı. (1) BOX sızıntı hipotezi ÇÜRÜTÜLDÜ (`0 FC`, yerel mode solver): `1.0/2.0/3.0 um` BOX'ta substrate gücü `%0.00`, `k_eff` gürültü tabanında (`4.3e-08` vs referans `-1.2e-08`), sızıntı `0.02 dB/cm` = tur başına `6e-06 dB`. BOX `1.0 um` KORUNUYOR. Kontrol grubu geçerli (`n_eff=2.40167`, beklenen SOI strip değeri). Not: `BOX=2.0` satırı mod seçicisinin farklı bir mod aldığını gösteriyor (`n_eff=2.2796`, tek-düze değil) — hüküm etkilenmiyor ama `n_eff` kalibrasyon çıktısı olarak kullanılacaksa polarizasyon sabitlenmeli ve ızgara yakınsaması yapılmalı. Yan bulgu: modun `%60-63`'ü çekirdekte, gerisi evanescent — `0.2 um` gap üzerinden `Q_e`'yi belirleyen oran. (2) Dört-port monitör doğrulandı (`0 FC`, KOD DEĞİŞİKLİĞİ YOK): `flux:bus_drop:in` token'ı `_port_plane` sayesinde gerçek drop portuna (`x=-8`, drop bus merkez hattı) oturuyor; translate+build yerel geçti, 4 monitör. SINIR: `flux:bus_through:in` kaynakla aynı düzlemde, oradaki flux net değer verir (temiz yansıma ölçümü değil). KALAN ŞÜPHELİ: kaynak ve monitör düzlemleri waveguide'ın kesilmiş uç yüzlerinde (`x=+-8`, domain `+-9`, arkada 1 um oksit sonra PML); sonlandırılmış facette enjeksiyon kılavuza girmeyen geri radyasyon üretir ve ölçülen eğimli baseline (`0.774`->`0.884`, 3 nm içinde) bununla uyumlu. Dört-port düzeltmesi rezonanstaki `%69`'u açıklar, rezonans dışını açıklamaz. Bkz. `docs/decisions/2026-09-13-box-leakage-falsified.md`. Sonra: düzeltilmiş port kurgusuyla tek ücretli koşu -> `Q_i`/`Q_e`; en son 14 step/λ mesh yakınsaması.

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
