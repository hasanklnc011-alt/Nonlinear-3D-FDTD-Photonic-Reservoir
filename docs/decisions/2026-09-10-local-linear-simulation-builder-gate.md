# Yerel lineer Simulation kurucu kapısı

- Tarih: 2026-09-10
- Karar sahibi: Astra/Codex
- Durum: Kabul edildi

## Karar

`fdtd.mrr` saf planlama/provenance katmanı olarak kalacak. Doğrulanmış
`LinearSimulationPlan`, yalnızca kardeş paket `fdtd.tidy3d_build` içinde lazy
Tidy3D importuyla somut `tidy3d.Simulation` nesnesine dönüştürülecek.

## Kabul gerekçesi

- Kurucu, planı tekrar dry-run kapısından geçirir; lineerlik, provenance ve cloud
  alanları ihlal edilirse nesne kurmadan hata verir.
- `tidy3d.web`, upload, maliyet tahmini, başlatma, indirme ve ağ modülleri bu
  katmanda yoktur.
- Medium, yapı, PML, kaynak, monitör, AutoGrid, run-time ve shutoff değerleri
  plandan alınır; fiziksel parametre seçmez.
- Tidy3D'nin yerel serileştirmesi anahtar-sıralı JSON'a dönüştürülür ve SHA-256
  ile kimliklenir. Böylece cloud öncesi konfigürasyon sabitlenebilir.

## Doğrulama

Claude teslimi 29 yeni test ve toplam 244/244 yerel test raporladı. Astra/Codex,
modül sınırını ve fail-closed koşullarını bağımsız kod denetimiyle doğruladı.

## Sınır ve sonraki kapı

Bu katman non-dispersive lineer Medium ile sınırlıdır; gerçek MRR solve için
kaynaklı Si/SiO2 değerleri, dar-bant yaklaşımının geçerlilik aralığı, mesh/zaman/PML
convergence rung'u, plan ve Simulation digest'i ile maliyet tahmini ayrı kayda
bağlanmadan cloud solve gönderilemez.
