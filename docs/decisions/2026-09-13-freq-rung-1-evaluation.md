# 2026-09-13 — freq-rung-1 değerlendirmesi: çizgi çözüldü, `Q_i`/`Q_e` ayrımı GEÇERSİZ

- Task: `fdve-719dd4d0-fed8-4d10-9be8-6c0aab8b047a`
- Durum: `success` | **gerçek maliyet `11.5346 FC`** (tahmin 14.6803, tavan 15)
- Final field decay `9.99e-06`, ~118 ps'de erken shutoff, time-stepping 2479 s
- Veri: `freq_rung1_data.hdf5` (Git'e eklenmez)
- Değerlendiren: Claude Opus 5

## 1. Monitör düzeltmesi amacına ulaştı

| | mesh-rung-2 | freq-rung-1 |
|---|---|---|
| FWHM başına nokta | `~0.1` | **`79.8`** |
| ölçülen `T_drop` tepesi | 0.1108 (ıskalanmış) | **0.13358** |

Rezonans artık tek örnek değil, tam çözülmüş bir çizgi. Kaynak darbesi
değişmediği için maliyet de değişmedi (`11.5346` vs `11.4329 FC`).

## 2. Savunulabilir sonuçlar

İki port **bağımsız olarak** aynı çizgi genişliğini veriyor — bu, sonucun
tek bir monitörün artefaktı olmadığını gösterir:

| | drop tepesi | through çukuru |
|---|---|---|
| `lambda_0` | 1.540909 µm | 1.540955 µm |
| FWHM | 0.1583 nm | 0.1612 nm |
| `Q_loaded` | **9 736** | **9 557** |

- **`Q_loaded` ~ 9 650** (iki port %2 içinde uyuşuyor)
- **Through extinction = 13.56 dB**, yerel baseline'a göre ölçüldüğü için
  mutlak normalizasyondan bağımsız
- Rezonans dalga boyu `1.54091 µm`; kaba koşunun `1.540931`'i ile `~22 pm` içinde

### Ring-down tahmini çürütüldü

`mesh-rung-2` log'undan çıkardığım `Q_loaded ~ 27 500` **yanlıştı**; doğru değer
`~9 650`, yani tahmin `2.8x` yüksekti. Neden: ring-down fit'i (`R^2 = 0.938`)
simülasyondaki *toplam* alan enerjisini ölçüyor ve geç zamanlarda en yavaş
sönen bileşen baskın çıkıyor. O yavaş bileşen bu rezonans değil. Zaten fit'in
`R^2`'sinin düşük olması bunu haber veriyordu; doğrudan çizgi genişliği ölçümü
onu geçersiz kılar. İki bağımsız yöntemin çelişmesi 3. bölümdeki kusuru açığa
çıkardı.

## 3. `Q_i`/`Q_e` ayrımı GEÇERSİZ — enerji dengesi kapanmıyor

Simetrik add-drop TCMT'de `x = sqrt(T_drop)` ve tutarlılık koşulu
`T_through = (1-x)^2` olmalıdır. Ölçüm:

```
x = sqrt(0.13358) = 0.36548
(1-x)^2 = 0.40262      olculen T_through = 0.17698      FARK 0.2256
```

Model uymuyor, dolayısıyla ondan çıkacak `Q_i = 15 247` / `Q_e = 26 470`
sayıları **rapor edilemez**. Kök neden enerji muhasebesi:

| | `through + drop` | ölçülmeyen |
|---|---|---|
| bant kenarı (1.53943 µm) | 0.7738 | **%23** |
| bant kenarı (1.54243 µm) | 0.8843 | **%12** |
| rezonansta | 0.3106 | **%69** |

Rezonans dışında halka ayrıktır, gücün düz bus'tan geçmesi beklenir; yine de
%12–23 kayıp var. **Bu kayıp malzeme emilimi olamaz**: `const.md` uyarınca tüm
ortamlar `conductivity = 0`, non-dispersive. Yani ya radyasyon/sızıntı, ya da
ölçülmeyen bir port.

## 4. Üç tanımlanmış neden

### (a) Monitör yerleşimi — drop portu yanlış uçta

```
kaynak            : bus_through, x = -8, yon '+'
flux:bus_through  : bus_through, x = +8   (dogru: through portu)
flux:bus_drop     : bus_drop,    x = +8   <-- bu ADD portu
```

Eş-yönlü (co-directional) add-drop halkada drop ışığı **geri** yönde, yani
`bus_drop` üzerinde `x = -8` ucunda çıkar. Monitör yanlış uçta. Ayrıca
`bus_through` üzerindeki `x = -8` geri-yansıma portu da izlenmiyor.
Dört portun ikisi ölçülmüyor.

### (b) Buried oxide muhtemelen çok ince

Geometri: BOX `z = 1.5–2.5` (**1.0 µm**), waveguide `z = 2.61`, ve altta
**Si substrate** `z = 0–1.5`. 450 x 220 nm Si waveguide için 1.0 µm BOX,
yüksek indeksli Si substrate'e sızıntıya açıktır; tipik SOI 2–3 µm kullanır.
Bu, rezonans dışı baseline kaybını ve ring-down'daki yavaş bileşeni aynı anda
açıklayabilir. **Hipotez, kanıt değil** — aşağıda ücretsiz testi var.

### (c) Drop tepesi ile through çukuru 46 pm ayrı

FWHM'in `%29`'u kadar kayma. Backscattering kaynaklı mod yarılması veya Fano
girişimi imzası olabilir; yorumlamak için dört portun verisi gerekir.

## 5. Sıradaki adım — ücretsiz, FDTD gerektirmiyor

(b) hipotezi **hiç FlexCredit harcamadan** test edilir: Tidy3D mode solver'ı
yerel çalışır. Bus waveguide kesitinin fundamental modunu mevcut 1.0 µm BOX ile
çöz, `n_eff`'in sanal kısmına ve substrate'e sızan güç oranına bak; sonra aynı
kesiti 2.0 ve 3.0 µm BOX ile tekrarla. Sızıntı gerçekten baskınsa BOX kalınlığı
bir geometri parametresi olarak düzeltilmelidir — bu, `freq-rung-2`'yi yanlış
geometride koşmaktan kurtarır.

Sıralama önerisi:

1. **(ücretsiz)** mode solver ile BOX kalınlığı taraması → sızıntı hükmü
2. **(kod, ücretsiz)** dört-port monitör tokenları: `bus_drop:in` ve
   `bus_through:in` uçlarına flux monitörü; enerji dengesi testi eklenir
3. **(ücretli)** düzeltilmiş geometri + dört port ile tek koşu → `Q_i`/`Q_e`
   ayrımı ilk kez geçerli olur
4. **(ücretli)** ancak ondan sonra 14 step/λ mesh yakınsaması

Adım 3'ten önce mesh merdivenine dönmek anlamsız: yanlış port kurgusu ve
muhtemelen yanlış BOX kalınlığıyla ölçülen `Q` yakınsatılsa da doğru olmaz.

## 6. Araştırma planı taslağına etkisi

`docs/coordination/2026-09-13-astra-tcmt-fdtd-research-plan-review.md` WP4'te
FDTD'yi `Q_i`, `Q_e`, coupling kalibratörü olarak kullanıyor. 4. inceleme
maddesinin cevabı güncellendi: **çizgi genişliği ve dolayısıyla `Q_loaded`
ölçülebilir durumda, ama `Q_i`/`Q_e` ayrımı henüz değil.** Ayrım, port
kurgusu ve BOX kalınlığı kapatılmadan WP4'e girdi olamaz. Bu, planın öngördüğü
"observability riski"nin ikinci somut doğrulamasıdır.

## 7. Harcama kaydı

| rung | gerçek FC |
|---|---|
| time-rung 1/2/3 + PML + mesh-rung-1 | ~~18.6~~ → **27.3** (bkz. düzeltme) |
| mesh-rung-2 | 11.4329 |
| freq-rung-1 | 11.5346 |

`freq-rung-1` tahminin altında kapandı (11.53 < 14.68) çünkü aynı erken
shutoff devreye girdi — tahmin tam `run_time` üzerinden hesaplanıyor.

## DÜZELTME (2026-09-13, denetim sonrası)

Yukarıdaki §7 harcama tablosundaki `~18.6 FC` satırı **yanlıştı**; cloud'dan
doğrulanan gerçek değer `27.3 FC`. Rakam `realFlexUnit`'ten okunmak yerine
önceki metin kayıtlarından tahmin edilmişti. Bu hata
`docs/decisions/2026-09-13-freq-rung-3-plan.md`'ye de taşındı ve orada proje
toplamının `~61 FC` sanılmasına yol açtı; gerçek `~78 FC`.

Doğrulanmış defter: `reports/FLEXCREDIT-LEDGER.md`.
