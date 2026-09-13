# FlexCredit defteri — mrr-linear-001

Tidy3D cloud'dan `realFlexUnit` ile doğrudan okundu (`web.get_tasks` +
`web.get_info`), kayıtlardan toplanmadı. Son güncelleme: 2026-09-13.

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
| **TOPLAM** | **60.9646** | |

## Devam eden

| `mrr-linear-001-freq-rung-3-estimate-only` | tahmin 22.8463, tavan 23, beklenen gerçek `~16.6` |
|---|---|

Tamamlanınca beklenen proje toplamı: **`~78 FC`**.

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
