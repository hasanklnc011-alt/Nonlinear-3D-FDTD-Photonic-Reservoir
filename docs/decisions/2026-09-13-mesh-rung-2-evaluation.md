# 2026-09-13 — mesh-rung-2 değerlendirmesi: zaman kapısı geçti, mesh kapısı kapalı, monitör kusuru bulundu

- Task: `fdve-b2b294bc-e886-4f84-adcc-4430d5a24a0e` (`mrr-linear-001-mesh12-time-est-150ps`)
- Durum: `success` | gerçek maliyet **11.4329 FC** (tahmin 14.5508 FC)
- Zaman adımı sayısı: 2 214 167 | erken shutoff ~118 ps'de
- Veri: `mesh_rung2_data.hdf5` (Git'e eklenmez)
- Değerlendiren: Claude Opus 5 (tek operatör sözleşmesi)

## 1. Zaman yakınsaması — GEÇTİ

Final field decay **`9.99e-06 < 1e-5`**. Çözücü 150 ps'yi kullanmadan ~118 ps'de
"Field decay smaller than shutoff factor" ile çıktı.

Bağımsız doğrulama: aynı mesh'te (12 step/λ) 105 ps'lik `mesh-rung-1` ile
karşılaştırıldığında bant-integre |flux| farkı through'da `+0.01%`, drop'ta
`+1.21%`; rezonans dalga boyları **altı hanede aynı**. Yani 105→150 ps uzatması
gözlenebilirleri değiştirmiyor → zaman ekseni 12 step/λ'da yakınsamış.

`mesh-rung-1` kaydındaki "zaman yakınsaması da geçmedi" engeli böylece kalktı.

## 2. Mesh yakınsaması — GEÇMEDİ

10 step/λ (`time-rung-3`) ile 12 step/λ (`mesh-rung-2`) arasında rezonans
dalga boyları sistematik olarak kayıyor:

| 12 step/λ | 10 step/λ | kayma |
|---|---|---|
| 1.50376 µm | 1.50565 µm | `+1.89 nm` |
| 1.52236 µm | 1.52381 µm | `+1.45 nm` |
| 1.55996 µm | 1.56148 µm | `+1.52 nm` |
| 1.57947 µm | 1.58103 µm | `+1.56 nm` |

Ölçülen FSR `18.6–19.5 nm`. Kayma FSR'nin **~%8'i** ve tüm rezonanslarda aynı
işaretli/aynı büyüklükte — sayısal gürültü değil, sistematik mesh hatası
(effective index'in mesh çözünürlüğüyle kayması). 12 step/λ hâlâ yakınsamamış.

## 3. YENİ BULGU — frekans monitörü rezonansları çözmüyor (kapı-engelleyici)

Flux monitörleri `1.500–1.600 µm` bandında **201 nokta** = `0.500 nm` adım.
Rezonans çevresindeki ham örnekler (drop portu, 12 step/λ):

```
lam ofset:  -1.48   -0.99   -0.49    0.00   +0.50   +0.99   +1.49  nm
drop:       0.0006  0.0014  0.0065  0.1108  0.0048  0.0013  0.0005
```

Tepe **tek bir örnekten** ibaret; komşular ~20–70× aşağıda. Yani gerçek FWHM
`0.5 nm`'den belirgin küçük, gerçek `Q > ~3100`, ve **ölçülen tepe değeri
gerçek tepe değeri değil** — ızgaranın rezonansa ne kadar yakın düştüğüne bağlı
rastgele bir alt sınır.

Sonuçları:

- Rung'lar arası **genlik** karşılaştırmaları geçersiz. Backlog'daki
  "`%40–60` flux değişimi" bulgusu büyük ölçüde bu örnekleme artefaktıdır,
  fiziksel mesh hatası değil. (Bant-integre |flux| farkı gerçekte through'da
  `-0.26%`, drop'ta `+7.83%`.)
- `Q_i`/`Q_e` ayrımı, extinction ratio ve coupling bu veriden **çıkarılamaz**.
- Kusur rung-0'dan beri tüm koşularda mevcut; şimdiye kadarki hiçbir koşu
  Q veya coupling gözlenebiliri üretmemiştir.

## 4. Hüküm

Lineer kapı **kapalı kalıyor**. Ama engel sanıldığı yerde değil: asıl sorun
mesh merdivenini yukarı tırmanmak değil, **ölçüm kurgusunun rezonansı
görememesi**. Daha yüksek mesh'e (14/16 step/λ) çıkmak, aynı kör monitörle
yine Q/coupling üretmez.

### Önerilen sıradaki adım (Hasan onayı gerektirir — ücretli)

12 step/λ'yı koru, **frekans örneklemesini düzelt**: bandı rezonans çevresine
daralt veya frekans nokta sayısını `201 → ~2000`'e çıkar. DFT monitör noktası
eklemek time-stepping maliyetini değiştirmez; koşu yine ~11–12 FC
mertebesindedir, ama çıktı ilk kez Q ve coupling verir. Ardından aynı düzeltilmiş
monitörle 14 step/λ tekrarlanıp rezonans kayması yakınsama testi yapılır.

Bu düzeltme yapılmadan yeni mesh rung'u açmak FlexCredit israfıdır.

## 5. Araştırma planı taslağına etkisi

`docs/coordination/2026-09-13-astra-tcmt-fdtd-research-plan-review.md`, WP4'te
FDTD'yi "geometri → `Q_i`, `Q_e`, coupling, mode overlap" kalibratörü olarak
kullanıyor. Bu bulgu o planın **4. inceleme maddesini** (FDTD büyüklükleri
mevcut monitor verisiyle gerçekten tanımlanabilir mi?) doğrudan cevaplıyor:
**mevcut monitör kurgusuyla tanımlanamaz.** Plan kabul edilirse WP4'ten önce
monitör sözleşmesi düzeltilmelidir. Bu, planı geçersiz kılmaz — aksine
öngördüğü riski somut olarak doğrular.
