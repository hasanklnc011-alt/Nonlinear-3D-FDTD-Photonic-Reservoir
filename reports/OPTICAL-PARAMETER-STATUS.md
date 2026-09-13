# Optik parametre durumu — V1–V5 doğrulama merdiveni

Merdivenin tanımı: `AGENTS.md` §Kanıt kuralları → Doğrulama merdiveni.
Bu dosya, her ölçülmüş optik parametrenin hangi basamakları geçtiğini tutar.
**Hiçbir değer, bu tablodaki durumu yazılmadan TCMT'ye girdi olamaz.**

Son güncelleme: 2026-09-13. Kaynak koşular: `freq-rung-2` (12 step/λ,
`fdve-0ecc2c8f...`) ve `freq-rung-3` (14 step/λ, `fdve-1f8f0d66...`);
geometry `68867f8d...`, schema `/2`.

## Durum tablosu

| parametre | değer | V1 korunum | V2 kontrol | V3 çapraz yol | V4 yakınsama | V5 dış çapa |
|---|---|---|---|---|---|---|
| `lambda_0` | `1.54090 ± 0.00008` µm | ✅ | — | ✅ iki port, 46 pm | ✅ `%0.42` FSR | — |
| `Q_e` (toplam) | `12 180 ± %1.3` | ✅ | — | ❌ **tek yol** | ✅ `%1.28` | — |
| `Q_loaded` | `9 500 ± %7` | ✅ | — | ✅ iki port, `%0.6` | ⚠️ `%6.56` — **belirsizlikle kabul** | 〰️ |
| `Q_i` | **rapor edilmiyor** | ✅ | — | ❌ | ❌ `%23` | ✅ |
| `T_add` (geri saçılma) | **rapor edilmiyor** | ✅ | — | ❌ | ❌ `%54` | — |
| `n_eff` | 2.4017 | — | ✅ kontrol grubu | ❌ | ❌ **yapılmadı** | ✅ |

V4 kaynağı: `freq-rung-2` (12 step/λ) vs `freq-rung-3` (14 step/λ), tek değişken
grid. Bkz. `docs/decisions/2026-09-13-freq-rung-3-evaluation.md`.

Gösterim: ✅ geçti · ❌ geçmedi/yapılmadı · ⏳ koşu devam ediyor · 〰️ kısmi · — uygulanmaz

**Dürüst özet:** `lambda_0` ve `Q_e` yakınsadı ve kullanılabilir durumda —
ikisinin de V3 durumu hâlâ eksik (`Q_e` tek yoldan geliyor). `Q_L` belirtilmiş
belirsizlikle kabul edildi. `Q_i` ve `T_add` FDTD transmisyonundan **rapor
edilmiyor**: yakınsamadılar ve `T_add`'de fiziksel/sayısal ayrımı yapılamadı.
`Q_i` için ücretsiz bend mode solver yolu planlandı.

## Basamak basamak gerekçe

### V1 — korunum: geçti

Rezonans dışında dört portun toplamı `0.9998 – 1.0000`, yani `1.0`'a `2e-4`
içinde. Eşik `1e-3`. Kayıpsız malzeme varsayımıyla tutarlı.

Bu kapı, daha önceki üç koşuda **düşüyordu** (`0.77 – 0.88`) ve üç ayrı
observability kusurunu işaret ediyordu. Geriye dönük bakıldığında V1 tek başına
`~34 FC`'lik geçersiz ölçümü önlerdi.

### V2 — kontrol grubu: yalnız `n_eff` için yapıldı

Mode solver'da substrate kaldırılınca sızıntı fiziksel olarak imkânsız hâle
geliyor; `k_eff = -1.235e-08`, yani gürültü tabanı. Aracın kendisi doğrulandı.
Aynı koşu `n_eff = 2.40167` verdi — 450 x 220 nm SOI strip için beklenen değer.

`Q` büyüklükleri için henüz bir kontrol kurgusu tanımlanmadı.

### V3 — çapraz yol: kısmen

**Geçenler:**

- `Q_loaded`: drop portu `9 736`, through portu `9 557` → `%2` içinde.
  Bunlar aynı koşunun iki farklı monitörü, yani bağımsız ölçüm yolları.
- `lambda_0`: iki port `46 pm` içinde. Bu farkı önce "backscattering mod
  yarılması, artefakt değil" diye yorumlamıştım; `freq-rung-3`'te `T_add`'in
  `%54` değiştiği görülünce bu yorum **geri çekildi** — fark fiziksel
  yarılma ve/veya eğri sınır ayrıklaştırması kaynaklı olabilir, ayırt edilmedi.

**Geçmeyenler ve ikinci yolları (hepsi `0 FC`, yerel):**

