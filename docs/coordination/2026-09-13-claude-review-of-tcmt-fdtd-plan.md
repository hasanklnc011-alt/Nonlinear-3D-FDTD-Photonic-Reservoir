# 2026-09-13 — Claude'un TCMT/FDTD araştırma planı incelemesi

- İnceleyen: Claude Opus 5
- İncelenen: `docs/coordination/2026-09-13-astra-tcmt-fdtd-research-plan-review.md`
- Hüküm: **REVİZYONLA KABUL** — bir tanesi bloke edici altı revizyon şartıyla
- Maliyet: 0 FlexCredit (inceleme tamamen yerel)

Taslak altı maddelik bir inceleme istiyordu. Aşağıda sırayla cevaplanıyor.
Cevapların çoğu artık fikir değil ölçüm: bu oturumda üç ücretli koşu ve iki
ücretsiz test yapıldı, hepsi `docs/decisions/` altında kayıtlı.

---

## 1. Araştırma sorusu bilimsel olarak sınanabilir mi?

**Büyük ölçüde evet, bir parçası hayır.**

Soru şuydu: *TCMT'de iyi NARMA-10 veren MRR parametreleri gerçek bir silikon
geometride birlikte gerçekleştirilebilir mi ve belirsizlik altında korunur mu?*

Sınanabilir kısım, artık **kanıtlanmış** biçimde sınanabilir. Taslak yazıldığında
"geometri → optik parametre" eşlemesinin ölçülebilirliği varsayımdı; bu oturumda
gerçekten ölçüldü (bkz. madde 4). Yani sorunun birinci yarısı somut sayı üretiyor.

Sınanamayan kısım **C3'ün kendisi**: "dayanıklı çalışma bölgesi" tanımsız.
Taslak belirsizlik eksenlerini sayıyor ama **hangi metrikle** dayanıklı sayılacağını
söylemiyor. Metrik önceden sabitlenmezse sonuç post-hoc seçilebilir hale gelir ve
bu, kilitli kör-seed protokolünün korumaya çalıştığı şeyin ta kendisidir.

> **R2 (revizyon):** C3 için metrik önceden yazılmalı. Öneri: belirsizlik
> örneklerinde *medyan* test NMSE, *en kötü %10* NMSE ve `NMSE < 0.05`'i
> sağlama olasılığı; üçü birden, örnek sayısı ve dağılımlar önceden sabit.

