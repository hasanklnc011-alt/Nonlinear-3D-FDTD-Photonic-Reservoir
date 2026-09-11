# MRR lineer rung-0 cloud ön kontrolü

- Tarih: 2026-09-10
- Karar sahibi: Astra/Codex
- Durum: Tamamlandı; fiziksel kabul kapısında reddedildi

## Amaç ve sınır

İlk ücretli çalışma yalnız lineer telecom-Si MRR rezonans taraması ve
mesh/zaman/PML ladder'ının ilk rung'udur. Bu sonuç nonlinear kabul değildir;
Kerr/TPA/FCA/FCD eklenmemiştir.

## Sabitlenen girdiler

- Input bundle: `manifests/fdtd/mrr-linear-001/rung-0.input.json`
- Malzeme snapshot SHA-256: `895de5028883be32ac3475508c66388c3900dc9f05330aaa8502513f54380ac7`
- Geometri SHA-256: `6844d49cf1585fc4df1c23ad8e60c2a9771f4a13d1df97e6408099ca0187147e`
- Config SHA-256: `b9b83892796763feb67930277afad9a67a486d3201e7a8e3f2955a0b8b184035`
- Lineer plan SHA-256: `7989baa39e1f685fb101472f5a8fc78041d9ea0ba5fd52d5828c50de16be35f4`
- Yerel Tidy3D Simulation SHA-256: `4d17633d3393e0b0a6ad8c08b4bb5b03d5307d8acbdd22eefa2b54c865674f05` (`tidy3d 2.12.0`)
- Dar-bant malzeme proxy: `cSi/Li1993_293K` ve `SiO2/Palik_LowLoss`, 1.50–1.60 µm'de 1.55 µm n², kayıpsız/non-dispersive ilk rung yaklaşımı.
- Geometri: 5.0 µm dış yarıçap, 450×220 nm Si ring/bus, 200 nm gap, add/drop; domain 18.0×13.3×6.22 µm.
- Rung-0: AutoGrid 10 step/λ @ 1.55 µm; 12 katman PML (x/y/z); 10 ps run-time; shutoff `1e-5`; 201 frekans noktası.

## Cloud kaydı ve maliyet

- Upload task ID: `fdve-7a16b155-f684-4bae-91ea-c1dd59877758`
- Tidy3D `estimate_cost`: **0.6261476005924334 FlexCredit** (tam run-time için üst tahmin; early shutoff gerçek maliyeti düşürebilir).
- Onaylı ilk rung bütçe tavanı: **0.70 FlexCredit**.
- Başlatma kanıtı: `web.start` başarılı; task bilgisi `status=queued`, `nodeSize=16240098`, `timeSteps=123924`, `solverVersion=release-26.3.3`, `realCost` henüz boş döndü.
- Tamamlanma kanıtı: `status=success`; bildirilen gerçek kullanım `realFlexUnit=0.06261476005924334` (Tidy3D yanıtındaki `realCost` boş kaldı).

## Yakınsama ve fail-closed kuralı

Rung-0 yalnız başlangıç ölçümüdür. Rezonans merkezi, through/drop iletimi ve
field-decay tamamlanması kaydedilir. Yakınsama yoksa veya sonuç sonlu değilse
nonlinear aşamaya geçilmez; önce zaman/mesh/PML için yerel teşhis ve sonraki
rung tasarlanır. Rung-0 kabul edilse bile en az iki rafinman basamağı aynı
gözlenebilir üzerinde karşılaştırılmadan lineer kapı kapanmaz.

## Rung-0 sonucu: fail-closed

İki flux monitörü 201 frekans noktasının tamamında sayısal olarak aynı çıktı:
`min=0.9516270756721497`, `max=0.9540104269981384`. Plan denetimi bunun fiziksel
bir sonuç olmadığını gösterdi: hem through hem drop monitor düzlemi `x=8, y=0`
olarak üretilmişti; drop bus'ın gerçek `y` konumu kullanılmamıştı. Bu nedenle
rezonans/near-sama yorumu yapılmayacak ve nonlinear aşamaya geçilmeyecek.

Sonraki işlem yalnız yerel translator düzeltmesidir: source/monitor düzlemi,
token içindeki bus adına göre ilgili yapı merkezinin enine koordinatını taşımalı;
regresyon testi iki bus için farklı y koordinatını zorunlu kılmalıdır. Düzeltilmiş
plan yeni digest ve maliyet tahminiyle yeniden gönderilir.

## Port düzeltmeli tekrar (rung-0b)

Claude'un port-merkez regresyonu `59/59` yerel testle geçti; tam yerel suite
Claude tarafından `223/223` raporlandı. Yeni plan SHA-256
`3e3a7c78d32447f8c61fbba9bd2b10f376c9c366faf87a294a21b48d2227da02`, yeni
Simulation SHA-256 `882ba3c70df96b41a01671b2936f724d49b0b55ba3c94c2b4f62294f3457fe66`.
Through/drop monitor merkezleri sırasıyla `[8.0, -5.425, 2.61]` ve
`[8.0, 5.425, 2.61]` olarak yerelde doğrulandı.

Upload task ID `fdve-ecd696f8-0313-4f15-93ff-93653a162934`; Tidy3D tahmini
**0.6179888739008371 FlexCredit**. Aynı 0.70 FlexCredit rung tavanı içinde;
bu kayıt tamamlandıktan sonra solve başlatılabilir.

## Rung-0b sonucu: port merkezi düzeldi, fizik kapısı hâlâ kapalı

