# Proje sabitleri

Bu dosya, proje boyunca değişmez kabul edilen gerçekleri ve sözleşmeleri içerir. Bir karar bu sabitlerden birini değiştirecekse önce açık bir karar kaydı oluşturulmalıdır.

## Kimlik ve konum

- Proje adı: Nonlinear 3D FDTD Photonic Reservoir
- Yerel kök: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`
- Uzak depo: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir.git`
- Tek yazıcı: bu kurtarma uygulamasında Codex; devam sahibi Claude (Hasan yetkisi).

## Bilimsel sözleşme

- **Geometriye bağlı optik parametreler full-wave ölçümüyle sınırlandırılır.**
  Kuplaj, rezonans, mod profili ve overlap EM kanıtına bağlıdır. Intrinsic
  kayıp radyasyon + absorpsiyon + proses saçılması olarak ayrılır; malzeme,
  carrier ve termal girdiler kaynaklandırılır. Bilinmeyenler NMSE'ye uydurulmaz.
  Güncel karar: docs/decisions/2026-09-13-optical-chain-recovery-plan.md.
- **Zaman-serisi görev çözücüsü TCMT/rate-equation modelidir.** Girdileri
  yukarıdaki FDTD ölçümleriyle ve kaynak-hash'li malzeme / carrier / termal
  parametreleriyle sınırlıdır.
- Optik çekirdek gerçek malzeme ve doğrulanmış nonlinear model içermelidir.
- Nihai görev NARMA-10'dur.
- Kabul hedefi: 10 kör seed üzerinde medyan test NMSE `< 0.05` ve en az 8/10 seed `<0.05`.
- Kör test sonucu tuning için geri beslenemez.
- **İddia kapsamı:** sonuç "full-wave photonic reservoir" değil, "geometriyle
  sınırlandırılmış, FDTD-kalibre edilmiş TCMT reservoir" olarak sunulur.
  Uçtan uca Maxwell kanıtı bu projede üretilmemektedir.

> Bu maddeler 2026-09-13'te değiştirildi. Önceki hâli uçtan uca 3D FDTD'yi
> zorunlu kılıyor ve TCMT'yi yardımcı kanıt sayıyordu; CFL duvarı ve FCD/FCA'nın
> Tidy3D'de native olmaması nedeniyle o hüküm ulaşılamazdı. Gerekçe ve kabul
> edilen bedel: `docs/decisions/2026-09-13-adr-tcmt-primary-fdtd-calibrator.md`.

## Süreç sözleşmesi

- Ücretli solve öncesi maliyet ve fizibilite raporu zorunludur; FlexCredit
  bakiyesi ve tahsis durumu da aynı raporda kontrol edilir.
- Optik parametreler `AGENTS.md`'deki V1–V5 doğrulama merdiveninden geçmeden
  TCMT'ye girdi olamaz. Belirsizlik istisnası yalnız gerekçeli hata zarfı ve görev duyarlılığıyla
  uygulanır; eksik fizik veya tanımlanamazlık istisna değildir.
- API anahtarları, ham HDF5 ve büyük artifact'ler Git'e eklenmez.
- Yarıda kalan işler `BACKLOG.md` içine, kapanış izleri `BACKLOGLOG.md` içine yazılır.
- `AGENTS.md` ve `CLAUDE.md` her değişiklikte birlikte güncellenir.

## Sınır

Fiziksel parametreler, mimari, güç, sembol hızı ve maliyet; kanıt geldikçe raporlarda belirlenir. Bunlar bu dosyanın değişmezleri değildir.
