# 2026-09-13 — freq-rung-2 değerlendirmesi: üç kabul ölçütü de geçti, `Q_e` ilk kez ölçüldü

- Task: `fdve-0ecc2c8f-e120-4b3c-8793-c9c0dcbda224`
- Durum: `success` | **gerçek maliyet `10.7316 FC`** (tahmin 14.7500, tavan 15)
- Final decay `9.83e-06`, erken shutoff, time-stepping 2697 s
- Veri: `freq_rung2_data.hdf5` (Git'e eklenmez)
- Geometri: schema `/2`, `bus_overhang_um = 2.0`, geometry hash `68867f8d...`

Kabul ölçütleri koşudan **önce** yazılmıştı
(`docs/decisions/2026-09-13-freq-rung-2-plan.md` §Kabul ölçütleri); aşağıdaki
hükümler o ölçütlere göre verildi.

## Ölçüt 1 — Fabry-Pérot fringe kayboldu mu? **GEÇTİ**

| | baseline min | max | tepe-tepe |
|---|---|---|---|
| `mesh-rung-2` (facet'li) | 0.5126 | 0.8988 | **%39** |
| `freq-rung-2` (facet PML'de) | 0.9988 | 1.0000 | **%0.1** |

Dalgalanma `%39 → %0.1`, yani ~400 kat bastırıldı. Facet teşhisi doğruydu.
Baseline ortalaması `0.6883 → 0.9997`.

## Ölçüt 2 — Enerji dengesi kapandı mı? **GEÇTİ**

Rezonanstan `4–8 nm` uzakta, dört portun toplamı:

```
lam=1.53295: through 0.9998 + drop 0.0001 + add 0.0000 = 0.9999
lam=1.53695: through 0.9996 + drop 0.0002 + add 0.0000 = 0.9998
lam=1.54495: through 0.9996 + drop 0.0002 + add 0.0000 = 0.9998
lam=1.54895: through 0.9999 + drop 0.0001 + add 0.0000 = 1.0000
```

Önceki durum `0.77–0.88` idi. Şimdi `1.0000`'a `2e-4` yakınlıkta. Kayıp
kanalı kalmadı; kayıpsız malzeme varsayımıyla da tutarlı.

## Ölçüt 3 — TCMT tutarlılığı **GEÇTİ**

Gerçek drop portu (`flux:bus_drop:in`, `x = -8`) ile:

```
T_drop = 0.63860    T_through = 0.04546    T_add = 0.09691
x = sqrt(T_drop) = 0.79912
beklenen T_through = (1-x)^2 = 0.04035   olculen 0.04546   FARK 0.00511
```

Tutarlılık hatası `0.22563 → 0.00511`, yani **44 kat** iyileşti. Önceki koşuda
yanlışlıkla ADD portunu drop sanıyorduk (`0.13358`); gerçek drop `0.63860`.

## Kontrol — `Q_loaded` değişmedi

`9 736 → 9 797`, **%0.6**. Bu önceden yazılmış bir uyarı sinyaliydi: FP zarfı
18 nm, rezonans çizgisi `0.157 nm` ölçeğinde olduğu için çizgi genişliğinin
etkilenmemesi gerekiyordu. Etkilenmedi — akıl yürütme doğrulandı.

## Sonuç: optik parametreler

### `Q_e` — sağlam

```
Q_loaded      =  9 797
Q_e (toplam)  = 12 260      iki bus birlikte
Q_c           = 24 519      tek coupler
```

`Q_e`, `Q_L` ve `x = sqrt(T_drop)`'tan doğrudan gelir; ikisi de doğrudan ölçüm.

### `Q_i` — model bağımlı, **aralık olarak** raporlanıyor

Girişin `%9.7`'si **add portundan** çıkıyor (`T_add = 0.09691`, drop'un `%15`'i).
Simetrik iki-coupler TCMT'de böyle bir kanal yok; model onu "kayıp" hanesine
yazıyor. Bu, `Q_i`'yi doğrudan etkiliyor:

| model | add portu nasıl sayılıyor | `Q_i` |
|---|---|---|
| A — simetrik TCMT (kanalsız) | intrinsic kayıp | **48 772** |
| B — add portu dış kanal | ölçülen radyasyon `0.2190` | **71 488** |

Aradaki çarpan `1.47`. İki modelin tutarlı olduğunun kanıtı: A'nın radyasyon
öngörüsü `0.3210`, ölçülen radyasyon + add `0.3159` — fark tamamen add
portundaki gücün nereye yazıldığından geliyor.

**`Q_i = 4.9e4 – 7.1e4` olarak raporlanmalıdır, tek sayı olarak değil.**
Daraltmak için ring'de geri saçılmayı içeren dört-portlu bir TCMT modeli
gerekir (WP1'in port normalizasyonu işi).

### Kuplaj rejimi — sağlam

`x = 0.799 >> 0.5`, yani **belirgin over-coupled**: `Q_e = 12 260 << Q_i`.
Her iki modelde de aynı sonuç. `0.2 µm` gap ile beklenen davranış.

### Geri saçılma doğrulandı

Add portundaki `0.0969`, halkada CW ve CCW modları birbirine bağlayan geri
saçılmanın doğrudan ölçümüdür. `freq-rung-1`'de gözlenen drop tepesi ile
through çukuru arasındaki `46 pm` kayma (mod yarılması) bununla tutarlı.
Bu, ideal olmayan ama **gerçek** bir cihaz özelliğidir.

## Harcama

| rung | gerçek FC |
|---|---|
| mesh-rung-2 | 11.4329 |
| freq-rung-1 | 11.5346 |
| freq-rung-2 | **10.7316** |

Tahmin `14.7500` idi; erken shutoff yine düşürdü ve beklentimin (`~11.6`)
de altında kapandı.

## Araştırma planına etkisi

`docs/coordination/2026-09-13-astra-tcmt-fdtd-research-plan-review.md` 4. inceleme
maddesi (FDTD büyüklükleri mevcut monitor verisiyle tanımlanabilir mi?) artık
**evet** ile cevaplanıyor — ama üç düzeltmeden sonra: frekans tarağı, port
yerleşimi, facet sonlandırması. WP4'ün ihtiyaç duyduğu geometri → `Q_e`
eşlemesi için gereken ölçüm zinciri kuruldu.

Kalan sınır: `Q_i` tek sayı olarak istenirse dört-portlu geri saçılmalı TCMT
gerekiyor.

## Sıradaki adım

Mesh yakınsaması hâlâ açık: `10 → 12 step/λ` rezonansları `+1.5 nm` kaydırıyordu
(`mesh-rung-2` değerlendirmesi). Ama o karşılaştırma facet'li, iki portlu ve
`0.5 nm` örneklemeli veriyle yapılmıştı — yani **üç kusurun üçü de içindeydi**.
Yakınsama artık düzeltilmiş kurguyla, `14 step/λ` ile tekrarlanmalı ve
`Q_L`, `Q_e`, `lambda_0` değerlerinin ne kadar kaydığına bakılmalıdır. Ayrı onay
ve ~15 FC.
