# Proje Sözleşmesi

## Amaç

Gerçek malzeme ve nonlinear elektromanyetik model içeren, Tidy3D ile uçtan uca 3D FDTD çözülen photonic reservoir tasarlamak ve NARMA-10'da medyan test NMSE `< 0.05` hedefini sınamak.

## Kapsam

Topoloji serbesttir. Mimari; fiziksel hafıza, gözlenebilir port özellikleri, nonlinear tepki, güç/hız fizibilitesi ve FDTD maliyeti birlikte değerlendirilerek seçilir.

## Kapsam dışı

İlk yapısal aşamada kod, ücretli cloud solve, üretim PDK'sı ve deneysel çip doğrulaması yoktur.

## Başarı kapıları

1. Benchmark ve kör seed hash'leri kilitli.
2. Maliyet ve kaynak fizibilitesi raporlu.
3. Mesh, zaman, PML ve nonlinear yakınsaması kanıtlı.
4. Aday kilidinden sonra 10 kör seed: medyan test NMSE `< 0.05`, en az 8/10 seed `< 0.05`.

## Durma koşulları

Sonlu olmayan veri, doğrulanmamış fizik, yakınsamayan FDTD veya bütçe dışı tahmin halinde ilgili aşama durur ve gerekçe kaydedilir.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/spiral-delay-reservoir/MayOS/Photonic-Reservoir|Önceki Photonic Reservoir hattı]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]
