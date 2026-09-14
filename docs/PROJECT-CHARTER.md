# Proje sözleşmesi

## Fiziksel kapsam

450×220 nm silicon kesit, merkez yarıçapı 4.775 µm, simetrik iki bus,
150–250 nm gap. Global surrogate, kesit/yarıçap/topoloji optimizasyonu ertelendi.
Zincir: kesit eigenmode → açık bus–ring kompleks S → round-trip → CW/CCW TCMT.
Geometri parametreleri full-wave kanıtından; malzeme/carrier/termal girdileri
kaynaklandırılmış veriden gelir. Bilinmeyenler NMSE'ye uydurulmaz.
Kayıpsız model kontrol modelidir. Intrinsic kayıp = radyasyon + absorpsiyon +
proses saçılması; ısı kaynağı yalnız absorbe edilen güçtür.

## Başarı ve durma kapıları

Başarı: kilitli 10 kör seed medyan NMSE <0.05 ve >=8/10 başarı.
Geliştirme: 5 seed; hash ve 200/3000/2000 split korunur.

Yürütme: [K0–K5 kurtarma ADR](decisions/2026-09-13-optical-chain-recovery-plan.md).
Kapsam dışı: global surrogate, yeni topoloji, fabricated-device kanıtı.
Durma: geçmeyen fizik/provenance kapısı, kaynaksız arama sınırı, bütçe veya solve onayı eksikliği.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/spiral-delay-reservoir/MayOS/Photonic-Reservoir|Önceki Photonic Reservoir hattı]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]

Uygulama arayüzleri, K2s/K2a ve B25: [ek sözleşme](decisions/2026-09-14-recovery-implementation-contract.md).

## Plan 2 kapsamı (2026-09-14)

[Plan 2 Kerr ADR](decisions/2026-09-14-plan2-kerr-reservoir.md) ayrı araştırma hattını tanımlar.
Eski silikon geometri kısıtları bu hatta uygulanmaz; eski sonuçlar korunur.
Plan 2: Si3N4/SiO2 ve AlGaAsOI adayları, 1550 nm, tek/iki halka,
10 mW ortalama / 100 mW tepe araştırma tavanı, 20 slot × 2 port = 40 özellik.
Kaynaklı keşif EM öncesi yapılabilir; fiziksel kabul/kör kilit için P6 kanıtı gerekir.
Ortak benchmark ve kör suite kopyalanmaz; hatlar arasında yalnız tek nihai kör aday.
Plan 2 için ek 47 FC tahsis edilmedi; bütçe, 20 FC rezerv ve B25 ortaktır.
Kod/test Claude; P0 teknik kabulü ve P1–P6 tamamlanmış değildir.
