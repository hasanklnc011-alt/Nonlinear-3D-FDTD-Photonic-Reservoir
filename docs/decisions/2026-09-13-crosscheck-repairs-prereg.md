# 2026-09-13 — Çapraz kontrol onarımları: ÖN KAYIT (sonuçlar görülmeden yazıldı)

- Yapan: Claude Opus 5
- Maliyet: `0 FlexCredit`
- Kural: `AGENTS.md` V3 — *bir çapraz yol uyuşmazlığı bulunduğunda, yapılacak
  düzeltme uyuşmayı kontrol etmeden önce yazılır.*

Bu belgenin **§Tahminler** bölümü, hesaplar çalıştırılmadan önce yazılmıştır.
Sonuçlar §Sonuçlar bölümüne eklenecek ve tahminlerle karşılaştırılacaktır.

## Onarım 1 — mod seçici

**Kusur:** seçici yalnız çekirdek güç oranına bakıyor ve farklı
çözünürlüklerde farklı modu seçiyor (`n_eff` V4 salınımı; BOX taramasında
`2.0 µm` aykırılığı).

**Düzeltme:** seçici artık (a) polarizasyon fraksiyonunu (`TE` baskın) ve
(b) çekirdek güç oranını birlikte kullanacak; ayrıca seçilen modun `n_eff`'i
bir önceki çözünürlükteki değere en yakın olan olacak (süreklilik takibi).

Bu, FDTD'ye uydurma değildir — aracın kendi hatasının giderilmesidir ve
FDTD'ye hiç bakılmadan da yapılması gerekirdi.

**Tahmin:** düzeltilmiş seçiciyle `n_eff`, `16 → 32 step/λ` boyunca tek düze
ve `%0.5`'ten küçük değişimle yakınsayacak; `26 step/λ` aykırılığı kaybolacak.

## Onarım 2 — `Q_e` faz uyumsuzluğu

Şimdiye kadar iki hata düzeltildi (ikisi de sonuçtan bağımsız doğrulanabilir):

- **A:** `L_eff = sqrt(pi*R/gamma)` → `sqrt(2*pi*R/gamma)`. Gerekçe: aralık
  profili `g(z) ≈ g0 + z²/(2R)` olduğundan `∫exp(-γz²/2R)dz = sqrt(2πR/γ)`.
  Aritmetik hata.
- **B:** `gamma`'da even supermode indeksi yerine **tek** waveguide `n_eff`'i.
  Gerekçe: aralıktaki alan sönümünü tek kılavuzun modu belirler.

Bunlar `Q_e`'yi `44 750 → 19 660`'a indirdi (FDTD'ye oran `3.67x → 1.61x`).

**Şimdi eklenecek — C:** bükülmüş halka modu ile düz bus modu arasındaki faz
uyumsuzluğu. Gauss profilli kuplajda katsayı
`exp(-Δβ² R / (2γ))` ile çarpılır, `Δβ = k0 (n_ring − n_bus)`.

**Tahmin (C):** `n_ring = 2.36863` (R=4.775 bend) ve `n_bus = 2.36698` ölçüldü,
yani `Δn ≈ 1.65e-03` — çok küçük. Faz uyumsuzluğu çarpanının `1`'e çok yakın
çıkmasını, dolayısıyla `Q_e`'yi **ihmal edilebilir ölçüde artırmasını**
bekliyorum. Yani **kalan `1.6x` uyuşmazlığını KAPATMAYACAK**, hatta çok az
açacak.

Bu tahmini şimdiden yazıyorum ki, C uyuşmayı kapatırsa bunun sürpriz olduğu
belli olsun.

## Onarım 3 — kontrol: `kappa`'nın gap bağımlılığı

**Amaç:** supermode yolunun kendisinin sağlamasını yapmak (V2).
`kappa` gap ile **üstel** azalmalıdır. `gap = 0.15 / 0.20 / 0.25 / 0.30 µm`
için `kappa` hesaplanacak ve `ln(kappa)` vs `gap` doğrusal mı bakılacak.

**Tahmin:** `ln(kappa)` gap'e karşı doğrusal çıkacak ve eğimi `−2γ ≈ −15.3 1/µm`
mertebesinde olacak. Çıkmazsa supermode yolu güvenilmez demektir ve `Q_e`
tartışmasında ağırlığı düşer.

## Kabul edilen sınır — peşinen

Kalan uyuşmazlığı kapatmak için **gerekçesiz bir çarpan konulmayacaktır.**
A, B, C ve kontrol uygulandıktan sonra fark sürerse, `Q_e` iki yolu da
kapsayan bir **aralıkla** raporlanacaktır. Belirsizliği yazmak meşru,
yok etmek için uydurmak değildir.

## EK ÖN KAYIT — Onarım 4 (Onarım 1 çürüdükten sonra yazıldı)

Onarım 1'in tahmini **tutmadı**: düzeltilmiş seçici (polarizasyon + süreklilik)
her dört çözünürlükte de aynı modu buluyor (`mode#7`, `TE %97-98`, çekirdek
`%58-62`) ama `n_eff` yine `26 step/λ`'da `2.2987`'ye sıçrıyor. Yani kusur
seçicide değil, çözümün kendisinde.

**Yeni hipotez:** kesit düzlemindeki `2 µm` Si substrate, `n_eff` ekseninde
sıkışık bir mod ailesi taşıyor; bu modların konumu ayrıklaştırmayla kayıyor ve
biri waveguide moduna yaklaştığında **hibritleşme (anti-crossing)** oluyor.
Destekleyen gözlem: doğru mod BOX taramasında `mode#5`, burada `mode#7` —
substrate modları indeks sırasını sürekli değiştiriyor.

**Tahmin (Onarım 4):** substrate tamamen kaldırılıp aynı tarama
(`16/20/26/32 step/λ`) tekrarlandığında `n_eff` **tek düze** ve toplam yayılım
**`%0.5`'ten küçük** olacak; `26 step/λ` sıçraması kaybolacak.

Çıkmazsa bu hipotez de düşer ve sorun mode solver kurgusunun daha temel bir
yerindedir.

---

## Sonuçlar

*(hesaplar çalıştırıldıktan sonra doldurulacak)*
