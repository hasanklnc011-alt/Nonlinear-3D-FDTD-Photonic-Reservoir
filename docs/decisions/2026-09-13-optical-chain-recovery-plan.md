# MRR kurtarma planı: doğrulanmış geometri → optik model → TCMT

- Durum: KABUL EDİLDİ; Hasan bu planın uygulanmasını açıkça istedi.
- Tarih: 2026-09-13; rol kapsamı 2026-09-14 tarihinde netleştirildi. Dokümantasyon: Codex; kod uygulaması: Claude.
- Tek uygulama sahibi Claude; devir BACKLOG üzerinden, aynı dosyada eşzamanlı yazma yok.
- Hasan’ın son talimatı: Codex kod yazmaz; yalnız hedef, sözleşme, karar ve görev dokümanlarını tamamlar. K1–K5 aşağıdaki kabul kapılarıyla Claude için açık uygulama işleridir.

Güncel sıra, hedef dosyalar, K2s/K2a ve B25: [uygulama sözleşmesi](2026-09-14-recovery-implementation-contract.md).

## Hedef ve kapsam

450×220 nm silicon kesit, merkez yarıçapı 4.775 µm, simetrik iki bus,
150–250 nm gap. Global surrogate, kesit/yarıçap/topoloji optimizasyonu ertelendi.
Zincir: kesit eigenmode → açık bus–ring kompleks S → round-trip → CW/CCW TCMT.
Geometri parametreleri full-wave kanıtından; malzeme/carrier/termal girdileri
kaynaklandırılmış veriden gelir. Bilinmeyenler NMSE'ye uydurulmaz.
Kayıpsız model kontrol modelidir. Intrinsic kayıp = radyasyon + absorpsiyon +
proses saçılması; ısı kaynağı yalnız absorbe edilen güçtür.

## K0 — ortak karar ve kayıt, 0 FC

Charter/const/AGENTS/CLAUDE aynı sözleşmeyi taşıyacak. Eski kararlar silinmez,
güncel durum raporu ve bu ADR önceliklidir. Eski backlog tarihçeye aktarılır.
Q_i'nin kesin sayısal olduğu, Q_bend>3e7'nin doğrulandığı ve tüm yerel solver'ın
kullanılamadığı hükümleri kabul edilmiş fizik değildir. Önceki sabit-grid
+1e-12 µm öteleme tanısı 2.298684→2.364882 verdi; ikinci değer üretim girdisi değildir.
İki port aynı koşu/model tutarlılığıdır; bağımsız yöntem değildir. FSR doğrudan
n_eff doğrulamaz. İki mesh farkı güven aralığı değildir. V4 istisnası ancak
kaynaklı ve görev hassasiyetiyle sınanmış hata zarfı için kullanılabilir.
İlk commit: docs: adopt optical-chain recovery plan and gated milestones.
Normal push origin/main; force-push yok; uzak SHA doğrulanır.

## K1 — mode tanısı (K0 sonrası)

Yerel 0 FC, gerekli uzak kontrol toplam tavan 2 FC. Eski script/hash ve ortam
korunur; tanı Git'te tekrar üretilebilir olur. İzole, sürüm-kilitli ortamda
local subpixel zorunlu; sessiz fallback yasak. 16/20/26/32 step/λ Ex/Ey/Ez
örnekleri, aynı grid'de ±1e-12 µm öteleme testi. Üretimde koordinat yaması yok.
TE/çekirdek/alan örtüşmesi/parity seçici; geçerli mod yoksa hata, en yüksek iki
n_eff'e veya keyfî moda fallback yok. Tek kılavuz ve 150/200/250 nm çiftler;
büyük-gap tek-kılavuz limiti; genlik kappa ve güç K farklı isimler.
Geçiş: öteleme |Δn_eff|<1e-5; son iki mesh |Δn_eff|<1e-3;
n_g değişimi <%1; mod örtüşmesi >0.99.
Geçmezse aynı geometry/grid uzak subpixel karşılaştırması hazırlanır. O da
ayıramazsa coupler taraması durur; minimal reproducer/hata raporu teslim edilir.

## K2 — TCMT ve benchmark güvenliği (K0 sonrası), 0 FC

Durum: kompleks CW/CCW, carrier yoğunluğu, sıcaklık. s_out=C s_in+D a;
|a|² joule, |s|² watt; kappa enerji sönümü (1/s), Q=omega/kappa,
alan sönümü kappa/2. Kerr, TPA, FCA/FCD, termal ayrı anahtarlanır.
EM kabul öncesi exploratory; kaynaklandırılmamış katsayı fiziksel kabul alamaz.
20 sabit mask slotu × dört fiziksel çıkış gücü; slot sonu örnekleme;
semboller-arası dijital tap ve gizli carrier/thermal readout yok.
Kontroller: input-only, memoryless PD, linear+PD, carrier-off, thermal-off,
full; delayed-input 0/1/5/10/20 geçmiş örnek ayrıca raporlanır.
evaluate_states arayüzü korunur. blind-eval gerçekten kilitli scorer'ı çağırır,
baseline çağırmaz. Paket: tüm model/dependency kaynakları, config, optik kanıt,
ortam, mask/readout; her dosyanın içeriği tekrar doğrulanır.
Analitik lineer limit, serbest sönüm, sıfır giriş/kuplaj ve güç/enerji testleri;
zaman çözümü sıkılaşınca development NMSE değişimi <%1.

