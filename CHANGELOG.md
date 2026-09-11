# Changelog

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
