# Kör suite Kerr-Ring-Reservoir deposuna taşındı

- Durum: KABUL EDİLDİ (Hasan, 2026-09-14).
- Hedef depo: `Kerr-Ring-Reservoir` (Plan 2 Kerr hattı).

## Karar

Plan 2 Kerr hattı ayrı bir depoya taşındı. Kör suite **taşındı, kopyalanmadı**:
10 kör seed'in tek meşru değerlendirme yolu artık hedef depodur. Bu depoda
`blind-eval` CLI komutu, kök dizindeki `BLIND-SUITE-MOVED.md` mevcut olduğu
sürece fail-closed reddeder.

Benchmark kimliği, sabitler ve seed hash'leri iki depoda aynıdır; bu
karşılaştırılabilirlik içindir, iki değerlendirme hakkı anlamına gelmez.

## Etkilenmeyenler

- Geliştirme (dev) seed'leri, `baseline`, `verify-manifests`, `preflight`
  ve tüm testler bu depoda çalışmaya devam eder.
- K0–K5 silikon kurtarma hattı bu depoda devam eder. K5'in nihai kör
  değerlendirmesi, hedef depodaki tek suite üzerinden ve tek nihai aday
  olarak yapılır.

## Ortak kalanlar

FlexCredit bütçesi, 60 FC taban / 25 FC tek koşu / 20 FC final rezerv ve
B25 kararı iki depo için ortaktır. İki depo ayrı bütçe veya ayrı kör hak
kazanmaz.

## Devralınan açık bug

`cmd_blind_eval` gerçek kilitli scorer yerine `baseline_delay_scorer` çağırıyor
ve tüketim skordan sonra, atomik olmadan kaydediliyor. Bu kusurlar hedef
depoya olduğu gibi taşındı ve orada `G0` olarak açıktır; bu depoda düzeltilmez.
