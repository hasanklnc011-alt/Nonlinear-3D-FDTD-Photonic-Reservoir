# FlexCredit defteri — mrr-linear-001

Tidy3D cloud'dan `realFlexUnit` ile doğrudan okundu (`web.get_tasks` +
`web.get_info`), kayıtlardan toplanmadı. Son güncelleme: 2026-09-13.

## Bakiye ve tahsis (2026-09-13)

Cloud'dan `Account.get()` ile okundu.

```
bakiye (2026-09-13, rung-3 sonrasi)  115.7358 FC   son kullanma 2027-04-29
aylik ek hak                           0.00        (cycle sonu 2026-09-30)
gunluk ucretsiz simulasyon             0
toplam harcanan                       79.0726
```

Harcanan `79.0726` + bakiye `115.7358` → başlangıç bütçesi **`~195 FC`**;
bugüne kadar **`%41`** kullanılmış.

### Tahsis planı

```
  Q_i / Q_e / n_eff ikinci yollari    0   yerel mode solver (V3)
  WP4 surrogate dogrulama            35   2-3 nokta 3B FDTD
  WP6 nihai kilit                    20   REZERVE, dokunmak ayri karar
  ---------------------------------------
  planlanan                          55
  pay                               ~62   belirsizlik icin
```

### Sözleşmeye bağlanan kurallar

`AGENTS.md` §Bütçe ve bakiye:

- Her ücretli solve öncesi bakiye ve tahsis **kontrol edilip rapora yazılır**.
  Bakiyeyi bilmeden tavan önerilmez.
- Tek koşu `25 FC`'yi aşamaz.
- WP6 rezervi `20 FC`, dokunmak ayrı karar gerektirir.
- Kalan bakiye `60 FC` altına inerse yeni koşu için ayrı karar gerekir.
- Doğrulama amaçlı harcama proje toplamının `%25`'ini aşarsa ayrı karar.

**Bu kural neden var:** 2026-09-13'te `freq-rung-3` için `23 FC` tavanı
önerilirken bakiye hiç kontrol edilmemişti. Tavan, bilinmeyen bir bakiyenin
üstüne önerildi. Kural bu hatayı tekrarlanamaz kılmak için yazıldı.

## Tamamlanmış koşular

| task adı | gerçek FC | ne için |
|---|---|---|
| `mrr-linear-001-time-rung-est-90ps` | 5.1770 | zaman yakınsaması (decay `1.53e-05`, geçmedi) |
| `mrr-linear-001-time-rung-est-105ps` | 5.3944 | zaman yakınsaması (decay `7.05e-06`, geçti) |
| `mrr-linear-001-pml-16layers-estimate-only` | 5.9777 | PML yakınsaması (12 vs 16 katman, geçti) |
| `mrr-linear-001-mesh-12steps-estimate-only` | 10.7165 | mesh-rung-1, 12 step/λ @ 105 ps (geçmedi) |
| `mrr-linear-001-mesh12-time-est-150ps` | 11.4329 | mesh-rung-2, zaman kapısı geçti |
| `mrr-linear-001-freq-rung-1-estimate-only` | 11.5346 | yoğun frekans tarağı, `Q_L` çözüldü |
| `mrr-linear-001-freq-rung-2-estimate-only` | 10.7316 | facet'siz + dört port, `Q_e` ölçüldü |
| `mrr-linear-001-freq-rung-3-estimate-only` | 18.1080 | 14 step/λ mesh yakınsaması (3/4 ölçüt geçti) |
| **TOPLAM** | **79.0726** | |

## Devam eden

Yok. `freq-rung-3` yakınsama amaçlı **son** ücretli koşuydu; bundan sonraki FDTD
harcaması yalnız WP4 surrogate doğrulaması ve WP6 nihai kilit içindir.

## Düzeltme — daha önce yanlış rapor edilmişti

`docs/decisions/2026-09-13-freq-rung-3-plan.md` ilk yazıldığında
"önceki rung'lar `~44.4`" ve "proje toplamı bu koşuyla `~61 FC` olur" deniyordu.
**Bu yanlıştı.** Hata, `docs/decisions/2026-09-13-freq-rung-1-evaluation.md`
§7'deki "time-rung 1/2/3 + PML + mesh-rung-1 ≈ `18.6`" satırının cloud'dan
doğrulanmadan, önceki metin kayıtlarından tahmin edilmesinden kaynaklandı;
gerçek değer `27.3`. Sapma `~17 FC`, yani **`%28` eksik bildirim**.

Gerçek durum: koşu başlamadan önce zaten `60.96 FC` harcanmıştı ve
`freq-rung-3` toplamı `~78 FC`'ye çıkaracak — Hasan'a sunulan `~61 FC`
rakamının değil.

Bu dosya bundan sonra tek doğru kaynaktır; harcama rakamı metin kayıtlarından
değil, buradan (ve nihayetinde cloud'dan) alınır.

## Not

`time-rung-1` (30 ps, kayıtlarda `1.7888 FC`) ve `rung-0` (tahmin `0.6261 FC`)
bu listede görünmüyor; task'ları cloud listesinde bulunamadı (silinmiş veya
sorgu penceresinin dışında). Eğer gerçekten harcandılarsa toplam `~2.4 FC`
daha yüksektir. Yukarıdaki `60.9646` bu nedenle bir **alt sınırdır**.
