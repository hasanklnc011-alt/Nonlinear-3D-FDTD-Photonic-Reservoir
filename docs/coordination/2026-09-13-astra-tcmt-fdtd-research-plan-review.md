# Astra taslağı — geometriyle sınırlandırılmış TCMT/FDTD araştırma planı

- Tarih: 2026-09-13
- Hazırlayan: Astra/Codex
- İnceleyen: Claude Sonnet 5
- Durum: DRAFT — REVIEW REQUESTED
- Kapsam: Araştırma yönü ve kanıt zinciri
- Sözleşme etkisi: Bu belge `AGENTS.md`, `CLAUDE.md`, `const.md` veya kilitli
  NARMA-10 benchmarkını değiştirmez. Değişiklik ancak ayrı bir karar kaydı ve
  Hasan'ın kabulüyle yapılabilir.

## İnceleme isteği

Claude bu taslağı canlı depo ve mevcut FDTD sonuçlarına karşı incelemeli.
Özellikle şunları raporlamalı:

1. Araştırma sorusunun bilimsel olarak sınanabilir olup olmadığı.
2. Mevcut kodun hangi bölümlerinin yeniden kullanılabileceği.
3. TCMT modelinde eksik fizik, observability veya benchmark sızıntısı riski.
4. FDTD'den çıkarılması önerilen büyüklüklerin mevcut monitor verileriyle
   gerçekten tanımlanabilir olup olmadığı.
5. İş paketlerinin bağımlılık sırası ve ücretsiz ilk adım.
6. Taslağın kabul, revizyon veya reddedilme gerekçesi.

Claude bu inceleme tamamlanmadan mimariyi, benchmarkı veya kanıt sözleşmesini
değiştirmemeli ve yeni ücretli Tidy3D solve başlatmamalıdır.

## Aday araştırma sorusu

> TCMT'de iyi NARMA-10 sonucu veren MRR parametrelerinin hangileri gerçek bir
> silikon geometrisinde birlikte gerçekleştirilebilir ve bu başarı geometri,
> malzeme ve üretim belirsizlikleri altında korunur mu?

Bu sorunun literatürde tamamen özgün olduğu henüz kanıtlanmış değildir.
Özgünlük iddiasından önce geometriyle sınırlandırılmış photonic reservoir
optimization, full-wave-calibrated TCMT ve fabrication-aware MRR reservoir
çalışmaları için odaklı bir tarama gerekir.

## Aday bilimsel katkılar

### C1 — Geometriyle sınırlandırılmış performans

TCMT'deki `Q_i`, `Q_e`, bus-ring coupling, rezonans ve effective mode volume
bağımsız serbest değişkenler gibi optimize edilmez. Aynı geometri değişikliğinin
bu büyüklüklerde oluşturduğu bağlı değişim korunur. Böylece ideal modelde iyi
görünen parametre kümesi ile elektromanyetik olarak gerçekleştirilebilir cihaz
arasındaki fark ölçülür.

### C2 — Bellek ve nonlinearity mekanizmalarının ayrıştırılması

Aynı dataset, split, mask, readout özellikleri ve eğitim protokolü altında şu
kontroller karşılaştırılır:

- input-only ve photodiode-only baseline;
- lineer MRR + square-law photodiode;
- photon-lifetime state;
- free-carrier state;
- carrier + thermal state;
- varsa explicit optik delay veya seri-halka belleği;
- tam aday model.

Amaç, düşük NMSE'nin halka dinamiğinden mi, fotodiyot karesinden mi, explicit
delay'den mi veya readout'a verilen geçmiş örneklerden mi geldiğini belirlemektir.

### C3 — Dayanıklı çalışma bölgesi

Tek bir optimum yerine, aşağıdaki belirsizlikler altında kilitli geliştirme
protokolünde kararlı kalan bir çalışma bölgesi aranır:

- gap, waveguide width/thickness ve rezonans kayması;
- intrinsic loss ve backscattering;
- `tau_FC` ve `tau_th`;
- `n2`, TPA/FCA/FCD katsayıları ve thermal overlap;
- giriş gücü, detuning ve detector noise.

Kör seed'ler aday seçimine veya hyperparameter tuning'e geri beslenmez.

## Önerilen kanıt zinciri

```text
Kaynaklı TCMT/rate-equation modeli ve parametre aralıkları
        ↓
Geliştirme seed'lerinde hedef çalışma bölgesi ve mekanizma ablation'ları
        ↓
Gerekli optik parametre zarfı: Q_i, Q_e, coupling, mode overlap, loss
        ↓
Eigenmode/EME/3B FDTD ile gerçekleştirilebilir geometri bölgesi
        ↓
Fiziksel kısıtlar TCMT'ye geri bağlanarak yeniden optimizasyon
        ↓
Belirsizlik ve tolerans analizi
        ↓
Aday/config/source kilidi
        ↓
10 kör seed üzerinde nihai NARMA-10 değerlendirmesi
```

## FDTD'nin rolü ve sınırı

FDTD/eigenmode/EME şu optik sorulara cevap verir:

