# Changelog

## 2026-09-13

- Çalışma sözleşmesi tek operatöre geçirildi: ChatGPT/Astra orkestra şefliği
  `AGENTS.md`, `CLAUDE.md` ve `const.md` içinden kalıcı olarak kaldırıldı
  (bkz. `docs/decisions/2026-09-13-single-operator-contract.md`). Tamamlanmış
  Tidy3D task sonuçlarını indirme yasağı kalktı; ücretli solve için Hasan
  onayı şartı korundu.
- `Q_loaded ~ 27.000` (FWHM `~0.056 nm`) ring-down fit'inden çıkarıldı; Tidy3D
  `shutoff` tanımı (E-field intensity oranı) doğrulanarak 2x belirsizlik kapandı.
- `linear_build._monitors` artık monitör başına `sampling` bloğunu kullanıyor;
  monitör frekans tarağı kaynak darbesinden ayrıştırıldı (8 yeni test, 187/187 OK).
- **Bulundu: bus facet'leri Fabry-Pérot kavitesi kuruyor** (`0 FC`, zaten ödenmiş
  `mesh-rung-2` verisinden). Tam bantta baseline `0.51-0.90` arası salınıyor
  (`%40` tepe-tepe), periyot `17.96 nm`; facet turu (`2L=32 um`, `n_g~4.2`)
  `17.66 nm` öngörüyor, halka FSR'si `18.93 nm` — ve iki tarak bant boyunca
  birbirinden yürüyor (`+3.74 -> -1.07 nm`). Bugüne kadarki tüm mutlak genlik
  ölçümleri bu dalgalanmanın üstünde alınmış. Çizgi genişliği etkilenmiyor.
  (`docs/decisions/2026-09-13-facet-fabry-perot.md`)
- Düzeltme: geometri schema `/2` ve `bus_overhang_um`. Bus port düzlemlerinden
  taşacak kadar uzun çiziliyor, uç yüzler PML içinde sonlanıyor. `domain_size_um`
  kasten `bus_length_um`'e bağlı kaldı, yani domain ve maliyet büyümüyor; port
  düzlemleri `±8`'de sabit. `bus_overhang_um = 0` iken alan serileştirmeden
  çıkarılıp şema `/1` beyan ediliyor, böylece kilitli merdivenin geometry hash'i
  `6844d49c...` birebir korunuyor. `tests/fdtd/test_bus_overhang.py` (19 test,
  kilitli hash literal pinlendi). Depo `286/286 OK`.
