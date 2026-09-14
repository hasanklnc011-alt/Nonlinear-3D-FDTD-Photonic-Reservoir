# Nonlinear MRR — çalışma sözleşmesi

Kanonik karar: [docs/decisions/2026-09-13-optical-chain-recovery-plan.md](docs/decisions/2026-09-13-optical-chain-recovery-plan.md). Önce const.md, bu ADR, BACKLOG.md ve parametre durumunu oku.

## Amaç

Geometriyle sınırlandırılmış, FDTD-kalibre TCMT reservoir. İlk aile 450×220 nm,
R_center=4.775 µm, simetrik iki bus, gap 150–250 nm. Global surrogate ertelendi.
Geometri → eigenmode → açık coupler S → round-trip → CW/CCW TCMT.
NARMA-10: 5 development, 10 blind; medyan blind NMSE <0.05 ve >=8/10 başarı.
200/3000/2000 split ve veri hash'leri değişmez; kör skor tuning'e dönmez.

## Kaynak ve kanıt

- Geometriye bağlı optik parametreler EM ölçümünden; malzeme/carrier/termal girdiler kaynaklı veriden.
- Kayıpsız geometri kontrol modelidir. kappa_i=rad+abs+scatter; ısı yalnız absorpsiyondan.
- Her sonuç kaynak/config/geometri/malzeme/grid/solver ve artifact digest'i taşır.
- Yerel mode solve için task_id yoksa local run ID, ortam ve veri hash'i gerekir; cloud task ID uydurulmaz.
- V1: tüm ilgili portlar+radyasyon+absorpsiyon dengesi; rezonans dahil, artık <1e-3.
- V2: analitik limit/kontrol; V3: bağımsız yöntem. Aynı koşunun iki portu yalnız iç tutarlılıktır.
- FSR grup gecikmesine çapadır, doğrudan n_eff doğrulaması değildir.
- V4: ADR'deki observable'a özgü mesh/domain/time ve uç-geometri testleri. İki mesh farkı güven aralığı değildir.
- Belirsizlik istisnası yalnız gerekçeli hata zarfı ve görev duyarlılığı ile; eksik fizik/tanımlanamazlık kabul edilmez.
- V5 dış çapa destekleyicidir, diğer kapıların yerine geçmez.
- Exploratory/synthetic sonuçlar fiziksel kabul veya blind lock alamaz.

## Sahiplik ve çalışma

- Rol sınırı (Hasan, 2026-09-14): Codex yalnız proje hedefleri, sözleşmeler, kararlar ve backlog dokümanlarını düzenler. Uygulama kodunu ve testlerini Claude yazar.
- Tek uygulama sahibi Claude; aynı dosyalarda eşzamanlı yazma yok. K0 dokümantasyon teslimatı, K1–K5 uygulamasının tamamlandığı anlamına gelmez.
- İlgili işi BACKLOG'da sahiplen; aynı dosyada eşzamanlı yazma yapma. İnceleme salt okunur olabilir.
- AGENTS.md ve CLAUDE.md byte-identical tutulur. Değiştirmeden önce dosyayı oku.
- Her teslimatı aynı oturumda diff/test/provenance ile doğrula; küçük commit ve normal origin/main push yap.
- Önce git fetch/status; başkasının değişikliğini ezme, force-push yok.
- Kapanan iş BACKLOGLOG'a; açık/engelli iş BACKLOG'a, önemli değişiklik CHANGELOG'a kaydolur.
- Eski kararlar tarihçedir; yeni ADR ile çelişen hükümler güncel talimat değildir.
- Sırlar/HDF5/gptpro/ Git'e alınmaz. API anahtarları okunmaz veya yazdırılmaz.

## Bütçe

Yerel 0, uzak mode 2, coupler 10, bridge 15, final rezerv 20 FC: toplam 47 FC.
Canlı bakiye ve taahhütler her ücretli adımda kontrol edilir; kaynak FLEXCREDIT-LEDGER.
Tek koşu <=25 FC, bakiye >=60 FC; final 20 FC rezerv başka işe aktarılmaz.
Geçmiş doğrulama %25 eşiğini aşıyor olabilir; yeni ücretli adım öncesi ayrı karar gerekir.
Tahsis solve onayı değildir: her ücretli solve yazılı estimate_cost ve Hasan'ın açık onayını ister.
K0/K1/K2 teslimatları görülmeden ücretli coupler yok. Tamamlanmış cloud sonucu okunabilir.

## Araştırma hattı bağlantıları

- [[docs/PROJECT-CHARTER|Proje sözleşmesi]]
- [[docs/decisions/2026-09-13-optical-chain-recovery-plan|Kurtarma hattı]]

## Güncel uygulama devri

[2026-09-14 ek sözleşme](docs/decisions/2026-09-14-recovery-implementation-contract.md) önceliklidir: K2s kör-test güvenliği ilk iş; K2a kaynak girdileri ve B25 bütçe kararı ayrı kapılardır. Gerçek kör suite K2s kapanmadan çalıştırılmaz.

## Plan 2 kapsamı (2026-09-14)

[Plan 2 Kerr ADR](docs/decisions/2026-09-14-plan2-kerr-reservoir.md) ayrı araştırma hattını tanımlar.
Eski silikon geometri kısıtları bu hatta uygulanmaz; eski sonuçlar korunur.
Plan 2: Si3N4/SiO2 ve AlGaAsOI adayları, 1550 nm, tek/iki halka,
10 mW ortalama / 100 mW tepe araştırma tavanı, 20 slot × 2 port = 40 özellik.
Kaynaklı keşif EM öncesi yapılabilir; fiziksel kabul/kör kilit için P6 kanıtı gerekir.
Ortak benchmark ve kör suite kopyalanmaz; hatlar arasında yalnız tek nihai kör aday.
Plan 2 için ek 47 FC tahsis edilmedi; bütçe, 20 FC rezerv ve B25 ortaktır.
Kod/test Claude; P0 teknik kabulü ve P1–P6 tamamlanmış değildir.
