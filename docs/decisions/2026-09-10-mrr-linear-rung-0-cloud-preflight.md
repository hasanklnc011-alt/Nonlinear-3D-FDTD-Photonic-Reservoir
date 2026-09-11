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

## Zaman-rung-2 (90 ps) sonucu: hâlâ eşik üstü, ama marjinal

Task `fdve-cc220e40-5154-42b4-9bb9-1ac7bad84846` `status=success`; gerçek
kullanım `realFlexUnit=5.177004813944414` (tahminle birebir aynı).

- Final field decay: `1.53e-05` — hedef `1e-5`'in yalnızca `~1.53×` üzerinde
  (rung-0c'nin `0.00355`'inden ve time-rung-1'in `0.000801`'inden büyük
  iyileşme). Tidy3D uyarısı: "Simulation final field decay value of 1.53e-05
  is greater than the simulation shutoff threshold of 1e-05."
- Through flux aralığı `0.2774–0.8984`; drop flux aralığı `-5.40e-05–0.2194`.

**Karar**: sözleşmedeki sert eşik (`< 1e-5`) hâlâ sağlanmadı; zaman
yakınsaması kapısı resmen kapalı kalır. Ancak açık, önceki rung'lara göre çok
küçüktür (80× → 1.53×). Hasan'a maliyet farkı sunuldu: 90 ps `5.177 FC` vs
105 ps tahmini `5.987 FC` (fark `~0.81 FC`, `%16`). Decay eğrisinin son iki
noktasından extrapolasyon 105 ps'de `~5.7e-6` bekliyor (hedefin altında).
Hasan 105 ps'yi onayladı.

## Zaman-rung-3 (105 ps) başlatıldı

Plan `manifests/fdtd/mrr-linear-001/time-rung-3.plan.json`
(`run_time_s = 1.05e-10`, diğer girdiler time-rung-2 ile aynı). Tahmin-amaçlı
upload + `estimate_cost`: task `fdve-5f199de8-272c-47e1-b6ce-2cf8822ff4e8`,
tahmini `5.986517149965992 FlexCredit`. Hasan onayı sonrası `web.start`
çağrıldı; `2026-09-11` itibarıyla durum `queued`. Tamamlanma ve gerçek
sonuç ayrı bir kayıtla eklenecek.

## Zaman-rung-3 (105 ps) sonucu: zaman yakınsaması GEÇTİ

Task `fdve-5f199de8-272c-47e1-b6ce-2cf8822ff4e8` `status=success`; gerçek
kullanım `realFlexUnit=5.394372833943262` (tahmin `5.987`'den düşük — solver
early-shutoff'a girdi).

- Çözücü log'u: field decay `%90` adımda (`9.46e-11 s ≈ 94.6 ps`)
  `7.05e-06`'ya indi; "Field decay smaller than shutoff factor, exiting
  solver." mesajıyla planlanan `105 ps`'den önce kendiliğinden durdu.
- **Final field decay: `7.05e-06 < 1e-5`** — hedef sağlandı.
- Through flux aralığı `0.2789–0.8995`; drop flux aralığı
  `-5.12e-05–0.2196` (rung-0c/time-rung-1/time-rung-2 ile tutarlı).

**Karar**: bu mesh/PML çözünürlüğünde **zaman yakınsaması kapısı geçti**.
Yakınsama merdiveni:

| Rung | run_time (hedef) | gerçek durma | final decay |
| --- | --- | --- | --- |
| rung-0c | 10 ps | 10 ps | `0.00355` |
| time-rung-1 | 30 ps | 30 ps | `0.000801` |
| time-rung-2 | 90 ps | 90 ps | `1.53e-05` |
| time-rung-3 | 105 ps | `~94.6 ps` (early shutoff) | `7.05e-06` ✅ |

## Açık kalan kapı: mesh/PML yakınsaması

`docs/PROJECT-CHARTER.md` başarı kapısı 3 "mesh, zaman **ve** PML
yakınsaması" der. Yalnız zaman ekseni kanıtlandı; mevcut mesh
(`AutoGrid 10 step/λ @ 1.55 µm`) ve PML (`12 katman`, tüm eksenlerde) hiçbir
refinman adımıyla karşılaştırılmadı. Sıradaki adım en az bir daha ince mesh
(örn. `14–16 step/λ`) ve/veya daha kalın PML rung'u; aynı gözlenebilir
(through/drop flux, rezonans merkezi) üzerinde tutarlılık karşılaştırılmadan
lineer kapı tam kapanmaz, Kerr+TPA aşaması açılmaz. Bu yeni bir ücretli
solve'dur; Hasan'ın açık onayı gerekir.

## PML-rung-1 (16 katman) maliyet tahmini ve başlatma

Mesh (`10→14` step/λ: tahmini `17.375 FC`; `10→16`: tahmini `24.774 FC`) ve
PML (`12→16` katman: tahmini `6.634 FC`) refinman seçenekleri için yalnız
`web.upload` + `web.estimate_cost` çağrıldı (ücretsiz, hiçbiri başlatılmadı).
Mesh refinman'ı çok daha pahalı çıktı (time-step sayısı ~1.3M'den ~1.8-2.1M'e
çıkıyor); PML refinman'ı görece ucuz. Hasan önce ucuz PML refinman'ını
başlatmayı onayladı.