- rezonans frekansı ve spektral tepki;
- loaded response ile uygun port modeli kurulduğunda `Q_i/Q_e` ayrımı;
- bus-ring coupling ve gap duyarlılığı;
- mode profile, mode volume ve nonlinear overlap integralleri;
- ideal geometride radyasyon, bend ve tanımlı malzeme kayıpları;
- parazitik modlar ve modellenmiş backscattering/disorder etkileri.

FDTD aşağıdaki büyüklükleri tek başına üretmez:

- ölçülmüş `n2`, TPA, FCA/FCD katsayıları;
- carrier ve thermal lifetime;
- gerçek sidewall roughness ve üretim dağılımı;
- fabricated-device kabulü.

Bu girdiler kaynaklı aralık, ayrı carrier/thermal model veya ileride deneysel
fit gerektirir. Uzun NARMA-10 dizisinin femtosaniyelik Maxwell adımlarıyla
uçtan uca çözülmesi bu taslağın önerdiği ana hesaplama yolu değildir.

## İş paketleri ve bağımlılıkları

### WP0 — Mevcut FDTD kapısını kapat

Başlatılmış mesh-rung-2 sonucunu indir ve mevcut kabul ölçütleriyle değerlendir.
Bu sonuç tamamlanmadan yeni ücretli mesh veya nonlinear rung açılmaz. Sonuç,
mevcut geometrinin lineer spektral yakınsama kaydı olarak korunur.

### WP1 — Literatür ve model sözleşmesi

Giron Castro, Dong, Ren, Bazzanella/Donati ve ilgili kaynaklardan denklemleri,
birimleri, parametre provenance'ını ve raporlanan aralıkları çıkar. TCMT port
normalizasyonu ve `s_out = C s_in + D a` observability modeli açıkça yazılır.

Çıkış: kaynak-hash'li parametre tablosu, denklem sözleşmesi ve test edilebilir
baseline listesi.

### WP2 — Carrier-thermal TCMT hedef-bölge taraması

Kilitli benchmark uygulaması değiştirilmeden yalnız geliştirme seed'leriyle
`Q_i/Q_e`, coupling, güç, detuning, `tau_FC`, `tau_th` ve mimari bellek
parametreleri taranır. Arama değişkenleri fiziksel ve readout değişkenleri diye
ayrılır.

Çıkış: `NMSE < 0.05` için gereken optik/fiziksel zarf veya fail-closed biçimde
böyle bir zarf bulunamadığı sonucu.

### WP3 — Mekanizma ablation'ları

WP2'deki aday bölgede C2 kontrolleri ortak split ve eşit readout-feature bütçesi
ile çalıştırılır. Her mekanizmanın marjinal katkısı ve etkileşimi raporlanır.

Çıkış: bellek/nonlinearity attribution tablosu ve yanlış başarı kaynaklarını
eleyen kontroller.

### WP4 — Geometriye geri eşleme

Yalnız WP2'de gereken optik zarf için geometri taranır. Önce ücretsiz/ucuz
eigenmode veya EME kontrolleri, ardından gerekli en az sayıda yakınsamış 3B
FDTD doğrulaması seçilir. FDTD koşu sayısı önceden sabitlenmez; observable
yakınsaması ve hedef zarf kapsamı belirler.

Çıkış: geometri → optik parametre surrogate/tablosu ve erişilebilirlik hükmü.

### WP5 — Belirsizlik ve tolerans

Geometri ve malzeme belirsizlikleri birlikte örneklenir. Nominal optimumun yanı
sıra median/worst-case performans, başarısızlık olasılığı ve hassasiyet sırası
raporlanır.

Çıkış: tek nokta yerine dayanıklı çalışma bölgesi veya fail-closed sonuç.

### WP6 — Aday kilidi ve kör değerlendirme

Kaynak, config, model ve benchmark hash'leri kilitlenir. Mevcut 10 kör seed
protokolü yalnız bir kez ve tuning'e geri beslenmeden çalıştırılır.

## Taslak kabul ölçütleri

Planın uygulamaya alınması için Claude incelemesi ve sonraki merkezî karar şu
noktaları kapatmalıdır:

- odaklı tarama sonrası katkının literatür boşluğu olarak savunulabilmesi;
- TCMT denklemlerinin birim ve enerji normalizasyonunun doğrulanması;
- input/PD/readout-memory baselinelarının tanımlanması;
- FDTD observable'larının TCMT parametrelerine tanımlanabilir eşlemesi;
- kör benchmark kilidinin değişmemesi;
- yeni ücretli solve öncesi ayrı maliyet ve bilgi-değeri kararı.

## Açık karar

Bu plan kabul edilirse `const.md` içindeki “nihai elektromanyetik çözüm Tidy3D
ile uçtan uca 3D FDTD olmalıdır” ve “TCMT yalnız yardımcı kanıttır” hükümleri
ayrı bir ADR ile yeniden değerlendirilmelidir. Taslak aşamasında bu sabitler
yürürlüktedir.

