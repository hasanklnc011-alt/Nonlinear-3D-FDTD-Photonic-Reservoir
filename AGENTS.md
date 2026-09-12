# Nonlinear 3D FDTD Photonic Reservoir — Çalışma Sözleşmesi

## Amaç

Bu depo, Tidy3D ile gerçek malzeme modelleri ve nonlinear elektromanyetik çözüm kullanarak uçtan uca 3D FDTD photonic reservoir geliştirmek içindir. Nihai benchmark NARMA-10'dur; kabul hedefi önceden kilitlenmiş 10 kör seed üzerinde medyan test NMSE < 0.05'tir.

## Kanonik konum ve Git

- Yerel kanonik çalışma alanı: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`
- Uzak kanonik depo: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir.git`
- Yapısal, deneysel ve dokümantasyon değişiklikleri küçük, anlamlı commit'lerle uzak depoya gönderilir.
- API anahtarları, HDF5 sonuçları, büyük önbellekler ve kişisel veriler Git'e eklenmez.

## Ajan işbirliği

- `CLAUDE.md` bu dosyayla eşdeğer içerikte tutulur.
- Bir görev başlamadan önce ilgili plan ve sahiplik yazılır.
- Üretici değişikliğinden sonra diff, test ve provenance kontrolü yapılır; bu
  doğrulama ayrı bir ajana devredilemez, aynı oturumda kanıtıyla yazılır.
- Nihai karar ve birleştirme tek merkezî akışta yapılır; kör test sonucu aday
  seçimine geri beslenmez.

## Aşamalar

1. Yapı ve proje sözleşmesi
2. NARMA-10 veri/baseline kilidi
3. FDTD fizibilite ve maliyet raporu
4. Doğrusal rezonans, mesh ve zaman yakınsaması
5. Kerr/nonlinear doğrulama ve fiziksel çıkış özellikleri
6. Geliştirme seed'leriyle mimari arama
7. Aday kilidi ve 10 seed kör değerlendirme

## Kanıt kuralları

- Tidy3D task kimliği, sürüm, geometri/malzeme hash'i, mesh, run time ve tahmini/gerçek FlexCredit maliyeti kaydedilir.
- Reduced-order/TCMT sonuçları yardımcı kanıttır; uçtan uca 3D FDTD sonucunun yerine geçmez.
- Sonlu olmayan veri, yakınsamayan çözüm veya doğrulanmamış malzeme parametresi kabul edilmez.
- Ücretli solve öncesi maliyet raporu ve açık görev kaydı gerekir.

## Değişiklik protokolü

Dosyayı değiştirmeden önce oku. Her anlamlı oturum sonunda `docs/decisions/`, `CHANGELOG.md` ve gerekirse `STATUS.md` güncellenir. Kod başlamadan önce `docs/PROJECT-CHARTER.md` tamamlanır.
## Raporlar

Teknik, maliyet, FDTD doğrulama ve benchmark raporları `reports/` altında tutulur.

## Backlog ve yarım kalan işler

- Bir iş herhangi bir nedenle yarıda kalırsa aynı oturumda `BACKLOG.md` içine yazılır.
- Her backlog maddesi sahip, tarih, durum, bağlam, değişen dosyalar ve sıradaki tek adımı içerir.
- İş tamamlandığında `BACKLOG.md` maddesi kapatılır; tamamlanma, karar ve geçiş izi `BACKLOGLOG.md` içine eklenir.
- Backlog temizlenmeden oturum kapatılmaz; gerçek bir engel varsa madde açık ve engel ayrıntılı bırakılır.
## Proje sabitleri

Genel ve değişmez proje gerçekleri [`const.md`](const.md) dosyasında tutulur. Her görev başlangıcında okunur; değişiklik gerekiyorsa önce karar kaydı açılır.
## Rol dağılımı — tek operatör (2026-09-13'ten itibaren kalıcı)

- Bu depoda tek ajan çalışır: Claude. Hem karar/mimari hem kod/test/yerel
  doğrulama rolünü üstlenir. ChatGPT/Astra orkestra şefliği **kalıcı olarak
  kaldırılmıştır** — askıya alma değil, sözleşmeden çıkarma.
- Her karar `docs/decisions/` içine gerekçesiyle yazılır. Tek operatör olmak
  kanıt yükünü azaltmaz; aksine denetleyecek ikinci ajan olmadığı için karar
  kaydı ve test kanıtı tek denetim mekanizmasıdır.
- Claude, mimariyi ve benchmark protokolünü değiştirebilir; ancak `const.md`
  sabitlerini veya kilitli NARMA-10 kör-değerlendirme protokolünü değiştiren
  her adım önce `docs/decisions/` içinde karar kaydı açar ve Hasan'ın açık
  onayını bekler.
- Claude, Tidy3D cloud'dan **tamamlanmış task sonuçlarını indirebilir ve
  değerlendirebilir** (indirme ek ücret doğurmaz).
- Fleet skill'leri bu projede gerekli değildir; ajan kendi harness'ını kullanır.

### Değişmeyen sınır

Ücretli Tidy3D solve başlatmak (yeni task submit, yeni FlexCredit harcaması)
yalnız **Hasan'ın açık onayıyla** yapılır. Tek operatöre geçiş bu onay
gereğini kaldırmaz. Her ücretli solve öncesi `estimate_cost` üst sınırı
yazılı olarak raporlanır.
