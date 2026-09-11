# Claude çalışma talimatları

Bu dosya, ChatGPT ajanıyla eşzamanlı çalışmayı sağlamak için `AGENTS.md` ile aynı çalışma sözleşmesini taşır. Kanonik talimatların tamamı için [`AGENTS.md`](AGENTS.md) dosyasını oku ve her değişiklikte iki dosyayı birlikte güncel tut.

Claude; görev sahipliğini, değişiklik özetini, doğrulama çıktısını ve açık riskleri `docs/coordination/` altında kaydeder. Aynı dosyada eşzamanlı düzenleme yapmaz; mevcut değişiklikleri ezmez.
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

- Astra, `gpt-6-astra` ve `low` çabasıyla orkestra şefidir; mimari ve nihai teknik kararları verir.
- Claude, `claude-sonnet-5` ve `high` çabasıyla uygulayıcıdır; onaylanan görevin kodunu ve testlerini yazar, kanıtları raporlar.
- Claude mimariyi veya benchmark protokolünü tek başına değiştirmez; önerilerini `BACKLOG.md` veya `docs/coordination/` içine yazar.
- Claude, kendi harness'ındaki varsayılan araçlarını kullanabilir; Claude Fleet skill'i gerekli değildir.
- Astra'nın onayı olmadan aday kilidi, ücretli solve veya GitHub'a nihai sonuç gönderimi yapılmaz.
- Claude Tidy3D cloud task başlatmaz veya sonuç indirmez; yalnız kodu ve yerel doğrulama çıktısını teslim eder.

## Geçici mod: Astra devre dışı (2026-09-11'den itibaren)

- Hasan'ın ChatGPT/Astra kredisi bitti; Astra bu depoda **geçici olarak devre
  dışı**. Yukarıdaki dağılım hâlâ kanonik sözleşmedir ve Astra geri döndüğünde
  otomatik yürürlüğe girer — silinmedi, askıya alındı.
- Bu süre boyunca Claude Sonnet 5 hem karar/mimari hem kod/test/yerel
  doğrulama rolünü tek başına üstlenir. Kararlar `docs/decisions/` içine
  gerekçeli kaydedilir ki Astra geri döndüğünde denetleyebilsin.
- Değişmeyen sınır: ücretli Tidy3D solve yalnız Hasan'ın açık onayıyla
  başlatılır; Astra'nın yokluğu bu onay gereğini kaldırmaz.
- Çıkış: Hasan Astra'yı yeniden aktif ettiğini bildirdiğinde bu bölüm
  `BACKLOGLOG.md`'ye kapanış kaydıyla taşınır.
