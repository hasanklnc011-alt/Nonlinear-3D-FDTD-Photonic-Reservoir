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