Ayrıca taslak özgünlük iddiasını dürüstçe askıya alıyor ("henüz kanıtlanmış
değildir"). Bu doğru tutum; madde 6'daki kabul koşullarında korunmalı.

---

## 2. Mevcut kodun hangi bölümleri yeniden kullanılabilir?

**Altyapının tamamı; fiziğin hiçbiri — çünkü fizik kodu henüz yok.**

Yeniden kullanılabilir:

| modül | durum | plandaki yeri |
|---|---|---|
| `fdtd/provenance/` | fail-closed doğrulayıcı, hash kilidi | her WP'nin kanıt kapısı |
| `fdtd/mrr/geometry.py` | schema `/1` + `/2`, parametrik | WP4 geometri taraması |
| `fdtd/mrr/linear_sim.py` | bundle → plan çevirici, port token'ları | WP4 |
| `fdtd/tidy3d_build/linear_build.py` | plan → `tidy3d.Simulation`, monitör başına tarak | WP4 |
| `benchmarks/narma10_np/` | kilitli benchmark, manifest, kör-seed protokolü | WP6 |
| `tests/` | 286 test | hepsi |

**Boşluk, taslağın hafife aldığı yerde:** depoda **hiç TCMT/rate-equation modeli
yok**. WP2 ve WP3'ün tamamı sıfırdan yazılacak — durum değişkenleri, port
normalizasyonu, carrier/termal ODE'ler, readout, eğitim, ablation koşum düzeni.
Benchmark paketi var ama **fiziksel bir modelden benchmark'a giden hiçbir kod
yolu yok**. Yani "mevcut kodun yeniden kullanımı" altyapı anlamına gelir, iş
tasarrufu anlamına gelmez.

---

## 3. Eksik fizik, observability veya benchmark sızıntısı riski

### Eksik fizik — taslak doğru kapsıyor

C2'nin ablation listesi (photon-lifetime, free-carrier, carrier+thermal) zaten
altı kaynağın işaret ettiği FCD/FCA+termal mekanizmasını içeriyor
(`reports/FDTD-001-mrr-feasibility.md`). Burada ekleyecek bir eksik görmüyorum.

### Observability — taslak doğru sezmiş, ama modeli eksik

Taslak `s_out = C s_in + D a` yazılmasını istiyor. Bu oturum **neden** gerektiğini
pahalı biçimde gösterdi: üç ayrı observability kusuru bulundu ve üçü de
ölçümleri bozuyordu (frekans tarağı, port yerleşimi, facet sonlandırması).

Ama tek-modlu bir port modeli **yetmez**. `freq-rung-2`'de girişin `%9.7`'si
add portundan çıkıyor (`T_add = 0.09691`, drop'un `%15`'i) — bu, halkada CW ve
CCW modlarını birbirine bağlayan geri saçılmanın doğrudan ölçümü ve
`freq-rung-1`'deki `46 pm` mod yarılmasıyla tutarlı. Tek-modlu TCMT'de bu kanal
yoktur ve onu "kayıp" hanesine yazar; sonuç olarak `Q_i` tek sayı olarak
çıkarılamıyor, `4.9e4 – 7.1e4` aralığında kalıyor.

> **R1 (revizyon):** WP1'in port sözleşmesi **iki modlu (CW + CCW) ve geri
> saçılma katsayılı** olmalı. Bu, ölçülmüş bir gerekliliktir, teorik bir incelik
> değil. Aksi halde WP4'ün üreteceği `Q_i` belirsiz kalır ve C1'in tam da
> ölçmek istediği "ideal model ile gerçekleştirilebilir cihaz farkı" bulanıklaşır.

### Benchmark sızıntısı — bir kontrol eksik

C2 kontrolleri iyi ve "readout'a verilen geçmiş örnekler"i şüpheli olarak
sayıyor. Ama tap sayısı serbest bırakılırsa, lineer MRR + kare-yasası fotodiyot
bile yeterli gecikmeli tap'la NARMA-10'un büyük kısmını çözer; o zaman ölçülen
şey halka değil readout olur.

> **R5 (revizyon):** Gecikmeli tap sayısı **önceden** sabitlenmeli ve ayrıca
> "yalnız readout, rezervuar yok" baseline'ı NMSE-vs-tap eğrisiyle raporlanmalı.
> Washout uzunluğu ve train/val/test bölünmesi de aynı şekilde önceden yazılmalı.

---

## 4. FDTD büyüklükleri mevcut monitor verisiyle tanımlanabilir mi?

**Artık evet — ama üç düzeltmeden sonra. Taslak yazıldığında cevap hayırdı.**

Ölçülenler (`docs/decisions/2026-09-13-freq-rung-2-evaluation.md`):

```
lambda_0     = 1.540945 um
Q_loaded     =  9 797
Q_e (toplam) = 12 260        Q_c (tek coupler) = 24 519
x            = 0.799  -> belirgin OVER-coupled
n_eff        = 2.4017        cekirdek guc %60-63 (mode solver, 0 FC)
```

Bunlar WP4'ün istediği geometri → optik parametre eşlemesinin çekirdeğidir.

Gereken üç düzeltme, hepsi bu oturumda bulundu:

1. Frekans tarağı `0.5 nm` → `10 pm`. Öncesinde rezonans **tek örnekten**
   ibaretti, genlik ölçülemiyordu.
2. Drop monitörü yanlış uçtaydı — ölçtüğümüz şey ADD portuydu (`0.134`),
   gerçek drop `0.639`.
3. Bus facet'leri Fabry-Pérot kavitesi kuruyordu; baseline `%39` tepe-tepe
   salınıyordu. Facet'ler PML'e taşınınca `%0.1`'e düştü.

Tanımlanamayan:

- **`Q_i` tek sayı olarak** — R1 çözülene kadar aralık.
- **Mesh yakınsaması** — `freq-rung-3` (14 step/λ) şu an çalışıyor. Not: eski
  `10 → 12 step/λ` "+1.5 nm kayma" bulgusu üç kusurun üçünü de içeren veriden
  geliyordu; o kanıt geçersiz sayılmalıdır.
- Taslağın zaten doğru biçimde FDTD dışı saydıkları (`n2`, TPA, FCA/FCD
  katsayıları, carrier/termal ömürler, sidewall roughness) — bu ayrım isabetli.

> **R6 (revizyon):** Her ileri FDTD rung'u, sonucu kabul etmeden önce bir
> **enerji dengesi kapısından** geçmeli: rezonans dışı tüm portların toplamı
> `1.0`'a `1e-3` içinde. Bu oturumda bu tek test üç kusuru da yakalardı ve
> `~34 FC`'lik üç koşuyu gereksiz kılardı.

---

## 5. İş paketlerinin bağımlılık sırası ve ücretsiz ilk adım

Taslağın sırası **ekonomik olarak doğru** ve bunu açıkça yazıyor: WP4'te
"yalnız WP2'de gereken optik zarf için geometri taranır". Bu, pahalı FDTD'yi
ucuz TCMT taramasının sonucuna bağlıyor. Katılıyorum.

Vurgulanması gereken, taslakta örtük kalan nokta: **WP2 ve WP3'ün FlexCredit
maliyeti sıfırdır.** Tamamen yerel hesap. Para yalnız WP0 ve WP4'te harcanır.

> **R3 (revizyon):** Her WP'nin yanına FlexCredit bütçesi yazılmalı —
> WP1/WP2/WP3/WP5 `0 FC`, WP0 ve WP4 için tavanlı tahmin. Böylece "ne kadar iş
> parasız yapılabilir" görünür olur.

**Ücretsiz ilk adım (öneri):** R1'deki iki modlu port sözleşmesi + tek-halka
TCMT çekirdeği ve ablation koşum düzeni. Bu, hem WP1'i kapatır, hem WP2'yi açar,
hem de `Q_i` aralığını daraltacak modeli üretir. Hiç kredi harcamaz.

**Dürüst not:** Bu oturumda WP0'a **`60.96 FC`** harcandı (`freq-rung-3` ile
`~78 FC` olacak) ve depoda hâlâ tek satır TCMT kodu yok. Harcama savunulabilir —
devralınan açık bir yakınsama kapısıydı ve üç gerçek ölçüm kusuru buldu — ama
taslağın ekonomik mantığı (önce ucuz taramayı yap) fiilen tersine işletildi.
Bundan sonraki sıralamada buna dikkat edilmeli. Defter:
`reports/FLEXCREDIT-LEDGER.md`.