Plan `manifests/fdtd/mrr-linear-001/pml-rung-1.plan.json`
(time-rung-3 girdileri + `boundary_spec.{x,y,z}.num_layers = 16`, diğer her
şey aynı). Task `fdve-384c5349-405a-4d47-bcac-9abbe459ef42`, tahmini
`6.633881588485531 FlexCredit`. `2026-09-11`'de `web.start` çağrıldı;
durum `queued`. Sonuç ayrı bir kayıtla eklenecek; through/drop flux ve
rezonans özelliklerinin `time-rung-3` (12 katman PML) ile tutarlı çıkıp
çıkmadığı kontrol edilecek.

## PML-rung-1 sonucu: PML yakınsaması GEÇTİ

Task `fdve-384c5349-405a-4d47-bcac-9abbe459ef42` `status=success`; gerçek
kullanım `realFlexUnit=5.977665166935861` (tahmin `6.634`'ten düşük, early
shutoff).

| | time-rung-3 (12 katman) | pml-rung-1 (16 katman) |
| --- | --- | --- |
| through flux | `0.2789–0.8995` | `0.2789–0.8995` |
| drop flux | `-5.12e-05 – 0.2196` | `-5.12e-05 – 0.2196` |
| final decay | `7.05e-06` | `6.93e-06` |
| durma zamanı | `~94.6 ps` | `~94.6 ps` |

PML katman sayısı `%33` artırıldığında (`12→16`) through/drop flux değerleri
6 hanede değişmedi; final decay pratikte aynı. Bu, mevcut `12` katmanlık
PML'nin sonuca yapay sınır-yansıması katmadığının doğrudan kanıtıdır.

**Karar: PML yakınsaması geçti.** Başarı kapısı 3'ün kalan tek parçası mesh
yakınsamasıdır (mevcut `AutoGrid 10 step/λ`).

## Mesh-rung-1 (12 step/λ) maliyet tahmini ve başlatma

Ucuz bir ilk mesh adımı için `10.7165 FlexCredit` tahmini çıkarıldı (yalnız
upload + `estimate_cost`, ücretsiz; task `fdve-3c712882-71d2-42b0-bf94-c09daf525f2c`).
14/16 step/λ seçenekleri (`17.375` / `24.774 FC`) ile karşılaştırıldı; Hasan
önce en ucuz adımı (`10→12`) denemeyi onayladı.

