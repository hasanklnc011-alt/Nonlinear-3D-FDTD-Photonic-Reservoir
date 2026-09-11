# 2026-09-10 — [BM-001] Claude — Kanonik benchmark için deterministik yerel preflight

## Sahiplik

- Görev: onaylanan güvenli yerel iş — kanonik `benchmarks/narma10_np` paketi için
  deterministik, salt-okunur bir `preflight` komutu.
- Uygulayıcı: Claude Sonnet 5 (bu oturum), `high` çaba.
- Sınır (uygulandı): aday kilidi oluşturulmadı/ratifiye edilmedi, manifestolar
  değiştirilmedi, blind evaluation çalıştırılmadı, bilimsel sabitler /
  sözleşmeler / `BACKLOG.md` değiştirilmedi, Tidy3D/cloud çağrısı yok, paket
  kurulmadı, commit/push yapılmadı, alt-ajan başlatılmadı.
- Sözleşme dosyaları (`AGENTS.md`, `CLAUDE.md`, `const.md`, `BACKLOG.md`,
  `BACKLOGLOG.md`, `docs/PROJECT-CHARTER.md`) **değiştirilmedi**.

## Neden

`docs/decisions/2026-09-10-benchmark-canonicalization.md` ve `BACKLOG.md` [BM-001]
"manifestolar doğrulanmış fakat ratifiye edilmemiş; candidate lock olmadan blind
evaluation yasaktır" durumunda. Astra'nın ratifikasyon kararından önce tekrar
tekrar elle kontrol etmesi gereken şeyleri tek deterministik komutta toplar ve
**doğrular** (yalnız yazdırmaz).

## Teslim edilenler

### `benchmarks/narma10_np/preflight.py` (yeni)

`run_preflight(*, strict_blind=True, lock_dir=None, ledger_path=None) -> PreflightReport`.
Dosya sistemi bakımından saf (hiçbir şey yazmaz). 8 kontrol, sabit sırada:

| # | check | ne doğrular | durum kuralı |
| --- | --- | --- | --- |
| 1 | `environment.provenance` | Python impl/sürüm + NumPy sürümü | her zaman INFO (kanıt manifest kontrollerinde) |
| 2 | `manifest.dev` | dosya var; `verify_manifest` OK; stored `spec`/entry hash'leri `config.py` ile bit-bit eşleşiyor (drift yakalama); committed vs recomputed `manifest_digest`; entry sayısı = `N_DEV_SEEDS` | PASS/FAIL |
| 3 | `manifest.blind` | aynısı, `N_BLIND_SEEDS` | PASS/FAIL |
| 4 | `manifest.digests_distinct` | dev ve blind `manifest_digest` farklı | PASS/FAIL |
| 5 | `seeds.dev` | `config` count == `N_DEV_SEEDS`; tüm trial'lar üretiliyor; her `u`/`y` sonlu; `max|y| < 1e3` (dataset testlerinin kullandığı sınır) | PASS/FAIL |
| 6 | `seeds.blind` | aynısı, `N_BLIND_SEEDS` | PASS/FAIL |
| 7 | `candidate_lock` | `manifests/narma10/candidates/*.lock.json` taranır; her biri için id / `locked` / kod artefaktı var mı / `blind_manifest_digest` | yok → INFO "absent"; var → INFO + liste |
| 8 | `blind_evaluation.blocked` | her lock için `guard_blind_evaluation` çağrılır (salt-okunur); ticket dönerse blind eval AÇIK demektir | lock yok veya hepsi bloklu → PASS; en az biri açık → FAIL (`strict_blind=True`) ya da INFO (`--allow-blind-unblocked`) |

Rapor JSON'a (`to_dict`) ve metne (`format_text`) serialize olur; timestamp
içermez, iki koşuda birebir aynıdır (`test_report_is_deterministic`).

