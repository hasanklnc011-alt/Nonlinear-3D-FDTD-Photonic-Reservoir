# Nonlinear 3D FDTD Photonic Reservoir — Çalışma Sözleşmesi

## Amaç

Bu depo, Tidy3D ile gerçek malzeme modelleri ve nonlinear elektromanyetik çözüm kullanarak uçtan uca 3D FDTD photonic reservoir geliştirmek içindir. Nihai benchmark NARMA-10'dur; kabul hedefi önceden kilitlenmiş 10 kör seed üzerinde medyan test NMSE < 0.05'tir.

## Kanonik konum ve Git

- Yerel kanonik çalışma alanı: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`
- Uzak kanonik depo: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir.git`
- Yapısal, deneysel ve dokümantasyon değişiklikleri küçük, anlamlı commit'lerle uzak depoya gönderilir.
- API anahtarları, HDF5 sonuçları, büyük önbellekler ve kişisel veriler Git'e eklenmez.

## ChatGPT + Claude işbirliği

- Her iki ajan aynı sözleşmeye uyar; `CLAUDE.md` bu dosyayla eşdeğer içerikte tutulur.
- Bir görev başlamadan önce ilgili issue/plan ve sahiplik yazılır.
- Ajanlar aynı dosyada eşzamanlı yazmaz; üretici değişikliği sonrası doğrulayıcı diff, test ve provenance kontrolü yapar.
- Nihai karar ve birleştirme tek merkezî akışta yapılır; kör test sonucu aday seçimine geri beslenmez.

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
## Astra → Claude görev dağılımı

- Astra, `gpt-6-astra` ve `low` çabasıyla orkestra şefidir: amaç, mimari, kabul ölçütleri, görev sırası ve nihai kararları belirler.
- Claude, `claude-sonnet-5` ve `high` çabasıyla uygulayıcıdır: Astra'nın onayladığı görevleri kodlar, testleri çalıştırır ve sonuçları raporlar.
- Claude mimariyi veya benchmark protokolünü tek başına değiştirmez; önerilerini `BACKLOG.md` veya `docs/coordination/` içine yazar.
- Astra, Claude'un diff'ini, test kanıtını, fiziksel varsayımlarını ve maliyetini incelemeden işi kabul etmez.
- Fleet skill'leri bu projede gerekli değildir. Ajanlar kendi mevcut harness ve varsayılan araçlarını kullanır.
- Tidy3D cloud submission, task başlatma ve sonuç indirme yalnız Codex/Astra sorumluluğundadır; Claude yalnız kod ve yerel doğrulama yapar.

## Geçici mod: Astra devre dışı (2026-09-11'den itibaren)

- Hasan'ın ChatGPT/Astra kredisi bitti; Astra bu depoda **geçici olarak devre
  dışı**. Yukarıdaki "Astra → Claude görev dağılımı" bölümü hâlâ kanonik
  sözleşmedir ve Astra geri döndüğünde otomatik olarak yeniden yürürlüğe girer
  — silinmedi, yalnız askıya alındı.
- Bu süre boyunca Claude Sonnet 5 **hem karar/mimari hem de kod/test/yerel
  doğrulama** rolünü tek başına üstlenir. Kararlar Astra onayı olmadan
  `docs/decisions/` içine kaydedilir; ne karar verildiği ve neden açıkça
  yazılır ki Astra geri döndüğünde denetleyebilsin.
- Değişmeyen sınır: Tidy3D cloud submission / ücretli solve başlatma yalnız
  Hasan'ın açık onayıyla yapılır (bkz. sistem talimatındaki explicit-permission
  kuralı). Astra'nın yokluğu bu onay gereğini kaldırmaz.
- Bu geçici moddan çıkış: Hasan Astra'yı yeniden aktif ettiğini bildirdiğinde,
  bu bölüm `BACKLOGLOG.md`'ye kapanış kaydıyla taşınır ve orkestra şefliği
  Astra'ya döner.
