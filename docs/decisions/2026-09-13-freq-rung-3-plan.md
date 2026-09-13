# 2026-09-13 — freq-rung-3 planı: 14 step/λ mesh yakınsaması (ONAY BEKLİYOR)

- Hazırlayan: Claude Opus 5
- Durum: PLAN HAZIR — **ücretli solve başlatılmadı**
- Draft task: `fdve-1f8f0d66-3509-4ce5-8239-359c5e6f6d08` (yalnız upload + estimate)
- Simulation digest: `fd1cdd416344d12748d9c16957074a3b...`
- Geometry hash: `68867f8d...` — **`freq-rung-2` ile birebir aynı**
- Plan: `manifests/fdtd/mrr-linear-001/freq-rung-3.plan.json`

## Neden gerekiyor

Mesh yakınsaması hâlâ kapalı. Eldeki tek kanıt `mesh-rung-2` değerlendirmesindeki
`10 → 12 step/λ` için `+1.45..+1.89 nm` rezonans kayması. **O ölçüme artık
güvenmiyorum**: facet Fabry-Pérot kavitesi, yanlış uçtaki drop portu ve `0.5 nm`
frekans örneklemesi — üç kusurun üçü de o veride vardı. Yakınsama, düzeltilmiş
kurguyla sıfırdan kurulmalı.

## Koşu tanımı

`freq-rung-2` ile **tek farkı grid**. Geometri (schema `/2`,
`bus_overhang_um = 2.0`), dört port, monitör tarakları, `run_time` ve `shutoff`
aynı — bu kasten böyle, çünkü `lambda_0`, `Q_L` ve `Q_e` doğrudan
karşılaştırılabilsin.

| | freq-rung-2 | freq-rung-3 |
|---|---|---|
| grid | `12 step/λ` | **`14 step/λ`** |
| hücre | `25 198 080` | **`38 155 300`** (`1.51x`) |
| zaman adımı | `2 214 167` | **`2 586 028`** (`1.17x`, CFL) |
| domain | `18.0 x 13.3 x 6.22 µm` | aynı |
| `run_time` | `150 ps`, shutoff `1e-5` | aynı |
| monitörler | 4 port, 2001/201 nokta | aynı |

`run_time` kasten kısaltılmadı. Tahmin tam `run_time` üzerinden hesaplandığı
için `135 ps`'e çekmek tahmini `~%10` düşürürdü, ama erken shutoff `12 step/λ`'da
`~118 ps`'de tetikleniyordu ve `14 step/λ`'da biraz gecikirse dalga treni
kesilir — DFT'nin Lorentzian'ı doğru vermesinin ön şartı tam da sinyalin sönmüş
olması. `~2 FC` için bu riski almaya değmez.

## Maliyet — bu rung belirgin daha pahalı

| | FlexCredit |
|---|---|
| `estimate_cost` (üst sınır) | **22.8463** |
| beklenen gerçek | **`~16.6`** |
| önerilen tavan | **23** |

Beklenti gerekçesi: `freq-rung-2`'de tahmin `14.7500` → gerçek `10.7316`
(oran `0.728`). Aynı oranla `22.8463 x 0.728 ≈ 16.6`.

**Bu, şimdiye kadar kullanılan `15 FC` tavanının üstündedir ve ayrı bir karar
gerektirir.** Maliyet artışı fizikten geliyor: 3B'de hücre sayısı
`(14/12)^3 = 1.59`, zaman adımı CFL nedeniyle `14/12 = 1.17`; çarpım `~1.85`.

**DÜZELTME (2026-09-13, denetim sonrası):** bu satırda başta "proje toplamı bu
koşuyla `~61 FC` olur (önceki rung'lar `~44.4`)" yazıyordu. Yanlıştı. Cloud'dan
doğrulanan gerçek harcama, bu koşu başlamadan önce zaten **`60.9646 FC`** idi;
`freq-rung-3` ile toplam **`~78 FC`** olacak. Hata, harcamanın cloud yerine
önceki metin kayıtlarından toplanmasından kaynaklandı. Tek doğru kaynak artık
`reports/FLEXCREDIT-LEDGER.md`.

## Kabul ölçütleri — koşudan önce yazıldı

`freq-rung-2` referans değerleri: `lambda_0 = 1.540945 µm`, `Q_L = 9 797`,
`Q_e(toplam) = 12 260`, `x = 0.79912`, `T_add = 0.09691`.

1. **Rezonans kayması**: `|lambda_0(14) - lambda_0(12)|`. FSR `~18.9 nm`
   olduğuna göre kaymanın FSR'nin `%1`'inden (`~0.19 nm`) küçük olması
   yakınsama lehine güçlü kanıttır. `%5`'ten (`~0.95 nm`) büyükse
   `12 step/λ` yakınsamamıştır.
2. **`Q_L` kayması**: `%5`'ten küçük olmalı.
3. **`Q_e` kayması**: `%5`'ten küçük olmalı — WP4 için asıl kalibrasyon
   büyüklüğü bu.
4. **Enerji dengesi korunmalı**: rezonans dışı dört-port toplamı `1.0`'a
   `1e-3` içinde kalmalı. Kalmazsa daha ince mesh yeni bir sayısal kayıp
   kanalı açıyor demektir.

Ölçüt 1–3 geçerse lineer kapı kapanır ve `12 step/λ` üretim mesh'i olarak
kilitlenir. Geçmezse `16 step/λ` gerekir ve bu, maliyeti yine `~1.85x`
büyütür — o noktada mesh yakınsamasının bu geometride bu bütçeyle
erişilebilir olup olmadığı ayrıca sorgulanmalıdır.

## Riskler

- Tahmin `22.85`, tavan `23` ile arada yalnız `%0.7` pay var. `freq-rung-2`'de
  gerçek maliyet tahminin `%73`'ü çıktı, ama bu garanti değil.
- `12 step/λ`'da PML yakınsaması (`pml-rung-1`, 12 vs 16 katman) doğrulanmıştı;
  o test `14 step/λ` için tekrarlanmadı. PML katman sayısı sabit kalıyor ama
  fiziksel kalınlığı grid adımıyla birlikte küçülüyor.
- Ölçüt 1–3 geçse bile `Q_i` hâlâ aralık olarak kalır; onu daraltmak dört-portlu
  geri saçılmalı TCMT ister, mesh değil.

## Onay istenen tek şey

`freq-rung-3`'ü **`23 FC` tavanıyla** çalıştırmak. Bu, önceki rung'lardaki
`15 FC` tavanının üstüne çıkmak anlamına gelir.