| parametre | eksik ikinci yol | araç |
|---|---|---|
| `Q_e` | gap → coupling `κ`, even/odd supermode yarılmasından | iki kuplajlı waveguide mode solve |
| `Q_i` | bend radyasyon kaybı | `ModeSpec(bend_radius=..., bend_axis=...)` |
| `n_eff` | `n_g` → ölçülen FSR ile `lambda^2/(n_g L)` çaprazlaması | `ModeSpec(group_index_step=...)` |

Üçü de `tidy3d.ModeSpec` ile yereldir; alanların varlığı doğrulandı. Bunlar aynı
zamanda WP4 surrogate'inin makinesidir, yani doğrulama için yazılan kod zaten
gerekiyordu.

### V4 — yakınsama: yapıldı, kısmi geçti

`freq-rung-2` (12 step/λ) vs `freq-rung-3` (14 step/λ), tek değişken grid:

| | değişim | eşik `%5` |
|---|---|---|
| `lambda_0` | `-0.01%` (FSR'nin `%0.42`'si) | geçti |
| `Q_e` | `-1.28%` | geçti |
| `Q_L` | `-6.56%` | **geçmedi** |
| `T_add` | `+53.79%` | **geçmedi** |
| `Q_i` (model A) | `-22.95%` | **geçmedi** |

Rezonans **konumu** yakınsadı; yakınsamayan şey **kayıp kanalları**.
`subpixel` averaging açık olduğuna göre kalan açıklama eğri halka sınırının
Yee ızgarasına oturtulmasıdır — geri saçılma buna çok duyarlıdır.

`16 step/λ` (`~42 FC`) **önerilmedi**; V4 kaçış valfi uygulandı ve değerler
belirsizlikle kabul edildi.

`n_eff` için ızgara yakınsaması **hiç yapılmadı** — mode solver `20 step/λ` ile
tek seviyede çözüldü. Bu ücretsiz olarak kapatılabilir.

Eski `10 → 12 step/λ` karşılaştırması (`+1.45..+1.89 nm` kayma) **geçersiz
sayılmalıdır**: o veri üç observability kusurunun üçünü de içeriyordu.

### V5 — dış çapa: `Q_i` ve `n_eff` için olumlu

Silicon MRR reservoir computing literatüründe karşılaştırılabilir SOI
mikrohalkalar için `Q ≈ 6.5e4` raporlanıyor (Lugnan/Bazzanella hattı; bkz.
`reports/FDTD-001-mrr-feasibility.md` kaynakları). `freq-rung-2`'nin `Q_i`
aralığı (`4.9e4 – 7.1e4`) bu değeri içeriyordu; ancak `freq-rung-3`'te `Q_i`
`%23` değiştiği için o aralık artık **rapor edilmiyor**. V5 sağlaması, bend
mode solver yolundan gelecek `Q_i` için tekrar uygulanacaktır.

`n_eff = 2.4017`, 450 x 220 nm SOI strip için bilinen tipik değerle uyumlu.

Bu bir kanıt değil, sağlamadır — o literatürde parametreler üretilmiş çipten
ölçülüp fit ediliyor, bizde FDTD'den geliyor. Yöntemler farklı.

## Model varsayımları — ölçüm değil

Tabloda görünmeyen ama sonucu belirleyen iki varsayım:

1. **Simetrik kuplaj** (`tau_1 = tau_2`). `Q_e = Q_L / sqrt(T_drop)` bunu
   varsayar. Geometri simetrik olduğu için (iki gap da `0.2 µm`) gerekçelidir,
   ama sınanmamıştır.
2. **Tek modlu TCMT**. Add portunda ölçülebilir güç var (`12 sl`'de `0.097`,
   `14 sl`'de `0.149`) ve tek modlu modelde bu kanal yoktur. `Q_i`'nin
   belirsiz kalmasının sebebi budur. Kanalın **fiziksel büyüklüğü bilinmiyor**:
   iki mesh arasında `%54` değiştiği için sayısal katkı ayrıştırılamadı. Plan
   incelemesindeki R1 (iki modlu CW/CCW port sözleşmesi) hâlâ gerekli, ama
   gerekçesi "ölçülmüş geri saçılma" değil "modelde eksik kanal".

## Sıradaki ücretsiz adımlar

1. `ModeSpec(bend_radius=...)` ile bend `Q_i` → V3 ikinci yolu
2. Even/odd supermode ile `κ` → `Q_e` V3 ikinci yolu
3. `group_index_step` ile `n_g` → FSR çaprazlaması + `n_eff` V3
4. Mode solver ızgara yakınsaması → `n_eff` V4

Dördü de `0 FC` ve dördü de WP4 surrogate'ine doğrudan girdi.