- **`freq-rung-3` tamamlandı — 4 ölçütten 3'ü geçti**, gerçek `18.1080 FC`
  (tahmin 22.8463; beklentim `~16.6` idi, `%9` yanıldım). Bakiye `115.7358`.
  GEÇTİ: rezonans kayması `-0.08 nm` = FSR'nin `%0.42`'si; `Q_e` `-1.28%`;
  enerji dengesi `2.4e-04`. GEÇMEDİ: `Q_L` `-6.56%` (eşik `%5`).
  Teşhis: rezonans **konumu** yakınsadı, yakınsamayan şey **kayıp kanalları** —
  `T_add` `+53.8%`, `T_through` `+43.4%`. `subpixel` averaging zaten açık;
  kalan açıklama eğri halka sınırının ayrıklaştırılması.
  **DÜZELTME:** `freq-rung-2` değerlendirmesinde `T_add = 0.097`'yi "geri
  saçılmanın doğrudan ölçümü, gerçek cihaz özelliği" diye sunmuştum — fazla
  iddiaydı; yakınsamamış, fiziksel/sayısal ayrımı yapılmamış.
  **`16 step/λ` ÖNERİLMİYOR** (`~42 FC` = kalanın `%36`'sı): V4 kaçış valfi
  uygulandı. Kabul: `lambda_0 = 1.54090 ± 0.00008 um`, `Q_e = 12 180 ± %1.3`,
  `Q_L = 9 500 ± %7` (belirsizlikle), `Q_i` ve `T_add` **rapor edilmiyor** —
  `Q_i` ücretsiz bend mode solver yoluna bırakıldı. Lineer kapı koşullu kapandı;
  `12 step/λ` üretim mesh'i. (`docs/decisions/2026-09-13-freq-rung-3-evaluation.md`)
- **V1–V5 doğrulama merdiveni sözleşmeye yazıldı** (`AGENTS.md` §Kanıt kuralları,
  `const.md` §Süreç sözleşmesi). ADR FDTD'yi yetkili ilan etmişti ama "bir FDTD
  değeri ne zaman kabul edilmiş sayılır" tanımlı değildi — o boşluk kapandı.
  Fail-closed: değer, geçtiği basamaklar yazılmadan TCMT'ye giremez. V1 korunum,
  V2 kontrol grubu, V3 çapraz yol, V4 yakınsama, V5 dış çapa. Dördü `0 FC`;
  V4 **çalışma düzeyinde** tanımlandı (geometri ailesi başına bir merdiven +
  tarama uçlarında iki nokta kontrolü), naif nokta-başına uygulama yasaklandı.
  Kaçış valfi: yakınsatılamayan büyüklük reddedilmez, belirsizlikle raporlanır.
- **Bütçe ve bakiye kuralları eklendi.** Bakiye ilk kez okundu: `133.8438 FC`
  (son kullanma 2027-04-29); başlangıç bütçesi `~195 FC`, `%31` kullanılmış.
  Her ücretli solve öncesi bakiye kontrolü zorunlu; tek koşu `25 FC` üstü ayrı
  karar; WP6 için `20 FC` rezerve. Kural, `freq-rung-3`'e `23 FC` tavanı
  önerilirken bakiyenin hiç kontrol edilmemiş olması üzerine yazıldı.
- `reports/OPTICAL-PARAMETER-STATUS.md` eklendi: her optik parametrenin V1–V5
  durumu. Dürüst özet — **şu anda hiçbir parametre merdivenin tamamını geçmiş
  değil**; `Q_e` ve `Q_i` çapraz yolu yok, `n_eff` hiç yakınsatılmadı.
- **ADR: TCMT birincil çözücü, FDTD optik parametrelerin yetkili kaynağı.**
  Hasan'ın açık onayıyla `const.md` §Bilimsel sözleşme değiştirildi: "uçtan uca
  3D FDTD zorunlu" ve "TCMT yardımcı kanıt" hükümleri kaldırıldı. Gerekçe: CFL
  duvarı ve FCD/FCA'nın Tidy3D'de native olmaması o hükmü ulaşılamaz kılıyordu.
  Yeni sözleşme rolleri takas etmiyor — FDTD, TCMT'nin girdilerini kilitleyen
  merci oluyor: `Q_i`, `Q_e`, coupling, `n_eff`, mode overlap yalnız full-wave'den
  gelebilir, fit edilemez. İddia kapsamı "FDTD-kalibre edilmiş TCMT reservoir"
  olarak daraltıldı. Benchmark, kör-seed protokolü ve `NMSE < 0.05` değişmedi.
  `AGENTS.md` §Amaç/§Aşamalar/§Kanıt kuralları birlikte güncellendi; plan
  incelemesinin R6'sı (enerji dengesi kapısı, `1e-3`) doğrudan kanıt kuralına
  yazıldı. Plan incelemesindeki bloke edici R4 böylece çözüldü, WP1 açılabilir.
  (`docs/decisions/2026-09-13-adr-tcmt-primary-fdtd-calibrator.md`)
- DENETİM DÜZELTMELERİ: (a) FlexCredit rakamı yanlış raporlanmıştı — gerçek
  harcama cloud'dan doğrulandı, `60.9646 FC` (iddia edilen `~44.4` değil) ve
  `freq-rung-3` ile toplam `~78 FC` olacak (`~61` değil). Tek doğru kaynak artık
  `reports/FLEXCREDIT-LEDGER.md`; iki karar kaydına düzeltme notu eklendi.
  (b) `test_every_locked_plan_still_records_that_digest` aşırı genişti: diskteki
  TÜM planların `/1` hash'ini taşımasını iddia ediyordu, oysa `freq-rung-2/3`
  kasten schema `/2`. Test planın kendi beyan ettiği şemaya göre kapsamlandırıldı
  ve `/2` planları için ayrı değişmezler eklendi. Depo `207/207` + `82/82` OK.
- Astra'nın TCMT/FDTD araştırma planı incelendi (`0 FC`): **REVİZYONLA KABUL**,
  altı revizyon (biri bloke edici: `const.md` çelişkisi Hasan'ın kararını
  bekliyor). (`docs/coordination/2026-09-13-claude-review-of-tcmt-fdtd-plan.md`)
- `freq-rung-3` planı hazır (14 step/λ mesh yakınsaması): `freq-rung-2` ile tek
  farkı grid; geometri, dört port, tarak ve `run_time` aynı, böylece `lambda_0`,
  `Q_L`, `Q_e` doğrudan karşılaştırılabiliyor. Hücre `1.51x`, zaman adımı `1.17x`.
  `estimate_cost = 22.8463 FC`, beklenen gerçek `~16.6`. **Hasan `15 -> 23 FC`
  tavan artışını açıkça onayladı ve koşu BAŞLATILDI**
  (task `fdve-1f8f0d66-3509-4ce5-8239-359c5e6f6d08`, submit öncesi tahmin
  yeniden doğrulandı). Kabul ölçütleri koşudan önce yazıldı.
  (`docs/decisions/2026-09-13-freq-rung-3-plan.md`)
- **`freq-rung-2` tamamlandı — üç kabul ölçütü de GEÇTİ**, gerçek `10.7316 FC`
  (tahmin 14.7500). (1) FP fringe `%39 -> %0.1`, facet teşhisi doğrulandı.
  (2) Rezonans dışı dört-port toplamı `1.0000` (önceki `0.77-0.88`).
  (3) TCMT tutarlılık hatası `0.22563 -> 0.00511`, 44 kat.
  `Q_loaded` `9 736 -> 9 797` (`%0.6`) — önceden yazılmış kontrol sinyali tuttu.
  **İlk geçerli optik parametreler**: `Q_e(toplam) = 12 260`, `Q_c = 24 519`,
  belirgin OVER-coupled (`x = 0.799`). `Q_i` aralık olarak: `4.9e4 - 7.1e4`,
  çünkü girişin `%9.7`'si add portundan çıkıyor (halkada geri saçılma) ve
  simetrik TCMT'de o kanal yok. Geri saçılma, freq-rung-1'deki `46 pm` mod
  yarılmasını da açıklıyor.
  (`docs/decisions/2026-09-13-freq-rung-2-evaluation.md`)
- `freq-rung-2` Hasan'ın açık onayıyla BAŞLATILDI: facet'siz bus + dört port,
  task `fdve-0ecc2c8f-e120-4b3c-8793-c9c0dcbda224`, tahmin `14.7500 FC`, tavan
  `15`, submit öncesi tahmin yeniden doğrulandı. Beklenen gerçek `~11.6`.
  (`docs/decisions/2026-09-13-freq-rung-2-plan.md`)
- Buried-oxide sızıntı hipotezi ÇÜRÜTÜLDÜ (yerel mode solver, `0 FC`):
  `1.0 um` BOX'ta sızıntı `0.02 dB/cm`, substrate gücü `%0.00`, `k_eff` gürültü
  tabanında. BOX `1.0 um` korunuyor. Kontrol grubu (substrate yok) `n_eff=2.40167`
  ile geçerli. Yan bulgu: modun yalnız `%60-63`'ü çekirdekte — `Q_e` için girdi.
  Rezonans dışı `%12-23` eksik güç açıklanmadı; kalan şüpheli kaynak/monitör
  düzlemlerinin kesilmiş uç yüzlerde olması.
  (`docs/decisions/2026-09-13-box-leakage-falsified.md`)
- Dört-port monitör doğrulandı (`0 FC`, kod değişikliği yok): `flux:bus_drop:in`
  token'ı gerçek drop portuna (`x=-8`) oturuyor; translate + build yerel geçti.
- `freq-rung-1` tamamlandı, gerçek `11.5346 FC` (tahmin 14.6803, tavan 15).
  Monitör düzeltmesi çalıştı: FWHM başına `79.8` nokta. Çizgi çözüldü —
  `Q_loaded ~ 9 650` (drop 9 736 / through 9 557, %2 içinde uyuşuyor),
  FWHM `~0.159 nm`, through extinction `13.56 dB`. Ring-down'dan çıkarılan
  `~27 500` tahmini çürütüldü (`2.8x` yüksekti).
  **`Q_i`/`Q_e` ayrımı GEÇERSİZ**: enerji dengesi kapanmıyor (rezonans dışı
  `%12-23`, rezonansta `%69` ölçülmeyen). Nedenler: drop monitörü ADD portunda
  (gerçek drop portu `x=-8`), geri-yansıma portu izlenmiyor, ve `1.0 um` buried
  oxide altındaki Si substrate'e sızıntı şüphesi. Sıradaki adım ücretsiz:
  mode solver ile BOX kalınlığı taraması + dört-port monitör.
  (`docs/decisions/2026-09-13-freq-rung-1-evaluation.md`)
- `freq-rung-1` Hasan'ın açık onayıyla BAŞLATILDI: task
  `fdve-719dd4d0-fed8-4d10-9be8-6c0aab8b047a`, tahmin `14.6803 FC`, yazılı tavan
  `15 FC`, submit öncesi tahmin yeniden doğrulandı. `1501` nokta / `2 pm` adım
  dar-bant tarak; amaç `Q_i`/`Q_e` ayrımı.
- `mesh-rung-2` indirildi ve değerlendirildi (task `fdve-b2b294bc...`, gerçek
  `11.4329 FC`): zaman yakınsaması GEÇTİ (`9.99e-06 < 1e-5`), mesh yakınsaması
  GEÇMEDİ (10->12 step/λ rezonansları `+1.5..+1.9 nm` kaydırıyor, FSR'nin ~%8'i).
  Flux monitörlerinin `0.5 nm` frekans adımı rezonansları çözmüyor; `Q_i`/`Q_e`
  ve coupling hiçbir mevcut koşudan çıkarılamıyor
  (`docs/decisions/2026-09-13-mesh-rung-2-evaluation.md`).
- Geometriyle sınırlandırılmış, belirsizliklere dayanıklı MRR reservoir için
  TCMT/FDTD araştırma planı Claude incelemesine açık taslak olarak eklendi.
- Taslak mevcut `const.md`, çalışma sözleşmesi ve kilitli NARMA-10 benchmarkını
  değiştirmiyor; olası sözleşme değişikliği ayrı karar kaydına bırakıldı.

## 2026-09-10

- Claude Sonnet 5 high yerel NARMA-10 benchmark iskeletini üretti.
- Astra doğrulaması iki eşzamanlı iskeleti tekilleştirdi: `benchmarks/narma10_np/`
  kanonik hattır.
- 66 kanonik test ve iki hash-kilitli manifest doğrulaması geçti.
- Tidy3D cloud solve, aday kilidi ve kör değerlendirme başlatılmadı.
- Benchmark preflight eklendi; 8/8 kontrol ve 82/82 test geçti. Klasik
  NARMA-10 manifest sözleşmesi ratifiye edildi ve FDTD-001 fizibilite aşaması açıldı.
- FDTD candidate-study provenance validator eklendi; 129/129 test geçti ve
  kanıtsız çalışma manifestoları fail-closed reddediliyor.
- Parametrik silicon-MRR study builder eklendi; toplam 164/164 test geçti.
- Yerel-only `tidy3d.Simulation` kurucu katmanı eklendi: doğrulanmış lineer planı
  somut Simulation nesnesine çeviriyor, kanonik JSON ve SHA-256 digest üretiyor;
  cloud/web çağrıları ve nonlinear içerik fail-closed engelleniyor.
- İlk fiziksel lineer Si-MRR convergence rung'u Tidy3D'ye gönderildi: tahmin
  0.6261476005924334 FlexCredit, task `fdve-7a16b155-f684-4bae-91ea-c1dd59877758`.
