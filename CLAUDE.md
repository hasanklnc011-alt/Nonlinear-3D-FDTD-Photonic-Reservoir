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
