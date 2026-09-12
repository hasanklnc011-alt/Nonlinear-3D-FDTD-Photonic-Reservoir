# Changelog

## 2026-09-13

- Çalışma sözleşmesi tek operatöre geçirildi: ChatGPT/Astra orkestra şefliği
  `AGENTS.md`, `CLAUDE.md` ve `const.md` içinden kalıcı olarak kaldırıldı
  (bkz. `docs/decisions/2026-09-13-single-operator-contract.md`). Tamamlanmış
  Tidy3D task sonuçlarını indirme yasağı kalktı; ücretli solve için Hasan
  onayı şartı korundu.
- `Q_loaded ~ 27.000` (FWHM `~0.056 nm`) ring-down fit'inden çıkarıldı; Tidy3D
  `shutoff` tanımı (E-field intensity oranı) doğrulanarak 2x belirsizlik kapandı.
- `linear_build._monitors` artık monitör başına `sampling` bloğunu kullanıyor;
  monitör frekans tarağı kaynak darbesinden ayrıştırıldı (8 yeni test, 187/187 OK).
- `freq-rung-1` Hasan'ın açık onayıyla BAŞLATILDI: task
  `fdve-719dd4d0-fed8-4d10-9be8-6c0aab8b047a`, tahmin `14.6803 FC`, yazılı tavan
  `15 FC`, submit öncesi tahmin yeniden doğrulandı. `1501` nokta / `2 pm` adım
  dar-bant tarak; amaç `Q_i`/`Q_e` ayrımı.
- `mesh-rung-2` indirildi ve değerlendirildi (task `fdve-b2b294bc...`, gerçek
  `11.4329 FC`): zaman yakınsaması GEÇTİ (`9.99e-06 < 1e-5`), mesh yakınsaması
  GEÇMEDİ (10->12 step/λ rezonansları `+1.5..+1.9 nm` kaydırıyor, FSR'nin ~%8'i).
  Flux monitörlerinin `0.5 nm` frekans adımı rezonansları çözmüyor; `Q_i`/`Q_e`
  ve coupling hiçbir mevcut koşudan çıkarılamıyor
  (`docs/decisions/2026-09-13-mesh-rung-2-evaluation.md`).
- Geometriyle sınırlandırılmış, belirsizliklere dayanıklı MRR reservoir için
  TCMT/FDTD araştırma planı Claude incelemesine açık taslak olarak eklendi.
- Taslak mevcut `const.md`, çalışma sözleşmesi ve kilitli NARMA-10 benchmarkını
  değiştirmiyor; olası sözleşme değişikliği ayrı karar kaydına bırakıldı.

## 2026-09-10

- Claude Sonnet 5 high yerel NARMA-10 benchmark iskeletini üretti.
- Astra doğrulaması iki eşzamanlı iskeleti tekilleştirdi: `benchmarks/narma10_np/`
  kanonik hattır.
- 66 kanonik test ve iki hash-kilitli manifest doğrulaması geçti.
- Tidy3D cloud solve, aday kilidi ve kör değerlendirme başlatılmadı.
- Benchmark preflight eklendi; 8/8 kontrol ve 82/82 test geçti. Klasik
  NARMA-10 manifest sözleşmesi ratifiye edildi ve FDTD-001 fizibilite aşaması açıldı.
- FDTD candidate-study provenance validator eklendi; 129/129 test geçti ve
  kanıtsız çalışma manifestoları fail-closed reddediliyor.
- Parametrik silicon-MRR study builder eklendi; toplam 164/164 test geçti.
- Yerel-only `tidy3d.Simulation` kurucu katmanı eklendi: doğrulanmış lineer planı
  somut Simulation nesnesine çeviriyor, kanonik JSON ve SHA-256 digest üretiyor;
  cloud/web çağrıları ve nonlinear içerik fail-closed engelleniyor.
- İlk fiziksel lineer Si-MRR convergence rung'u Tidy3D'ye gönderildi: tahmin
  0.6261476005924334 FlexCredit, task `fdve-7a16b155-f684-4bae-91ea-c1dd59877758`.
