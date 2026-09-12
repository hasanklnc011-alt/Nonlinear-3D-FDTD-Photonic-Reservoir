# 2026-09-13 — Tek operatör sözleşmesi: Astra/ChatGPT rolü kalıcı olarak kaldırıldı

- Karar sahibi: Hasan (açık talimat)
- Uygulayan: Claude Opus 5
- Durum: KABUL EDİLDİ — yürürlükte

## Karar

`AGENTS.md` ve `CLAUDE.md` içindeki "Astra → Claude görev dağılımı" bölümü ve
2026-09-11 tarihli "Geçici mod: Astra devre dışı" bölümü **kalıcı olarak**
kaldırıldı. Yerine tek operatörlü "Rol dağılımı" bölümü kondu. `const.md`
içindeki "Ajanlar: ChatGPT ve Claude" satırı tek ajana güncellendi.

## Gerekçe

Projenin özgün kurgusu rolleri ayırıyordu: karar/mimari ChatGPT (Astra),
kod/test Claude. Hasan'ın ChatGPT kredisi 2026-09-11'de bitti ve o tarihte
rol ayrımı *geçici* olarak askıya alındı. Krediler geri gelmediği ve iş bu
kurguyla fiilen tek ajanla yürüdüğü için, askıya alma durumunu belirsiz süreyle
taşımak yerine sözleşme gerçeğe uyarlandı.

## Ne değişti

- Orkestra şefliği/onay zinciri olarak Astra kaldırıldı; mimari ve benchmark
  protokolü kararları artık Claude'un yetkisinde.
- Tidy3D cloud'dan **tamamlanmış task sonuçlarını indirme** yasağı kaldırıldı.
  Bu yasak rol ayrımından doğuyordu ve indirme ek FlexCredit harcamıyor.

## Ne değişmedi — bilerek korunan sınırlar

- **Ücretli solve başlatmak yalnız Hasan'ın açık onayıyla.** Tek operatöre
  geçiş bu onayı kaldırmaz; her submit öncesi `estimate_cost` üst sınırı yazılı
  raporlanır.
- `const.md` sabitleri ve kilitli NARMA-10 kör-değerlendirme protokolü;
  bunları etkileyen her adım ayrı karar kaydı + Hasan onayı ister.
- Kanıt yükü: ikinci denetleyen ajan kalmadığı için karar kaydı ve test kanıtı
  **tek** denetim mekanizmasıdır. Tek operatör, kanıtın gevşetilmesi anlamına
  gelmez.

## Kapsam dışı

`docs/coordination/` ve `docs/decisions/` altındaki eski kayıtlar, `BACKLOGLOG.md`
ve `reports/` içindeki Astra atıfları **değiştirilmedi** — bunlar tarihsel kayıt,
yürürlükteki sözleşme değil.

2026-09-13 tarihli `docs/coordination/2026-09-13-astra-tcmt-fdtd-research-plan-review.md`
taslağı bu kararla reddedilmiş veya kabul edilmiş sayılmaz; teknik içeriği
bağımsız olarak incelenmeye devam eder.
