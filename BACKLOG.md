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
