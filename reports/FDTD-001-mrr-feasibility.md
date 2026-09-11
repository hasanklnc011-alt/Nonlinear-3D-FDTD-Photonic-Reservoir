# FDTD-001 — Silicon MRR fizibilite ve ilk çözüm merdiveni

## Astra kararı

İlk 3B aday, telecom-band silicon MRR'dır. İlk ücretli çözüm **doğrusal**
rezonans/mesh/zaman/PML yakınsamasıdır; nonlinear kabul yalnız Kerr, TPA ve
taşıyıcı etkilerinin kapsamı açıkça kayda alındıktan sonra açılır.

## Kaynaklı fizik

- 1.54–1.55 µm'de kristal silicon için derleme tablosu `n2 = 400 × 10^-20 m²/W`
  ve `beta_TPA = 0.8 cm/GW` verir. Bu değerler MRR konfigürasyonuna ancak aynı
  dalga boyu ve malzeme kaynağı manifestte hash'lenirse girer.
  Kaynak: https://pmc.ncbi.nlm.nih.gov/articles/PMC10058895/
- Silicon'da telecom TPA'nın serbest taşıyıcı üretip FCA/FCD eklediği ve bunun
  nonlinear reservoir davranışında önemli olduğu belirtilmiştir. İlk Kerr+TPA
  FDTD, FCD/FCA'nın çözülmediğini açıkça sınırlayacaktır.
  Kaynak: https://pmc.ncbi.nlm.nih.gov/articles/PMC12909825/
- Tidy3D `KerrNonlinearity` ve `TwoPhotonAbsorption` sağlar; güçlü nonlinear
  çözüm iteratif olduğundan yakınsama ayrıca test edilir.
  Kaynak: https://docs.flexcompute.com/projects/tidy3d/en/latest/api/_autosummary/tidy3d.KerrNonlinearity.html

## Maliyet ve çözüm sırası

1. Yerel parametrik MRR geometri/config hash'i üret.
2. Cloud'a yalnız lineer, düşük çözünürlüklü tek rezonans task'ı yükle;
   `estimate_cost` üst sınırını kaydet, sonra başlat.
3. Mesh, zaman ve PML için en az iki rafinman basamağında aynı rezonans
   gözlenebilirini karşılaştır.
4. Doğrusal kapı geçerse kaynak-hash'li Kerr+TPA task'ını oluştur ve maliyeti
   yeniden tahmin et. FCD/FCA yoksa sonuç yalnız kısmi nonlinear kanıttır.

Tidy3D FDTD tahmini tam `run_time` üst sınırıdır; early shutoff gerçek maliyeti
düşürebilir. Kaynak: https://docs.flexcompute.com/projects/tidy3d/en/v2.5.1/_autosummary/tidy3d.web.estimate_cost.html
