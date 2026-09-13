# 2026-09-13 — freq-rung-3 değerlendirmesi: 4 ölçütten 3'ü geçti, `Q_L` geçmedi

- Task: `fdve-1f8f0d66-3509-4ce5-8239-359c5e6f6d08`
- Durum: `success` | **gerçek maliyet `18.1080 FC`** (tahmin 22.8463, tavan 23)
- Beklentim `~16.6` idi; `%9` üstünde çıktı. Final decay `9.93e-06`.
- Bakiye koşudan sonra: **`115.7358 FC`**
- Ölçütler koşudan önce yazıldı: `docs/decisions/2026-09-13-freq-rung-3-plan.md`

## Karşılaştırma — tek değişken grid

| | 12 step/λ | 14 step/λ | değişim |
|---|---|---|---|
| `lambda_0` (µm) | 1.540945 | 1.540865 | **`-0.01%`** |
| FWHM (nm) | 0.1573 | 0.1683 | `+7.01%` |
| `Q_loaded` | 9 797 | 9 154 | **`-6.56%`** |
| `T_drop` | 0.63860 | 0.57214 | `-10.41%` |
| `T_through` | 0.04546 | 0.06519 | `+43.40%` |
| `T_add` | 0.09691 | 0.14903 | **`+53.79%`** |
| `x` | 0.79912 | 0.75640 | `-5.35%` |
| `Q_e` | 12 259 | 12 102 | **`-1.28%`** |
| `Q_i` (model A) | 48 770 | 37 579 | `-22.95%` |

## Ölçüt hükümleri

| | ölçüt | sonuç | hüküm |
|---|---|---|---|
| 1 | rezonans kayması `< %1` FSR | `-0.0800 nm` = FSR'nin `%0.42`'si | **GEÇTİ (güçlü)** |
| 2 | `Q_L` kayması `< %5` | `-6.56%` | **GEÇMEDİ** |
| 3 | `Q_e` kayması `< %5` | `-1.28%` | **GEÇTİ** |
| 4 | enerji dengesi `1e-3` | en büyük sapma `2.37e-04` | **GEÇTİ** |

## Teşhis — hangi büyüklük yakınsamıyor

Rezonans **konumu** mükemmel yakınsamış (`%0.42` FSR). Yani geometri, effective
index ve mesh'in dispersiyon davranışı oturmuş durumda. Yakınsamayan şey
**kayıp kanalları**:

- `T_add` `+53.8%` — açık ara en büyük değişim
- `T_through` `+43.4%`
- `T_drop` `-10.4%`

Yani ince mesh'te halka daha fazla güç kaybediyor ve kaybın büyük kısmı add
portuna (geri saçılma yönüne) gidiyor. `Q_L` bu yüzden düşüyor; `Q_L`'nin
kendisi bağımsız bir kusur değil, bu kanalların sonucu.

Enerji dengesi her iki mesh'te de kapanıyor (`2.4e-04`), yani gross bir hata
yok. `subpixel` averaging açık (`PolarizedAveraging`), yani bu bir konfigürasyon
eksikliği değil.

Kalan açıklama: **eğri halka sınırının ayrıklaştırılması**. Subpixel averaging'e
rağmen, eğri bir sınırın Yee ızgarasına oturtulması sayısal bir pürüzlülük
üretir ve geri saçılma bu pürüzlülüğe çok duyarlıdır. Mesh değişince sayısal
pürüzlülüğün deseni de değişir. `T_add`'in iki mesh arasında yarıdan fazla
değişmesi, onun **yakınsamamış** ve muhtemelen ağırlıklı olarak sayısal
olduğunu gösterir.

### DÜZELTME — önceki fazla iddia

`docs/decisions/2026-09-13-freq-rung-2-evaluation.md`'de `T_add = 0.09691`
için şöyle yazmıştım:

> "Add portundaki `0.0969`, halkada CW ve CCW modlarını birbirine bağlayan
> geri saçılmanın **doğrudan ölçümüdür**... Bu, ideal olmayan ama **gerçek**
> bir cihaz özelliğidir."

**Bu fazla iddiaydı.** Tek mesh seviyesinde ölçülmüş, yakınsaması sınanmamış bir
büyüklüğü fiziksel gerçeklik olarak sundum. `14 step/λ`'da `%54` değiştiğine
göre değer sayısal kaynaklı olabilir. Doğru ifade: *"add portunda ölçülebilir
güç var; kaynağı fiziksel geri saçılma ve/veya eğri sınır ayrıklaştırması
olabilir, ayırt edilmedi."*

Bu, plan incelemesindeki R1'i (iki modlu CW/CCW TCMT) zayıflatmaz ama
gerekçesini değiştirir: R1 hâlâ gerekli, çünkü kanal modelde yok; ama o kanalın
fiziksel büyüklüğü henüz bilinmiyor.

## Sonuç ve tavsiye — `16 step/λ` ÖNERMİYORUM

Sözleşmenin V4 kaçış valfi (`AGENTS.md`) tam bu durum için yazıldı.

`16 step/λ` maliyeti `~42 FC` olurdu; kalan `115.74 FC`'nin **`%36`**'sı, ve
`25 FC` tek-koşu sınırının üstünde, yani zaten ayrı karar gerektirir. Karşılığında
elde edeceğimiz şey `Q_L`'nin belirsizliğini daraltmak — ama:

1. **WP4'ün ihtiyaç duyduğu parametre `Q_e` ve o yakınsadı** (`%1.28`).
2. `Q_i`, transmisyon yolundan zaten model bağımlı; onu daraltacak olan mesh
   değil, **ücretsiz bend mode solver yoludur** (V3 ikinci yolu). Bend mode
   çözümünde eğri yol konform dönüşümle ele alınır, yani halka sınırının
   ızgaraya oturtulması sorunu yoktur — bu yüzden `Q_i` için yapısal olarak
   daha uygun bir yol.
3. Geri saçılma kanalı sayısal olabileceği için, daha ince mesh onu
   yakınsatmayabilir de.

### Kabul edilen değerler ve belirsizlikleri

```
lambda_0 = 1.54090 um  +- 0.00008   (yakinsadi, %0.42 FSR)
Q_e      = 12 180      +- %1.3      (yakinsadi)
Q_L      = 9 500       +- %7        (MESH BELIRSIZLIGI ILE, yakinsamadi)
Q_i      = FDTD transmisyonundan RAPOR EDILMIYOR
           -> bend mode solver yoluna birakildi (0 FC)
T_add    = yakinsamadi, fiziksel/sayisal ayrimi yapilmadi
```

`Q_L` reddedilmedi; belirsizlikle işaretlendi ve TCMT'ye o belirsizlikle
girecek. C3'ün duyarlılık analizi zaten bu belirsizliği kullanacak.

## Lineer kapının durumu

**Koşullu olarak kapanıyor.** Rezonans konumu ve `Q_e` yakınsadı, enerji dengesi
sağlam, `12 step/λ` üretim mesh'i olarak kilitlenebilir — ancak `Q_L` ve geri
saçılma için belirtilmiş belirsizlikle.

`freq-rung-3` bu projede yakınsama amaçlı **son** ücretli koşu olmalıdır. Bundan
sonraki FDTD harcaması yalnız WP4 surrogate doğrulaması ve WP6 nihai kilit
içindir.

## Harcama

| | FC |
|---|---|
| bu koşu | 18.1080 |
| toplam harcanan | 79.0726 |
| kalan bakiye | **115.7358** |

Tahmin `22.85` → gerçek `18.11`, oran `0.79`. Beklentim `16.6` idi, `%9`
yanıldım; `freq-rung-2`'nin `0.728` oranını kullanmıştım ama daha ince mesh'te
erken shutoff daha geç tetikleniyor.
