# Claude uygulama sözleşmesi — K0.1

Üst karar: [Kurtarma planı](2026-09-13-optical-chain-recovery-plan.md).
Bu ek sıra ve uygulama arayüzlerinde önceliklidir. Kod/test sahibi Claude;
Codex yalnız dokümantasyon. Fizik kapıları henüz açık.

## Sıra

K0.1 doküman devri → K2s kör-test güvenliği → K1 tanı → K2 çekirdek.
K2a kaynak derlemesi fiziksel kabul ve K5 aramasından önce tamamlanır.
Sentetik/analitik K2 testleri K2a olmadan başlayabilir. K3 için K1 ve K2 temel
fizik testleri yanında bütçe/onay kapıları zorunludur.
K2s kapanana kadar gerçek kör suite çalıştırılmaz; regresyonlar geçici sentetik
suite kullanır. Bu operasyon kuralıdır; mevcut kodda teknik engel bulunduğu iddiası değildir.

## Dosya ve arayüz sözleşmesi

Yollar hedef teslimatlardır; henüz uygulanmış sayılmaz. Mevcut fdtd/mrr,
fdtd/provenance, fdtd/tidy3d_build ve evaluate_states tekrar kullanılır.

| İş | Hedef yollar | Arayüz / şema | Kabul |
|---|---|---|---|
| K1 | fdtd/modes/, tests/fdtd/test_modes.py | python -m fdtd.modes diagnose --config PATH --output PATH; mrr-mode-diagnostic/1 | Üst ADR ve aşağıdaki örtüşme |
| K2s | benchmarks/narma10_np/candidate_lock.py, cli.py, preflight.py; tests/narma10_np/test_candidate_lock.py, test_blind_candidate_execution.py | Mevcut lock-candidate/blind-eval; narma10-candidate-lock/2, narma10-blind-ledger/2 | Gerçek scorer, atomik tüketim, bozulma/yarış/çökme testleri |
| K2 | tcmt/, tests/tcmt/ | python -m tcmt simulate --config PATH --output PATH; mrr-tcmt-config/1 | Analitik limit, enerji, sönüm, zaman yakınsaması |
| K2a | docs/evidence/material-carrier-thermal.md, manifests/physics/material-carrier-thermal.json | mrr-physics-evidence/1; mevcut provenance'a adaptör | Kaynak/birim denetimi; eksikler unresolved |
| K3 | fdtd/mrr/coupler.py, fdtd/tidy3d_build/coupler.py, tests/fdtd/test_coupler.py | Mevcut fdtd CLI yapısına coupler altkomutu; mrr-coupler-measurement/1 | Üst ADR kompleks S kapıları |
| K4 | tcmt/roundtrip.py, tests/tcmt/test_roundtrip.py, reports/optical-chain/ | mrr-ring-bridge/1 | Ölçüm öncesi tahmin hash'i ve üst ADR |
| K5 | benchmarks/narma10_np/search.py, tests/narma10_np/test_search.py | Mevcut benchmark CLI'ına dev-search; mrr-search-design/1 | Ön kayıtlı 256 tasarım/64 senaryo |

Ortak manifest: schema, status, units, geometri/malzeme/kaynak/config/ortam içerik
hash'leri, solver/grid/ölçüm ayarları, veri konumu ve SHA-256, üretim komutu,
geçerlilik aralığı, belirsizlik yöntemi ve kapı başına kanıt. Büyük ham veri Git
dışında; küçük manifest/rapor Git'te. Eski şema sessizce kabul statüsü kazanamaz.

## K1 kaynak ve ortam teslimatı

gptpro/ ignored kalır; beş script taşınmaz veya force-add edilmez. Claude yeni
bağımsız tanı modülünü fdtd/modes içinde yazar. Eski scriptlerin SHA-256,
yerel konumları ve yeniden uygulanan/terk edilen işlemler
docs/evidence/legacy-mode-diagnostics.md içinde tutulur. Yeni tanı ignored
script importuna bağlı olamaz. Hash tek başına kaynak içeriğine erişim garantisi değildir.

Ortam teslimatı requirements/mrr-mode.in ve requirements/mrr-mode-win-py314.lock.txt:
tüm çözülmüş bağımlılıklar/paket hash'leri, Python/OS sürümü, kurulum komutu ve
temiz ortam doğrulaması. Başlangıç hedefi Tidy3D+extras 2.12.0, NumPy 2.4.6;
diğer sürümler doğrulanan ortamdan alınır. Import başarısı subpixel etkinliği değildir.
Depo dışındaki hazırlık ortamı doğrulanmadan K1 kabul kanıtı sayılmaz.

