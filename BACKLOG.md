# Backlog

Kanonik sıra: [Kurtarma ADR](docs/decisions/2026-09-13-optical-chain-recovery-plan.md). Geçmiş: BACKLOGLOG.md.

Güncel sıra: K2s → K1 → K2; K2a fiziksel kabul/arama öncesi. Hedef dosyalar, CLI, şemalar ve kabul: [uygulama sözleşmesi](docs/decisions/2026-09-14-recovery-implementation-contract.md). Değişen dosyalar gerçekleşen diff kaydıdır; hedef yollar ek sözleşmededir.

## [K1] Mode tanısı
- Sahip: Claude (kod, test ve uygulama kanıtı); Codex yalnız hedef/sözleşme dokümantasyonu.
- Tarih: 2026-09-13
- Durum: OPEN
- Bağımlılık: K0
- Teslimat ve kabul: ADR K1 bölümü.
- Değişen dosyalar: henüz yok.
- Engel: ilgili kabul kapıları / ücretli solve onayı.
- Sıradaki adım: Tanıyı tekrar üret; izole subpixel ortamını doğrula.

## [K2] TCMT ve güvenli scorer
- Sahip: Claude (kod, test ve uygulama kanıtı); Codex yalnız hedef/sözleşme dokümantasyonu.
- Tarih: 2026-09-13
- Durum: OPEN
- Bağımlılık: K0
- Teslimat ve kabul: ADR K2 bölümü.
- Değişen dosyalar: henüz yok.
- Engel: ilgili kabul kapıları / ücretli solve onayı.
- Sıradaki adım: Enerji-normalize çekirdek ve aday paketini uygula.

## [K3] Açık coupler
- Sahip: Claude (kod, test ve uygulama kanıtı); Codex yalnız hedef/sözleşme dokümantasyonu.
- Tarih: 2026-09-13
- Durum: OPEN
- Bağımlılık: K1 + K2 fizik testleri
- Teslimat ve kabul: ADR K3 bölümü.
- Değişen dosyalar: henüz yok.
- Engel: ilgili kabul kapıları / ücretli solve onayı.
- Sıradaki adım: Kapılar geçince nominal hücre ve maliyet raporu hazırla.

## [K4] Tam halka bridge
- Sahip: Claude (kod, test ve uygulama kanıtı); Codex yalnız hedef/sözleşme dokümantasyonu.
- Tarih: 2026-09-13
- Durum: OPEN
- Bağımlılık: K3
- Teslimat ve kabul: ADR K4 bölümü.
- Değişen dosyalar: henüz yok.
- Engel: ilgili kabul kapıları / ücretli solve onayı.
- Sıradaki adım: Bileşen spektrumu ön kaydı ve ortak monitor kurgusu hazırla.

## [K5] Dev arama ve kör test
- Sahip: Claude (kod, test ve uygulama kanıtı); Codex yalnız hedef/sözleşme dokümantasyonu.
- Tarih: 2026-09-13
- Durum: OPEN
- Bağımlılık: K2; fiziksel kabul için K4
- Teslimat ve kabul: ADR K5 bölümü.
- Değişen dosyalar: henüz yok.
- Engel: ilgili kabul kapıları / ücretli solve onayı.
- Sıradaki adım: Kaynaklı sınırlar olmadan arama açma.

## [K2s] Kör-test güvenliği — İLK İŞ
- Sahip: Claude.
- Durum: OPEN.
- Bağımlılık: K0.1.
- Teslimat ve kabul: uygulama sözleşmesi K2s bölümü.
- Sıradaki adım: Sentetik suite ile gerçek scorer, V2 kilit, atomik tüketim ve yarış/çökme regresyonları; gerçek kör suite kapalı.

## [K2a] Kaynaklı malzeme/carrier/termal ve proses kaybı
- Sahip: Claude.
- Durum: OPEN.
- Bağımlılık: Fiziksel kabul ve K5 öncesi; sentetik K2 testlerinden bağımsız.
- Teslimat ve kabul: uygulama sözleşmesi K2a bölümü.
- Sıradaki adım: Evidence tablosu ve provenance manifesti; kaynak bulunamayan satırlar unresolved.

## [B25] Tarihsel %25 bütçe eşiği
- Sahip: Claude (döküm); harcama kararı Hasan.
- Durum: OPEN.
- Bağımlılık: Her yeni ücretli solve öncesi; ücretsiz işler serbest.
- Teslimat ve kabul: uygulama sözleşmesi B25 bölümü.
- Sıradaki adım: Claude task bazlı döküm/istisna önerisi hazırlar; Hasan açık kararı olmadan kapanmaz.

## Plan 2 — ayrı Kerr araştırma hattı

Kanonik karar: [Plan 2](docs/decisions/2026-09-14-plan2-kerr-reservoir.md).
Ortak K2s ve B25 geçerlidir; önceki K işleri korunur.

### [PLAN2-P0] Araştırma ve benchmark sınırı
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: doküman kaydı hazır; teknik kabul OPEN.
- Bağımlılık: Ortak K2s, ortam ve kayıt doğrulaması.
- Teslimat/kabul: Plan 2 ADR P0 bölümü.
- Sıradaki adım: Sürüm/hash ve benchmark protokolünü somutlaştır.

### [PLAN2-P1] Platform ve güç fizibilitesi
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P0 kayıt biçimi.
- Teslimat/kabul: Plan 2 ADR P1 bölümü.
- Sıradaki adım: Si3N4/SiO2 ve AlGaAsOI kaynak tablosu; nihai seçim P3 sonrası.

### [PLAN2-P2] Dinamik çekirdek
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P0; sentetik test için P1 kabulü gerekmez.
- Teslimat/kabul: Plan 2 ADR P2 bölümü.
- Sıradaki adım: 20 slot / iki fiziksel güç / 40 özellik; analitik testler.

### [PLAN2-P3] Nonlinearlik-bellek bölgesi
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P1 kaynak kapısı ve P2 testleri.
- Teslimat/kabul: Plan 2 ADR P3 bölümü.
- Sıradaki adım: Her platform/mimaride 256 ön kayıtlı Sobol noktası.

### [PLAN2-P4] Angler geometri tasarımı
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P0/P1/P2 ilk teslimatlar ve P3 hedef bölgesi.
- Teslimat/kabul: Plan 2 ADR P4 bölümü.
- Sıradaki adım: FEMwell kesitinden 2B–3B normalizasyonu kur.

### [PLAN2-P5] Geometrik dayanıklılık
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P4 geometri-model paketi.
- Teslimat/kabul: Plan 2 ADR P5 bölümü.
- Sıradaki adım: 64 ön kayıtlı senaryo; en az 58 medyan geçmeli.

### [PLAN2-P6] 3B ve kör nihai test
- Sahip: Claude (uygulama/test/kanıt); Codex yalnız dokümantasyon.
- Durum: OPEN.
- Bağımlılık: P5, K2s, B25, maliyet/solve onayı.
- Teslimat/kabul: Plan 2 ADR P6 bölümü.
- Sıradaki adım: Önce maliyet/kanıt planı; final EM sonrası dev/dayanıklılık tekrar.
