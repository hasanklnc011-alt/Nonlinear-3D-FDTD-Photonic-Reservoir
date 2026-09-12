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
  **Risk seviyesi yükseltildi — bkz. aşağıdaki "FCD/FCA riski" bölümü
  (2026-09-12 literatür taraması sonrası).**
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

## FCD/FCA riski — YÜKSEK (2026-09-12 literatür taraması sonrası güncelleme)

Claude Sonnet 5, geçici Astra-devre-dışı modunda, `~50-70` ajanlık bir
literatür taraması ve gap-analiz workflow'u çalıştırdı (Hasan'ın "yeni yollar
bul, literatüre bak" talebiyle). Şüpheci (adversarial) doğrulama geçişinden
sonra tek bir yeni teknik/mimari öneri tam olarak ayakta kalmadı, ama bir
fiziksel risk bulgusu üç eksende de (yenilik, fizibilite, kanıt) doğrulandı
ve önceki değerlendirmemizden daha güçlü çıktı:

**Bulgu**: Kerr+TPA-only nonlinear planımız (FCD/FCA ve termal etkiler hariç),
muhtemelen silicon MRR reservoir'lerinde asıl bellek/nonlinearite kaynağını
dışlıyor. Artık **6 bağımsız kaynak** aynı sonuca varıyor — üçü daha önce
vault'ta biliniyordu, üçü bu taramada yeni bulundu ve tam metin okundu:

- (bilinen) Bazzanella et al. 2022 — gerçek tek-SOI-MRR deneyi; bellek
  photon-lifetime'dan değil, TPA-üretilen serbest taşıyıcı/termal
  gevşemeden geliyor.
- (bilinen) Foradori et al. 2026, arXiv:2509.11721 — 64 halkalı gerçek çip,
  serbest taşıyıcı+termo-optik self-pulsing ile MNIST/F-MNIST belleği.
- (bilinen) Giron Castro et al. 2024b — TCMT sistem simülasyonu, FCD/termal
  etkileşiminin optimum NARMA-10 bölgesini belirlediği gösteriliyor.
- **(yeni)** Ren et al. 2024, *Photonic time-delayed reservoir computing
  based on series-coupled microring resonators*, Opt. Express 32(7):11202,
  DOI 10.1364/OE.518063 (tam metin arXiv:2308.15902 üzerinden okundu —
  aylardır erişilemeyen makale). TCMT modeli; nonlinearite kaynağı açıkça
  FCD/FCA (TPA yalnız taşıyıcı üretim yolu). En iyi NARMA-10 sonucu
  NMSE=0.154 — bizim hedefimizin (`<0.05`) ~3 katı üstünde, tek geçişlik
  ölçümle (kör-seed protokolü yok).
- **(yeni)** "Dynamic Analysis and Reservoir Computing of Nonlinear
  Microring Resonators" (Trento grubu, ACS Photonics, PMC12447551) —
  Jacobian-eigenvalue analiziyle, tek MRR'de self-pulsing/bellek
  kaynağının FCD+termal etkileşim olduğunu (Kerr değil) matematiksel
  olarak gösteriyor.
- **(yeni)** Lugnan et al. 2024, arXiv:2411.17272 (Adv. Optical Materials,
  DOI 10.1002/adom.202403133) — **bizim adayımızla neredeyse aynı
  geometride** (450×220 nm Si core, ~200 nm gap, add/drop, telecom bandı)
  gerçek bir 64-halkalı çip; mikrosaniye ölçekli bellek FCD+termo-optik
  etkileşimden geliyor, Kerr/TPA'nın kendi (sub-ns) gevşeme süresi bu
  ölçekte bellek üretemeyecek kadar hızlı.

**Sonuç**: Bu risk artık "kısmi nonlinear kanıt" notundan daha ciddiye
alınmalı. Kerr+TPA-only ilk koşu hâlâ mantıklı bir ilk adım (fizibilite/
maliyet kapısı için), ama sonucun NARMA-10'da anlamlı bellek göstermemesi
durumunda bunun "yanlış mimari" değil "eksik fizik" (FCD/FCA/termal
dahil edilmemiş) olabileceği açıkça göz önünde bulundurulmalı. FCD/FCA'yı
sonraki bir aşamaya eklemek, Tidy3D'de native değildir (FDTD'nin fs-adımlı
zaman eksenine serbest-taşıyıcı/termal ODE'leri (ns-µs ölçek) self-consistent
bağlayan bir yerleşik mekanizma yok) — özel kod (harici rate-equation
entegrasyonu + kısa Tidy3D koşularıyla kalibrasyon) gerektirir.

## CFL duvarı — Tidy3D içinde bedava çözüm yok

Aynı taramada, FDTD'nin femtosekond zaman adımını (CFL koşulu) gevşetecek
gerçek, yayınlanmış sayısal yöntemler bulundu (ADI+ADE unconditionally-stable
scheme, Faber-polinom yerel yayıcılar, vektörel zarf-Maxwell formülasyonu,
precise-integration zaman-domeni yöntemi) — ama **hiçbiri Tidy3D'nin kapalı,
patentli açık (explicit) Yee-hücre çözücüsüne eklenemez.** Bu yöntemleri
kullanmak Tidy3D'yi bırakıp özel/açık-kaynak bir FDTD koduna (örn. MEEP)
geçmeyi gerektirir. Bu, mevcut araç setinde CFL duvarının aşılamaz olduğu
sonucunu bağımsız olarak doğruluyor; bkz.
[[⚔️ 200-Goals/FDTD-Zaman-Adimi-Ozgurlugu]] (MayOS goal notu).

## Kerr+TPA maliyet kalibrasyon noktası

Tidy3D'nin resmi "2D Kerr ring" community notebook'u
(https://www.flexcompute.com/tidy3d/community/notebooks/2DKerr/) — yalnız
Kerr (TPA yok), 2D effective-index indirgemesi, 750 ps toplam süre için
**~50 FlexCredit** harcıyor. Bu, kendi tam-3D + Kerr+TPA + muhtemelen daha
uzun süreli koşumuzun **maliyet alt sınırı** olarak alınmalı — gerçek koşu
kesinlikle daha pahalı olacaktır. Şu ana kadarki toplam proje harcaması
(~30 FC, tüm lineer rung'lar dahil) bu tek toy-run'dan bile düşük; Kerr+TPA
aşaması açılmadan önce yazılı bir FC tavanı belirlenmeli.

## Bütçe-duyarlı kalibrasyon metodolojisi (opsiyonel, gelecek)

Sequential Bayesian Experimental Design / EIVAR (Surer & Williams,
arXiv:2305.16506) gibi aktif-öğrenme yöntemleri, Kerr+TPA parametrelerini
(n2, beta_TPA, coupling) az sayıda pahalı FDTD noktasıyla kalibre etmek için
uygulanabilir — Tidy3D'de native değil, harici Python (GP/Bayesian
optimizasyon) gerektirir, ama gelecekteki Kerr+TPA kalibrasyon kampanyası
için FlexCredit tasarrufu sağlayabilir. Mevcut mesh/zaman/PML yakınsama
sorunu için uygun değil (bu bir kalibrasyon-karşı-veri problemi değil,
yakınsama testi).
