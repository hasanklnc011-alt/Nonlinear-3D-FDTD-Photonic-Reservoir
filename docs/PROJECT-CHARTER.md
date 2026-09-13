# Proje sözleşmesi



450×220 nm silicon kesit, merkez yarıçapı 4.775 µm, simetrik iki bus,
150–250 nm gap. Global surrogate, kesit/yarıçap/topoloji optimizasyonu ertelendi.
Zincir: kesit eigenmode → açık bus–ring kompleks S → round-trip → CW/CCW TCMT.
Geometri parametreleri full-wave kanıtından; malzeme/carrier/termal girdileri
kaynaklandırılmış veriden gelir. Bilinmeyenler NMSE'ye uydurulmaz.
Kayıpsız model kontrol modelidir. Intrinsic kayıp = radyasyon + absorpsiyon +
proses saçılması; ısı kaynağı yalnız absorbe edilen güçtür.


Başarı: kilitli 10 kör seed medyan NMSE <0.05 ve >=8/10 başarı.
Geliştirme: 5 seed; hash ve 200/3000/2000 split korunur.

Yürütme: [K0–K5 kurtarma ADR](decisions/2026-09-13-optical-chain-recovery-plan.md).
Kapsam dışı: global surrogate, yeni topoloji, fabricated-device kanıtı.
Durma: geçmeyen fizik/provenance kapısı, kaynaksız arama sınırı, bütçe veya solve onayı eksikliği.

## Araştırma hattı bağlantıları

- [[🏰 300-Projects/Photonic-Reservoir/spiral-delay-reservoir/MayOS/Photonic-Reservoir|Önceki Photonic Reservoir hattı]]
- [[🧠 500-Knowledge/concepts/Photonic-Research-Lines-Synthesis|Fotonik araştırma hatları sentezi]]
