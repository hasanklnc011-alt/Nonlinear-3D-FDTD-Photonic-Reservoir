# Proje sabitleri

Bu dosya, proje boyunca değişmez kabul edilen gerçekleri ve sözleşmeleri içerir. Bir karar bu sabitlerden birini değiştirecekse önce açık bir karar kaydı oluşturulmalıdır.

## Kimlik ve konum

- Proje adı: Nonlinear 3D FDTD Photonic Reservoir
- Yerel kök: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`
- Uzak depo: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir.git`
- Kod/test sahibi Claude; Codex yalnız plan, sözleşme ve değerlendirme dokümantasyonu.

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

## Plan 2 kapsamı (2026-09-14)

[Plan 2 Kerr ADR](docs/decisions/2026-09-14-plan2-kerr-reservoir.md) ayrı araştırma hattını tanımlar.
Eski silikon geometri kısıtları bu hatta uygulanmaz; eski sonuçlar korunur.
Plan 2: Si3N4/SiO2 ve AlGaAsOI adayları, 1550 nm, tek/iki halka,
10 mW ortalama / 100 mW tepe araştırma tavanı, 20 slot × 2 port = 40 özellik.
Kaynaklı keşif EM öncesi yapılabilir; fiziksel kabul/kör kilit için P6 kanıtı gerekir.
Ortak benchmark ve kör suite kopyalanmaz; hatlar arasında yalnız tek nihai kör aday.
Plan 2 için ek 47 FC tahsis edilmedi; bütçe, 20 FC rezerv ve B25 ortaktır.
Kod/test Claude; P0 teknik kabulü ve P1–P6 tamamlanmış değildir.