Task `fdve-ecd696f8-0313-4f15-93ff-93653a162934` başarıyla tamamlandı; bildirilen
gerçek kullanım `realFlexUnit=0.06179888739008371`. Through ve drop akıları artık
farklı (`0.9631–0.9658` ve `0.2785–0.2823`), dolayısıyla önceki eş-merkez hatası
giderildi. Ancak 1.50–1.60 µm bandında beklenen MRR rezonans özelliği görünmedi.

Bu rung, kaynak/monitör düzlemlerinin tüm domain kesitini kapsaması nedeniyle
rezonans/near-sama için kabul edilmez. Sonraki düşük-riskli yerel düzeltme,
düzlem boyutlarını token'ın named bus kesitinden türetmektir: enjeksiyon ekseni
sıfır, enine genişlik `bus_width + 2*domain_padding`, dikey yükseklik
`waveguide_thickness + 2*domain_padding`; merkez ilgili bus merkezidir. Yeni
plan, digest ve cost estimate olmadan üçüncü ücretli solve başlatılmaz.

## Rung-0c cloud kaydı

Dar named-bus plane regresyonu 68/68 geçti. Plan SHA-256:
`c2be038104d71703425a775655d0e461e7cdf9ca960cfb91d8225cbfe99f5dc6`.
Upload task: `fdve-91f511a1-4ba8-4ce0-a034-7592d1e401d5`; tahmin:
**0.6055170401765696 FlexCredit**, 0.70 tavanının altında. Başlatma yetkilidir.

Rung-0c tamamlandı; gerçek kullanım `0.6055170401765696` FlexCredit. Through
akı `0.3512–0.9701`, drop akı `-8.57e-05–0.1102` ile rezonans özelliği görünür;
ancak final field decay `0.00355 > 1e-5`. Bu nedenle yakınsama kabul edilmedi.
Sıradaki yalnız zaman-rung'u daha uzun run-time kullanmalıdır; nonlinear kapısı kapalıdır.

## Zaman-rung-1 cloud kaydı

Run-time 10 ps'den 30 ps'ye çıkarıldı; diğer rung-0c girdileri sabit. Plan SHA-256
`55697392e50e681094b360afb0dab317009109f172600748e43737eda84eb6cf`.
Upload task `fdve-3d860c65-eda0-4664-936c-0b6efe00ce9d`; Tidy3D tahmini
**1.7888406191711748 FlexCredit**. Amaç yalnız field-decay zaman yakınsamasıdır.

## Zaman-rung-1 sonucu: tamamlandı, zaman yakınsaması hâlâ geçmedi

Task `fdve-3d860c65-eda0-4664-936c-0b6efe00ce9d` `status=success`; gerçek kullanım
`realFlexUnit=1.7888406191711748` (tahminle birebir aynı). Claude Sonnet 5,
2026-09-11 oturumunda (Astra geçici devre dışıyken) sonucu indirip inceledi.

- Final field decay: `0.000801` (rung-0c'deki `0.00355`'ten ~4.4× iyileşme),
  hâlâ shutoff eşiği `1e-5`'in ~80× üzerinde. Tidy3D'nin kendi uyarısı:
  "Simulation final field decay value of 0.000801 is greater than the
  simulation shutoff threshold of 1e-05. Consider running the simulation
  again with a larger 'run_time' duration."
- Through flux aralığı `0.2610–0.9034`; drop flux aralığı `-6.75e-05–0.1928`.
  Through/drop ayrımı fiziksel olarak makul görünür, ama field-decay
  yakınsamadan bu sayılara güvenilmez.

**Karar: zaman yakınsaması kapısı hâlâ kapalı.** `const.md` / `docs/PROJECT-CHARTER.md`
başarı kapısı 3 (mesh/zaman/PML yakınsaması) sağlanmadı; Kerr+TPA nonlinear
aşamasına geçilmez.

Sıradaki tek adım: run_time'ı daha da artırıp (örn. 60–90 ps) yeni bir
zaman-rung'u tasarlamak. Bu yeni bir ücretli solve'dur; Hasan'ın açık onayı
olmadan başlatılmayacak.

## Zaman-rung-2 maliyet tahmini ve başlatma (Hasan onayı, 2026-09-11)

Decay eğrisi (rung-0c 10 ps → `0.00355`; time-rung-1 30 ps → `0.000801`) üstel
extrapole edildi: `1e-5` hedefine ulaşmak için tahmini toplam run_time
`~85–90 ps`. Üç seçenek için sadece `web.upload` + `web.estimate_cost`
çağrıldı (ücretsiz, solve başlatılmadı):

- 60 ps → tahmini `3.5131 FlexCredit` (task `fdve-9123f8f0-156a-4e2a-b004-0ec47638e672`, başlatılmadı)
- 75 ps → tahmini `4.3526 FlexCredit` (task `fdve-43d3c750-48ce-4165-91e9-793b663453c9`, başlatılmadı)
- 90 ps → tahmini `5.1770 FlexCredit` (task `fdve-cc220e40-5154-42b4-9bb9-1ac7bad84846`)

Hasan **90 ps** seçeneğini onayladı ve başlatılmasını istedi. Plan
`manifests/fdtd/mrr-linear-001/time-rung-2.plan.json` olarak kaydedildi
(`run_time_s = 9e-11`, diğer tüm girdiler time-rung-1 ile aynı). `web.start`
çağrıldı; `2026-09-11` itibarıyla task durumu `queued`, `estFlexUnit =
5.177004813944414`. Tamamlanma ve gerçek maliyet ayrı bir kayıtla eklenecek.

Not: 60 ps ve 75 ps için oluşturulan tahmin-amaçlı task'lar (`fdve-9123f8f0...`,
`fdve-43d3c750...`) başlatılmadı; bunlar yalnız maliyet karşılaştırması için
upload edildi.
