# 2026-09-13 — freq-rung-1: dar-bant frekans tarağı planı (ONAY BEKLİYOR)

- Hazırlayan: Claude Opus 5
- Durum: PLAN HAZIR — **ücretli solve başlatılmadı**, Hasan onayı bekleniyor
- Draft task: `fdve-719dd4d0-fed8-4d10-9be8-6c0aab8b047a` (yalnız upload + estimate)
- Simulation digest: `e9ec23b50579f965748bc3bf2b81e8e2fbede282b90fe0536750eeb1391ca75c`
- Plan: `manifests/fdtd/mrr-linear-001/freq-rung-1.plan.json`

## 1. Kapatılan belirsizlik: `Q_loaded`

Tidy3D'nin `shutoff` alanının tanımı doğrulandı
(`tidy3d/components/simulation.py`, `shutoff` açıklaması):

> "Ratio of the instantaneous integrated E-field **intensity** to the maximum value"

Intensity = enerji. Yani log'daki "field decay" enerji oranıdır, alan genliği
değil. `mesh-rung-2` ring-down fit'i (36–118 ps penceresi, `R^2 = 0.938`):

```
tau_enerji = 22.52 ps   ->   Q_loaded = omega * tau_E
```

| rezonans | `Q_loaded` | FWHM |
|---|---|---|
| 1.50376 µm | 28 209 | 0.0533 nm |
| 1.54093 µm | 27 529 | 0.0560 nm |
| 1.55996 µm | 27 193 | 0.0574 nm |
| 1.57947 µm | 26 857 | 0.0588 nm |

Önceki `2x` belirsizlik kapandı; `Q ~ 27 000`. `R^2 = 0.938`, tek üstel değil —
dört rezonans hafifçe farklı Q'larla vuruşuyor. Bu yüzden bu bir mertebe
tahminidir, nihai tek-rezonans değeri değil. Kesin değer bu koşudan gelecek.

## 2. `Q_loaded` yeter mi? Hayır

`1/Q_loaded = 1/Q_i + 1/Q_e`. Ring-down yalnız toplamı verir, çünkü **hız**
bilgisidir. Ayrım için rezonanstaki **genlik** gerekir: through portundaki
extinction derinliği ve drop portuna geçen güç. Mevcut `0.5 nm` örnekleme
tepeyi ıskaladığı için genlik ölçülemiyor, dolayısıyla ayrım yapılamıyor.

## 3. Bulunan kod kusuru ve düzeltmesi

`fdtd/tidy3d_build/linear_build.py` içindeki `_band_frequencies`, hem kaynak
darbesini hem monitör frekanslarını **aynı** `inputs.excitation` bloğundan
türetiyordu. Bu kurguda bandı daraltmak kaynağı da daraltır; dar-bantlı bir
Gaussian darbe zamanda uzar ve gereken `run_time`'ı büyütür. Yani ölçümü
iyileştirme girişimi maliyeti artırırdı.

Plan şeması zaten her monitörde bir `sampling` bloğu taşıyor, ama `_monitors`
bunu yok sayıyordu. `_sampling_frequencies` eklendi; `_monitors` artık
monitörün kendi `sampling` bloğunu kullanıyor. Blok yoksa eski davranış aynen
korunuyor, yani geriye dönük uyumlu.

Kanıt: `tests/fdtd/test_monitor_sampling.py` (8 test) — düşme davranışı,
monitör başına farklı tarak, bandın doğru gerilmesi, **kaynak darbesinin
değişmediği**, digest'in değiştiği ve bozuk `sampling` bloklarının fail-closed
reddedildiği. Depo geneli: `187/187 OK`.

## 4. Koşu planı

`mesh-rung-2` ile aynı: geometri, malzeme, 12 step/λ AutoGrid, 12 katman PML,
`run_time = 150 ps`, `shutoff = 1e-5`. Değişen tek şey monitör frekans tarağı.

| | mesh-rung-2 | freq-rung-1 |
|---|---|---|
| monitör bandı | 1.500–1.600 µm | **1.53943–1.54243 µm** |
| nokta | 201 | **1501** |
| adım | 500 pm | **2 pm** |
| FWHM başına nokta | `~0.1` | **`~28`** |
| kaynak darbesi | 1.55 µm ± 0.05 | aynı (değişmedi) |

Hücre `25 198 080`, zaman adımı `2 214 167`, monitör verisi `2 x 6 kB`.

### DFT geçerliliği

Yoğun frekans örneklemesinin doğru Lorentzian vermesi, sinyalin koşu içinde
sönmüş olmasına bağlıdır; sönmemiş bir dalga treninin kesilmesi çizgiyi yapay
olarak genişletir. `mesh-rung-2` alanı `9.99e-06 < 1e-5`'e indirdi, yani kesme
hatası `~1e-5` mertebesinde ve ihmal edilebilir. **Bu ön şartı sağlayan ilk ve
tek koşu mesh-rung-2'dir.** Daha önceki rung'lara yoğun tarak konsaydı sonuç
yine güvenilmez olurdu.

## 5. Maliyet

| | FlexCredit |
|---|---|
| `estimate_cost` (üst sınır) | **14.6803** |
| mesh-rung-2 tahmin / gerçek | 14.5508 / 11.4329 |
| beklenen gerçek | `~11.5` (aynı erken shutoff) |

Yoğun tarağın ek yükü tahminde `+0.13 FC`. Önerilen yazılı tavan: **15 FC**.

## 6. Bu koşudan ne çıkar

- Rezonansın çözülmüş Lorentzian çizgisi, dolayısıyla `Q_loaded` kesin değeri
- Through extinction derinliği + drop tepe değeri, dolayısıyla **`Q_i` ve `Q_e`
  ayrı ayrı**
- Kuplaj rejimi: under-coupled, kritik, yoksa over-coupled
- Bu, `AGENTS.md` kanıt kuralının istediği ilk gerçek optik parametre ölçümüdür
  ve TCMT/FDTD sınırı tartışmasına sayı sokar.

## 7. Ne çıkmaz

Mesh yakınsaması. 10→12 step/λ rezonansı `+1.5 nm` kaydırıyordu; bunun kapanması
için **düzeltilmiş tarakla** ayrı bir 14 step/λ koşusu gerekir (`freq-rung-2`).
O da ayrı onay ve ayrı `~15 FC`'dir. Sıralama önemli: 14 step/λ'yı eski kör
monitörle koşmak yine Q üretmez, o yüzden önce `freq-rung-1`.

## 8. Onay istenen tek şey

`freq-rung-1`'i `~15 FC` tavanıyla çalıştırmak. Onay gelmeden submit edilmez.