`--allow-blind-unblocked`: Astra bilinçli, denetimli bir blind koşusu için kilit
açtığında preflight'ı yeşil tutar (varsayılan: açık blind eval = FAIL).

### `benchmarks/narma10_np/cli.py` (düzenlendi)

`preflight` alt-komutu eklendi: `--json`, `--allow-blind-unblocked`.
Çıkış kodu: hiç FAIL yoksa 0, aksi halde 1.

### `benchmarks/narma10_np/README.md` (düzenlendi)

`preflight` satırı + modül tablosu + test sayısı 66 → 82.

### `tests/narma10_np/test_preflight.py` (yeni, 16 test)

- Repoda olduğu haliyle preflight **yeşil**; 8 kontrol doğru sırada; provenance
  INFO ve NumPy sürümünü içeriyor; manifest digest'leri committed ile eşleşiyor;
  seed blokları 5/10 sonlu; candidate lock "absent"; blind eval PASS (bloklu).
- `to_dict` şekli; determinizm (iki koşu aynı).
- Sentetik lock fixture'ı (tmp dizinde, gerçek committed manifestolara karşı
  `create_lock` — `test_candidate_lock.py` ile aynı desen; repoya lock yazılmaz):
  kilitli+açık lock varsayılanda FAIL, `strict_blind=False` ile INFO+ok;
  draft lock blind'i bloklu tutuyor; bozuk JSON lock blind'i bloklu tutuyor.
- CLI: `preflight` ve `preflight --json` çıkış 0; parser `cmd_preflight`e bağlı.

## Doğrulama — tam komutlar ve çıktılar

Ortam: Windows 11, CPython 3.14.7, NumPy 2.4.6. Ağ/cloud yok. Bu iş bir git
worktree'sinde yapıldı; kanonik paket ana çalışma kopyasında hâlâ commit'siz
olduğu için worktree'ye kopyalandı, sonra yeni/değişen dosyalar ana kopyaya geri
yazıldı (aşağıya bakın).

```
$ python -m unittest discover -s tests -t .
..................................................................................
Ran 82 tests in 16.000s
OK
```

```
$ python tests/narma10_np/run_tests.py
Ran 82 tests in 16.6s
OK
```

```
$ python -m benchmarks.narma10_np preflight ; echo exit=$?
[INFO] environment.provenance: CPython 3.14.7 / NumPy 2.4.6
[PASS] manifest.dev: verified; digest 1b865944b5f99eeb...
       committed_digest = 1b865944b5f99eeb8f408121760fe0f5f178b7eb58aae24e47401c7bdd13d482
       recomputed_digest = 1b865944b5f99eeb8f408121760fe0f5f178b7eb58aae24e47401c7bdd13d482
       entries = 5 (expected 5)
[PASS] manifest.blind: verified; digest 6cc96caac8f62442...
       committed_digest = 6cc96caac8f6244207e4f0d2c82cea2c5ad6138c25ebc5a9e8ebddd3d78eb4ea
       recomputed_digest = 6cc96caac8f6244207e4f0d2c82cea2c5ad6138c25ebc5a9e8ebddd3d78eb4ea
       entries = 10 (expected 10)
[PASS] manifest.digests_distinct: dev and blind digests differ
[PASS] seeds.dev: 5 finite trials, max|y| = 0.9704
[PASS] seeds.blind: 10 finite trials, max|y| = 1.045
[INFO] candidate_lock: absent - no candidate lock present
       scanned = manifests\narma10\candidates ; count = 0
[PASS] blind_evaluation.blocked: blocked - no candidate lock, blind evaluation is unreachable

PREFLIGHT OK (8 checks)
exit=0
```

```
$ python -m benchmarks.narma10_np preflight --json   # deterministik: iki koşu identik (diff boş)
{ "ok": true, "n_checks": 8, "n_failed": 0, "checks": [ ... ] }
```

Negatif yol (tmp dizinde sentetik kilitli lock, repoya hiçbir şey yazılmadan):