---

## 6. Kabul, revizyon veya red gerekçesi

**REVİZYONLA KABUL.** Taslağın bilimsel omurgası sağlam: soru sınanabilir,
kanıt zinciri mantıklı, FDTD/TCMT sınırı doğru çizilmiş, ve öngördüğü
observability riski bu oturumda **üç kez** somut olarak doğrulandı. Taslak
yazıldığında bir tahmindi; şimdi ölçülmüş bir gerçek.

Altı revizyon:

| | revizyon | dayanak |
|---|---|---|
| R1 | İki modlu (CW/CCW) geri saçılmalı TCMT port sözleşmesi | `T_add = 0.097` ölçümü |
| R2 | C3 dayanıklılık metriğini önceden sabitle | post-hoc seçim riski |
| R3 | WP başına FlexCredit bütçesi; WP1/2/3/5 = `0 FC` | harcama şeffaflığı |
| R4 | **`const.md` çelişkisini ADR ile çöz — BLOKE EDİCİ** | aşağıda |
| R5 | Gecikmeli tap sayısını önceden sabitle + readout-only baseline | benchmark sızıntısı |
| R6 | Her FDTD rung'una enerji dengesi kapısı (`1e-3`) | bu oturumun üç kusuru |

### R4 neden bloke edici

`const.md` şu anda **bağlayıcı** olarak şunu diyor:

> - Nihai elektromanyetik çözüm Tidy3D ile uçtan uca 3D FDTD olmalıdır.
> - TCMT/reduced-order sonuçları yardımcı kanıttır; full 3D FDTD yerine geçmez.

Taslağın önerdiği mimari bunun tam tersidir: TCMT birincil, FDTD kalibratör.
Ve elimizde bu hükmün **ulaşılamaz** olduğuna dair belgelenmiş kanıt var:

- CFL duvarı Tidy3D'nin kapalı explicit Yee çözücüsünde aşılamıyor;
- FCD/FCA ve termal ODE'ler Tidy3D'ye native bağlanamıyor
  (`reports/FDTD-001-mrr-feasibility.md`).

Yani `const.md` şu anda **yapılamayacak bir şeyi zorunlu kılıyor** ve bu plan
kabul edilirse her adım nominal olarak sözleşmeyi ihlal eder. Bu, taslağın
kalitesiyle ilgili bir sorun değil, sözleşmenin kendisiyle ilgili. Taslak da
bunu zaten "Açık karar" başlığı altında işaret ediyor — doğru teşhis.

`AGENTS.md` §Amaç ve §Aşamalar da aynı ifadeyi taşıyor, birlikte güncellenmeli.

**Bu benim tek başıma değiştireceğim bir şey değil**: tek-operatör sözleşmesi
mimari kararları bana bırakıyor ama `const.md` sabitlerini açıkça Hasan'ın
onayına ve ayrı bir karar kaydına bağlıyor
(`docs/decisions/2026-09-13-single-operator-contract.md`). Karar Hasan'ındır.

Öneri: `const.md`'nin ilgili iki maddesi şöyle yeniden yazılsın —

> - Optik çekirdeğin parametreleri (`Q_i`, `Q_e`, coupling, mode overlap,
>   rezonans) 3B FDTD/eigenmode ile ölçülür ve kaynak-hash'lenir.
> - Zaman-serisi görev çözümü, FDTD-kalibre edilmiş TCMT/rate-equation
>   modeliyle yapılır; uçtan uca Maxwell zorunluluğu kaldırılır.
> - Kaldırılan zorunluluğun gerekçesi: CFL duvarı ve FCD/FCA'nın Tidy3D'de
>   native olmaması (belgelenmiş).

Benchmark, kör-seed protokolü ve `NMSE < 0.05` hedefi **değişmeden** kalır.

---

## Sonuç

Taslak kabul edilebilir ve iyi düşünülmüş. R1–R3, R5, R6 taslağın içinde
çözülebilir. **R4 Hasan'ın kararını bekliyor ve çözülmeden WP1 başlatılmamalıdır**,
çünkü WP1'in ürettiği model sözleşmesi doğrudan `const.md`'nin yasakladığı
mimariyi kuruyor.
