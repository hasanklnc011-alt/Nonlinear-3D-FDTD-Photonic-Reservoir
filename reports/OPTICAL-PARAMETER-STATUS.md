# Optik parametre durumu — V1–V5 doğrulama merdiveni

Merdivenin tanımı: `AGENTS.md` §Kanıt kuralları → Doğrulama merdiveni.
Bu dosya, her ölçülmüş optik parametrenin hangi basamakları geçtiğini tutar.
**Hiçbir değer, bu tablodaki durumu yazılmadan TCMT'ye girdi olamaz.**

Son güncelleme: 2026-09-13. Kaynak koşu: `freq-rung-2`
(`fdve-0ecc2c8f-e120-4b3c-8793-c9c0dcbda224`, digest `2032012f...`,
geometry `68867f8d...`, schema `/2`).

## Durum tablosu

| parametre | değer | V1 korunum | V2 kontrol | V3 çapraz yol | V4 yakınsama | V5 dış çapa |
|---|---|---|---|---|---|---|
| `lambda_0` | 1.540945 µm | ✅ | — | ✅ iki port, 46 pm | ⏳ `freq-rung-3` | — |
| `Q_loaded` | 9 797 | ✅ | — | ✅ iki port, `%0.6` | ⏳ `freq-rung-3` | 〰️ |
| `Q_e` (toplam) | 12 260 | ✅ | — | ❌ **tek yol** | ⏳ `freq-rung-3` | — |
| `Q_i` | `4.9e4 – 7.1e4` | ✅ | — | ❌ **tek yol, model bağımlı** | ⏳ | ✅ |
| `n_eff` | 2.4017 | — | ✅ kontrol grubu | ❌ | ❌ **yapılmadı** | ✅ |

Gösterim: ✅ geçti · ❌ geçmedi/yapılmadı · ⏳ koşu devam ediyor · 〰️ kısmi · — uygulanmaz

**Dürüst özet: şu anda hiçbir parametre merdivenin tamamını geçmiş değildir.**
Hiçbiri TCMT'ye nihai girdi olarak kabul edilemez.

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
- `lambda_0`: iki port `46 pm` içinde (bu fark backscattering mod
  yarılmasıyla açıklanıyor, artefakt değil).

**Geçmeyenler ve ikinci yolları (hepsi `0 FC`, yerel):**

| parametre | eksik ikinci yol | araç |
|---|---|---|
| `Q_e` | gap → coupling `κ`, even/odd supermode yarılmasından | iki kuplajlı waveguide mode solve |
| `Q_i` | bend radyasyon kaybı | `ModeSpec(bend_radius=..., bend_axis=...)` |
| `n_eff` | `n_g` → ölçülen FSR ile `lambda^2/(n_g L)` çaprazlaması | `ModeSpec(group_index_step=...)` |

Üçü de `tidy3d.ModeSpec` ile yereldir; alanların varlığı doğrulandı. Bunlar aynı
zamanda WP4 surrogate'inin makinesidir, yani doğrulama için yazılan kod zaten
gerekiyordu.

### V4 — yakınsama: `freq-rung-3` test ediyor

`14 step/λ` koşusu şu an çalışıyor. `freq-rung-2` ile tek farkı grid olduğu için
`lambda_0`, `Q_L`, `Q_e` doğrudan karşılaştırılabiliyor. Eşik: değişim `%5`'ten
küçük.

`n_eff` için ızgara yakınsaması **hiç yapılmadı** — mode solver `20 step/λ` ile
tek seviyede çözüldü. Bu ücretsiz olarak kapatılabilir.

Eski `10 → 12 step/λ` karşılaştırması (`+1.45..+1.89 nm` kayma) **geçersiz
sayılmalıdır**: o veri üç observability kusurunun üçünü de içeriyordu.

### V5 — dış çapa: `Q_i` ve `n_eff` için olumlu

Silicon MRR reservoir computing literatüründe karşılaştırılabilir SOI
mikrohalkalar için `Q ≈ 6.5e4` raporlanıyor (Lugnan/Bazzanella hattı; bkz.
`reports/FDTD-001-mrr-feasibility.md` kaynakları). Bizim `Q_i` aralığımız
`4.9e4 – 7.1e4` bu değeri **içeriyor**.

`n_eff = 2.4017`, 450 x 220 nm SOI strip için bilinen tipik değerle uyumlu.

Bu bir kanıt değil, sağlamadır — o literatürde parametreler üretilmiş çipten
ölçülüp fit ediliyor, bizde FDTD'den geliyor. Yöntemler farklı.

## Model varsayımları — ölçüm değil

Tabloda görünmeyen ama sonucu belirleyen iki varsayım:

1. **Simetrik kuplaj** (`tau_1 = tau_2`). `Q_e = Q_L / sqrt(T_drop)` bunu
   varsayar. Geometri simetrik olduğu için (iki gap da `0.2 µm`) gerekçelidir,
   ama sınanmamıştır.
2. **Tek modlu TCMT**. Girişin `%9.7`'si add portundan çıkıyor
   (`T_add = 0.09691`) — bu, CW/CCW geri saçılmasıdır ve tek modlu modelde
   kanal yoktur. `Q_i`'nin aralık olmasının tek sebebi budur. Plan
   incelemesindeki R1 bu varsayımı kaldırmayı öneriyor.

## Sıradaki ücretsiz adımlar

1. `ModeSpec(bend_radius=...)` ile bend `Q_i` → V3 ikinci yolu
2. Even/odd supermode ile `κ` → `Q_e` V3 ikinci yolu
3. `group_index_step` ile `n_g` → FSR çaprazlaması + `n_eff` V3
4. Mode solver ızgara yakınsaması → `n_eff` V4

Dördü de `0 FC` ve dördü de WP4 surrogate'ine doğrudan girdi.
