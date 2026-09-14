# Kör suite bu depodan taşındı

Tarih: 2026-09-14. Karar: [docs/decisions/2026-09-14-blind-suite-moved.md](docs/decisions/2026-09-14-blind-suite-moved.md).

10 kör NARMA-10 seed'inin tek meşru değerlendirme yolu artık
**Kerr-Ring-Reservoir** deposudur. Taşındı, kopyalanmadı.

Bu depodaki `python -m benchmarks.narma10_np blind-eval` komutu, bu dosya
mevcut olduğu sürece `BlindEvaluationBlocked` ile reddeder. Dosyayı silerek
kör yolu yeniden açmak, "tek kör suite" sözleşmesinin ihlalidir ve ancak
Hasan'ın açık kararı ve yeni bir karar kaydıyla yapılabilir.

Bu depodaki geliştirme (dev) seed'leri, benchmark kodu ve testler
**çalışmaya devam eder**; kapatılan yalnız kör değerlendirme yoludur.
