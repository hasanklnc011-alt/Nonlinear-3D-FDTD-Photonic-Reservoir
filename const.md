# Proje sabitleri

Bu dosya, proje boyunca değişmez kabul edilen gerçekleri ve sözleşmeleri içerir. Bir karar bu sabitlerden birini değiştirecekse önce açık bir karar kaydı oluşturulmalıdır.

## Kimlik ve konum

- Proje adı: Nonlinear 3D FDTD Photonic Reservoir
- Yerel kök: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`
- Uzak depo: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir.git`
- Ajanlar: ChatGPT ve Claude

## Bilimsel sözleşme

- Nihai elektromanyetik çözüm Tidy3D ile uçtan uca 3D FDTD olmalıdır.
- Optik çekirdek gerçek malzeme ve doğrulanmış nonlinear model içermelidir.
- Nihai görev NARMA-10'dur.
- Kabul hedefi: 10 kör seed üzerinde medyan test NMSE `< 0.05`.
- Kör test sonucu tuning için geri beslenemez.
- TCMT/reduced-order sonuçları yardımcı kanıttır; full 3D FDTD yerine geçmez.

## Süreç sözleşmesi

- Ücretli solve öncesi maliyet ve fizibilite raporu zorunludur.
- API anahtarları, ham HDF5 ve büyük artifact'ler Git'e eklenmez.
- Yarıda kalan işler `BACKLOG.md` içine, kapanış izleri `BACKLOGLOG.md` içine yazılır.
- `AGENTS.md` ve `CLAUDE.md` her değişiklikte birlikte güncellenir.

## Sınır

Fiziksel parametreler, mimari, güç, sembol hızı ve maliyet; kanıt geldikçe raporlarda belirlenir. Bunlar bu dosyanın değişmezleri değildir.