```
[INFO] candidate_lock: 1 candidate lock file(s) present
[FAIL] blind_evaluation.blocked: blind evaluation is NOT blocked for: ...\C999.lock.json
       ...C999.lock.json: NOT BLOCKED - guard admitted candidate 'C999'
PREFLIGHT FAILED (1 check(s): blind_evaluation.blocked)   # exit=1
```

## Şu anki preflight verdiği tablo (repo olduğu gibi)

- Provenance: CPython 3.14.7 / NumPy 2.4.6.
- `manifests/narma10/dev_seeds.sha256.json` digest
  `1b865944b5f99eeb8f408121760fe0f5f178b7eb58aae24e47401c7bdd13d482`, 5 entry,
  `verify_manifest` OK, `config.py` ile drift yok.
- `manifests/narma10/blind_seeds.sha256.json` digest
  `6cc96caac8f6244207e4f0d2c82cea2c5ad6138c25ebc5a9e8ebddd3d78eb4ea`, 10 entry,
  `verify_manifest` OK, drift yok.
- Dev seed bloğu: 5 sonlu trial, `max|y| ≈ 0.970`.
- Blind seed bloğu: 10 sonlu trial, `max|y| ≈ 1.045`.
- Aday kilidi: **yok** (`manifests/narma10/candidates/` boş).
- Blind evaluation: **bloklu** (admit edilecek lock yok) — beklenen güvenli durum.

## Değişen / eklenen dosyalar (ana çalışma kopyasında, commit'siz)

- `benchmarks/narma10_np/preflight.py` — yeni
- `benchmarks/narma10_np/cli.py` — `preflight` alt-komutu
- `benchmarks/narma10_np/README.md` — preflight satırları, test sayısı
- `tests/narma10_np/test_preflight.py` — yeni, 16 test
- `docs/coordination/2026-09-10-claude-preflight.md` — bu dosya

## Açık riskler

- **Determinizm CPython + NumPy sürümüne bağlı.** Preflight sürümleri yalnız
  raporlar; asıl garanti "bu yorumlayıcı committed digest'i yeniden üretiyor mu"
  kontrolüdür. Farklı bir ortamda digest kırılırsa `manifest.dev`/`manifest.blind`
  FAIL verir — bu doğru davranış, ama çapraz-dil/çapraz-sürüm referans üretimi
  gerekiyorsa ayrı karar kaydı gerekir (mevcut ADR'nin açık kapısı).
- **`--allow-blind-unblocked` bir kaçış kapısı.** Yalnız Astra'nın bilinçli,
  denetimli blind koşusu için. Varsayılan davranış (açık blind eval = FAIL)
  değiştirilmemeli.
- **Sentetik lock testi gerçek committed manifestolara karşı `create_lock`
  çağırıyor** (yalnız tmp dizine yazar, `test_candidate_lock.py` ile aynı desen).
  Repoda hiçbir lock/ledger oluşturulmaz; yine de bu testler manifestoları
  okur — manifestolar değişirse bu testler de yeniden koşmalı.
- **`preflight.py` `manifest._spec_payload`'ı dolaylı olarak `build_manifest`
  üzerinden kullanır** (özel API değil, `build_manifest` public). Manifest şeması
  değişirse drift karşılaştırması da güncellenmeli.
- Preflight ~15 s sürüyor (25 trial × 5200 adımlık Python döngüsü × birkaç kez).
  Kabul edilebilir; hızlandırma gerekirse `narma10_target` vektörleştirilebilir
  (ayrı iş).

## Sıradaki tek adım

Astra: `python -m benchmarks.narma10_np preflight` çıktısını ve `python -m
unittest discover -s tests -t .` sonucunu kaydet; preflight'ı BM-001
ratifikasyon kontrol listesine ekleyip ekleyemeyeceğine karar ver. Kod ve
davranış değişikliği önerisi bu dosyada; `BACKLOG.md` / `const.md` bu oturumda
değiştirilmedi.
