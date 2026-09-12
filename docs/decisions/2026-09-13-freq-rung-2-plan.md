# 2026-09-13 — freq-rung-2 planı: facet'siz bus + dört port (ONAY BEKLİYOR)

- Hazırlayan: Claude Opus 5
- Durum: PLAN HAZIR — **ücretli solve başlatılmadı**
- Draft task: `fdve-0ecc2c8f-e120-4b3c-8793-c9c0dcbda224` (yalnız upload + estimate)
- Simulation digest: `2032012f922f974f7acf3316fa9f06734f3ee5b37d754dfe7d9b65bbc78de981`
- Geometry hash: `68867f8d...` (schema `fdtd-mrr-geometry/2`)
- Plan: `manifests/fdtd/mrr-linear-001/freq-rung-2.plan.json`
- Girdi: `manifests/fdtd/mrr-linear-001/freq-rung-2.input.json`

## Neyi düzeltiyor

İki kusur birlikte kapatılıyor:

1. **Facet Fabry-Pérot** (`2026-09-13-facet-fabry-perot.md`): bus artık her port
   düzleminden `2.0 µm` daha uzun çiziliyor (`bus_overhang_um = 2.0`), toplam
   `20.0 µm`. Uç yüzler `x = ±10`'da, domain `±9`; yani PML içinde sonlanıyorlar.
   Kavite ortadan kalkıyor.
2. **Eksik portlar** (`2026-09-13-freq-rung-1-evaluation.md` §4a): dört port
   birlikte ölçülüyor, böylece enerji dengesi ilk kez kapatılabilir.

## Koşu tanımı

Domain, mesh, sınırlar ve `run_time` `mesh-rung-2` / `freq-rung-1` ile **aynı**:

| | değer |
|---|---|
| grid | AutoGrid `12 step/λ` @ 1.55 µm |
| domain | `18.0 x 13.3 x 6.22 µm` — overhang büyütmedi |
| hücre | `25 198 080` |
| PML | 12 katman (x/y/z) |
| `run_time` | `150 ps`, `shutoff = 1e-5` |
| zaman adımı | `2 214 167` |

### Monitörler — role göre tarak

Hepsi `1.53093–1.55093 µm` bandında (20 nm, bir tam FP periyodundan geniş):

| token | konum | nokta | adım | rol |
|---|---|---|---|---|
| `flux:bus_through:out` | `x=+8` | **2001** | 10 pm | çizgi + FP baseline kontrolü |
| `flux:bus_drop:in` | `x=-8` | **2001** | 10 pm | **gerçek drop portu**, çizgi |
| `flux:bus_drop:out` | `x=+8` | 201 | 100 pm | add portu, enerji muhasebesi |
| `flux:bus_through:in` | `x=-8` | 201 | 100 pm | kaynak düzlemi net flux, muhasebe |

`0.159 nm` FWHM'e 10 pm adımda `~16` nokta düşüyor — tepe genliği `%0.5`'ten iyi.
Dört portun hepsini `2001`'de tutmak tahmini `14.93 FC`'ye çıkarıyordu; muhasebe
portlarını seyreltmek `14.75`'e indirdi. Çizgi çözünürlüğü gereken iki port
yoğun kaldı.

Bant `20 nm` seçildi ki **FP fringe'inin gerçekten kaybolduğu doğrulanabilsin**:
periyot `17.96 nm`, bant `1.11` periyot kapsıyor. Bu, koşunun kabul testidir.

## Maliyet

| | FlexCredit |
|---|---|
| `estimate_cost` (tam `run_time` üst sınırı) | **14.7500** |
| beklenen gerçek | **`~11.6`** |
| önerilen tavan | **15** |

Beklenti gerekçesi: `freq-rung-1`'de tahmin `14.6803` → gerçek `11.5346`
(oran `0.785`), çünkü erken shutoff `~118 ps`'de devreye giriyor ve tahmin tam
`run_time` üzerinden hesaplanıyor. Aynı domain ve aynı zaman adımı sayısı.

## Kabul ölçütleri

Koşu şu üç testten geçmeli:

1. **FP fringe kayboldu mu**: `flux:bus_through:out` baseline'ındaki `%40`
   tepe-tepe salınım belirgin biçimde azalmalı. Azalmazsa facet teşhisi yanlıştı.
2. **Enerji dengesi kapandı mı**: rezonans dışında dört portun toplamı `1.0`'a
   yakın olmalı (şu an iki portla `0.77–0.88`). Kapanmazsa dördüncü bir kayıp
   kanalı var.
3. **`Q_i`/`Q_e` tutarlılığı**: gerçek drop portu ile `T_through = (1-x)^2`
   koşulu tutmalı. Tutarsa ayrım ilk kez geçerli olur.

`Q_loaded ~ 9 650` değişmemeli — FP zarfı 18 nm, çizgi `0.16 nm` ölçeğinde,
karışmazlar. Değişirse bir varsayımım yanlış demektir.

## Riskler

- `flux:bus_through:in` kaynakla aynı düzlemde; oradaki flux **net** değer verir
  (ileri eksi geri), temiz bir yansıma ölçümü değil. Enerji dengesinde bu
  yorumlanabilir ama tek başına yansıma katsayısı vermez.
- Facet'ler PML içinde sonlandığında PML'in kılavuzlu modu soğurma kalitesi
  önem kazanır. 12 katman `pml-rung-1`'de 16 katmana karşı doğrulanmıştı, ama o
  test facet'siz bir kılavuz için yapılmadı.
- Geometri değişti, dolayısıyla rezonans dalga boyu `1.54091`'den hafifçe
  kayabilir. `20 nm` bant bunu rahatça kapsıyor.

## Onay istenen tek şey

`freq-rung-2`'yi `15 FC` tavanıyla çalıştırmak. Onay gelmeden submit edilmez.
