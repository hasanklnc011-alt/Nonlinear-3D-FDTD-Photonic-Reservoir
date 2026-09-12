# Claude çalışma talimatları

Bu dosya `AGENTS.md` ile aynı çalışma sözleşmesini taşır. Kanonik talimatların tamamı için [`AGENTS.md`](AGENTS.md) dosyasını oku ve her değişiklikte iki dosyayı birlikte güncel tut.

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
## Rol dağılımı — tek operatör (2026-09-13'ten itibaren kalıcı)

- Bu depoda tek ajan çalışır: Claude. Hem karar/mimari hem kod/test/yerel
  doğrulama rolünü üstlenir. ChatGPT/Astra orkestra şefliği **kalıcı olarak
  kaldırılmıştır** — askıya alma değil, sözleşmeden çıkarma.
- Her karar `docs/decisions/` içine gerekçesiyle yazılır; ikinci bir denetleyen
  ajan olmadığı için karar kaydı ve test kanıtı tek denetim mekanizmasıdır.
- Mimari ve benchmark protokolü değiştirilebilir; ancak `const.md` sabitlerini
  veya kilitli NARMA-10 kör-değerlendirme protokolünü etkileyen her adım önce
  karar kaydı açar ve Hasan'ın açık onayını bekler.
- Claude, Tidy3D cloud'dan tamamlanmış task sonuçlarını indirebilir ve
  değerlendirebilir (indirme ek ücret doğurmaz).
- Claude kendi harness'ının varsayılan araçlarını kullanır; Fleet skill'i
  gerekli değildir.

### Değişmeyen sınır

Ücretli Tidy3D solve başlatmak (yeni task submit, yeni FlexCredit harcaması)
yalnız Hasan'ın açık onayıyla yapılır. Her ücretli solve öncesi `estimate_cost`
üst sınırı yazılı olarak raporlanır.