Örtüşme elektrik-alan şekil metriğidir:
O = |integral E1* dot E2 dA|² / (integral |E1|² dA integral |E2|² dA).
Üç kompleks E bileşeni ortak fiziksel koordinatlara taşınır. Aynı geometrinin
iki çözümünün PML dışı ortak kesitinde ince grid koordinatları, lineer
interpolasyon ve alan ağırlıklı trapez integrali kullanılır; ekstrapolasyon yoktur.
Bu pozitif L2 metriği güç ortogonalliği veya bağımsız fizik doğrulaması değildir.
O>0.99 ardışık mesh çiftlerinde ve her mesh'in sıfır/±1e-12 um öteleme
çiftlerinde aynı fiziksel dal için aranır; küresel fazdan bağımsızdır.
Yakın dejenere çiftte parity dalı ayıramazsa tek-mod kapısı kapanmaz;
altuzay benzerliği yalnız ek tanıdır. Çekirdek/polarizasyon koşulları korunur.

Domain/PML kök neden ilan edilmez. Sabit-grid arayüz tanısı önce tekrarlanır.
Uzak kontrolden önce nominal 200 nm için bir genişletilmiş-domain ve bir fiziksel
PML-kalınlığı kontrolü ön kaydedilir; sınırsız tarama açılmaz. Legacy ve üretim
stack farkları manifestte yazılır; sonuç görüldükten sonra eşik değiştirilmez.

## K2s kilit sözleşmesi

V2 paketi scorer giriş noktası, bütün yerel kaynak/dependency içerik hash'leri,
config, fizik/optik kanıt, ortam, mask dizisi/seed'i, 20 slot, dört port sırası
(80 özellik), örnekleme, sıfır dijital tap, başlangıç ve train-içi ridge seçim
protokolü/final alpha içerir. Scorer doğrulanmış paketten kurulur; CLI kilitli
ayarları değiştiremez. V1 kilitleri gerçek kör değerlendirmeye kabul edilmez.
Suite kimliği blind manifest digest'idir; farklı aday kimliği yeniden açamaz.
Skordan önce atomik tüketim ve eşzamanlı süreç kilidi gerekir. Kurtarma yalnız
aynı paket/run ve doğrulanmış checkpoint ile olur. Testler baseline çağrısı,
transitif kaynak değişimi, farklı adayla tekrar, yarış ve hatalı kurtarmayı yakalar.

Canlı kod düzeltmesi: guard kalıcı tüketim yapmıyor; kayıt skor sonrasında
yazılıyor. Baseline çağrısı gerçek bug; atomik tüketim ayrıca eksik.

## K2a kaynaklı fizik girdileri — 0 FC

Sahip Claude. Tablo n2, beta_TPA, sigma_FCA, dn/dN, dn/dT, tau_FC, tau_th,
ısıl kapasite/direnç ve gerekli modal hacim/örtüşme dönüşümlerini kapsar.
Her satır: birim, birincil kaynak/denklem/sayfa, artefakt hash'i, dalga boyu,
sıcaklık, proses/geometri uyumu, nominal/aralık, dönüşüm ve kabul durumu.
Literatür cihaz ömrü bu cihazın ölçümü değildir; uyumsuzluk unresolved kalır.
Kaynak yoksa sentetik test mümkündür; fiziksel aday ve K5 araması açılamaz.

kappa_scatter proses kaybıdır: uygun proses ölçümü veya kaynaklı roughness
modeli ve belirsizliğinden gelir; düzgün kayıpsız FDTD bunu ölçmüş sayılmaz.
Güç zayıflaması alpha_power [1/m] için enerji kayıp hızı vg*alpha_power;
dB/uzunluk dönüşümü belgelenir. Roughness geri saçılması ile CW/CCW bağlaşımında
aynı etki çift sayılmaz. Absorpsiyon olmayan saçılma ısı girdisi değildir.
Kaynaksız sıfır saçılma yalnız ideal kontrol senaryosudur.

## B25 tarihsel bütçe kararı

Durum OPEN: yeni ücretli solve bloke; kayıt sahibi Claude, harcama kararı Hasan.
79.0726 FC tarihsel harcama silinmez; sınıflandırmayla aşım gizlenmez.
47 FC tahsis %25 kuralından muafiyet değildir. Claude task bazında doğrulama
harcaması dökümü ve istisna önerisini yazılı teslim eder. Hasan açık karar
vermeden eşik aşımı onaylanmış değildir. 60 FC taban, 25 FC tek-koşu,
20 FC final rezerv ve solve başına tahmin/onay korunur. Ücretsiz işler serbesttir.