Plan `manifests/fdtd/mrr-linear-001/mesh-rung-1.plan.json` (time-rung-3
girdileri + `grid_spec.min_steps_per_wavelength = 12.0`, diğer her şey aynı,
`16` katmanlı PML'ye değil `12` katmanlı zaman-rung-3 tabanına göre —
mesh ve PML refinman'ları ayrı eksenlerde test ediliyor, birleştirilmiyor).
`2026-09-11`'de `web.start` çağrıldı; durum `queued`, `estFlexUnit =
10.71645727981614`. Sonuç ayrı bir kayıtla eklenecek.

## Mesh-rung-1 sonucu: mesh yakınsaması BAŞARISIZ, zaman/mesh eksenleri bağımlı

Task `fdve-3c712882-71d2-42b0-bf94-c09daf525f2c` `status=success`; gerçek
kullanım `realFlexUnit=10.71645727981614` (tahminle birebir aynı — bu
run 105 ps'nin tamamını kullandı, early shutoff olmadı).

| | time-rung-3 (10 step/λ, 105 ps hedef) | mesh-rung-1 (12 step/λ, 105 ps) |
| --- | --- | --- |
| through flux | `0.2789–0.8995` | `0.1092–0.8987` |
| drop flux | `-5.12e-05–0.2196` | `-5.69e-05–0.1265` |
| final decay | `7.05e-06` (`~94.6 ps`'de erken durdu) | `3.62e-05` (105 ps'nin tamamı, hedefin üstü) |

Through flux alt sınırı `~%61`, drop flux üst sınırı `~%43` değişti — bu
"yakınsadı" değil, **mesh'e hassas** bir sonuçtur. PML testinin aksine
(12→16 katman: değişim yok), burada gerçek bir mesh bağımlılığı var.

**Kök neden (yorum, sonraki rung'la doğrulanacak)**: 10 step/λ'daki kaba
mesh halkanın eğri kenarını basamaklı yaklaşıklıyor; bu yapay saçılma/kayıp
alanın gerçekte olduğundan daha hızlı sönmesine yol açıyor gibi görünüyor.
Mesh inceldikçe bu yapay kayıp azalıyor, gerçek foton yaşam süresi (Q) daha
uzun çıkıyor, aynı run_time (105 ps) decay hedefine yetmiyor. Yani **zaman
ve mesh yakınsaması bağımsız eksenler değil**; önceki "zaman yakınsadı"
sonucu yalnız o kaba mesh için geçerliydi.

**Karar**: mesh yakınsaması kapısı açık kalır; mesh-rung-1 sonucu (105 ps'de
yetersiz zaman yakınsamasıyla) doğrudan time-rung-3 ile adil kıyaslanamaz.
Aynı mesh'te (12 step/λ) run_time'ı uzatıp önce zaman yakınsamasını
sağlamak, sonra o yakınsamış flux değerlerini time-rung-3 ile kıyaslamak
gerekir.

## Mesh-rung-2 (12 step/λ, 150 ps) maliyet tahmini ve başlatma

Mesh-rung-1'in log'undaki son decay eğiliminden (`96%→100%`:
`4.24e-05→3.62e-05`) extrapolasyon: `1e-5` hedefine ulaşmak için tahmini
toplam run_time `~135–140 ps`. 150 ps (`14.5508 FC`, task
`fdve-b2b294bc-e886-4f84-adcc-4430d5a24a0e`) ve 180 ps (`16.8847 FC`, task
`fdve-e6584722-f472-4fbf-a4cd-b27752576854`) için yalnız upload +
`estimate_cost` (ücretsiz) çağrıldı. Hasan 150 ps'yi onayladı.

Plan `manifests/fdtd/mrr-linear-001/mesh-rung-2.plan.json` (mesh-rung-1
girdileri + `run_time_s = 1.5e-10`). `2026-09-11`'de `web.start` çağrıldı;
durum `queued`, `estFlexUnit = 14.550799839495676`. Sonuç ayrı bir kayıtla
eklenecek; bu run'daki final decay `1e-5`'in altına inerse elde edilen
flux değerleri time-rung-3 (10 step/λ) ile adil biçimde kıyaslanacak.