## K3 — açık coupler (K1 ve K2 fizik testleri sonrası), 10 FC

Önce gap=200 nm nominal; kabulden sonra 150/250 nm. Aynı stack/eğrilik,
kaynak ve monitor ayrı, ileri/geri kompleks modal genlik, kapalı akı yüzeyi.
Gerekli bağımsız girişler ölçülür; doğrulanmamış simetriyle sütun doldurulmaz.
Port de-embedding, sonlandırma/bölge boyu kontrolü; keyfî uyum çarpanı yok.
Enerji artığı <1e-3; son rafinmanda K <%5, anlamlı S fazı <2 derece;
uçlarda da doğrulama. Üç nokta geçerse 175/225 nm yerel tahmin; önce yalnız
175 nm bağımsız ölçüm, K tahmin hatası <%5. Sığmazsa ayrık geometri kullanılır.

## K4 — halka bağlantı doğrulaması (K3 sonrası), 15 FC

200 nm tam halka spektrumu ölçümden ÖNCE bileşenlerden tahmin edilir.
Ortak dört-port tarak, linewidth başına >=20 örnek, kompleks modal monitor,
az sayıda zaman probu, radyasyon akısı. Eski FluxData'dan faz türetilmez.
Geçiş: rezonans hatası <0.1 linewidth, linewidth <%5, port güç mutlak hata
<0.02, enerji artığı <1e-3. Ortak kutuplar ve ringdown ayrıca karşılaştırılır.
Eksik fizik/tanımlanamazlık belirsizlik etiketiyle kapatılamaz.

## K5 — görev araması ve nihai test

K2 sonrası exploratory; fiziksel aday seçimi için K4 zorunlu. 5 dev/10 blind,
200 washout + 3000 train + 2000 değerlendirme ve mevcut veri hash'leri korunur.
256 deterministik Sobol tasarımı ve kaynaklı sınırlar ilk skordan önce kilitlenir.
Arama: doğrulanmış gap, güç, detuning, sembol süresi. Bilinmeyen malzeme ömürleri
optimize edilmez; kaynaklı senaryodur. Kaynaksız eksen varsa arama başlamaz.
Ridge yalnız train iç ayrımıyla seçilir; mask/başlangıç/readout adaya kilitlenir.
Nominal dev medyan <0.04, >=4/5 seed <0.05. Önceden kilitli 64 belirsizlik
senaryosunun >=%90'ında beş-seed medyan <0.05. Dağılım bilinmiyorsa cihaz
başarı olasılığı değil senaryo kapsamıdır. Geçmezse final rezerv harcanmaz.
Geçerse 20 FC rezervle final EM kontrolü, tam aday kilidi, sonra yalnız bir
blind değerlendirme: medyan <0.05 VE >=8/10 seed <0.05.
Suite farklı aday ID ile yeniden açılamaz. Çalışmadan önce atomik tüketim;
çökme sonrası yalnız aynı kilitli çalışmanın checkpoint'ten kurtarılması.

## Bütçe ve yürütme

Yerel iş 0; uzak mode 2; coupler 10; bridge 15; final rezerv 20 = 47 FC.
Defterdeki 115.7358 bakiyeye göre 68.7358 FC tahsis dışı kalır; canlı bakiye
yeniden okunmadan bu değer güncel cloud bakiyesi diye sunulmaz.
Tahsisler estimate/solve onayı değildir. Her ücretli koşu için canlı bakiye,
taahhüt, estimate_cost ve Hasan'ın açık solve onayı gerekir. Tek koşu <=25 FC;
bakiye 60 FC altına inemez; kullanılmayan pay otomatik aktarılmaz.
Geçmiş 79.0726 FC'nin yaklaşık 195 FC toplam içindeki %40.6 payı, tüm bu
harcama doğrulama sayılırsa %25 eşiğini aşmıştır. Bu plan geçmişi onaylanmış
saymaz: yeni ücretli adım öncesi bu eşik için de açık karar kaydı gerekir.
K0 push → K2s güvenliği → K1 tanı → K2 çekirdek; bunlar ve B25 kapanmadan ücretli coupler solve yok.
Her teslimat küçük commit, test/preflight, kaynak/geometri/solver hash'leri,
parametre birim-köken-belirsizlik-kabul durumu, komut ve güncel backlog içerir.
HDF5, anahtarlar ve gptpro/ Git'e eklenmez. Başarı iddiası yalnız geçen kapıya aittir.
