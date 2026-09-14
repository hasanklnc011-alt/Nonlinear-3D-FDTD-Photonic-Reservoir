# Nonlinear 3D FDTD Photonic Reservoir

FDTD ile optik parametreleri doğrulanan, görev çözümünü CW/CCW TCMT ile yürüten photonic reservoir araştırması.

Durum: K0 kurtarma sözleşmesi yayımlandı; uygulama/fizik kapıları açık. Defterde tarihsel harcama 79.0726 FC ve kayıtlı bakiye 115.7358 FC; bu canlı bakiye sorgusu değildir.

## Hedef

NARMA-10 üzerinde, önceden kilitlenmiş 10 kör seed için medyan test NMSE `< 0.05`.

## Güncel belgeler

- [Kurtarma planı](docs/decisions/2026-09-13-optical-chain-recovery-plan.md)
- [Claude uygulama sözleşmesi](docs/decisions/2026-09-14-recovery-implementation-contract.md)
- [Açık görevler](BACKLOG.md)

Kod/test sahibi Claude. K2s kapanana kadar gerçek kör değerlendirme çalıştırılmaz.
Nihai medyan şartına ek olarak en az 8/10 seed başarısı gerekir.

- [`AGENTS.md`](AGENTS.md) — ortak ajan sözleşmesi
- [`CLAUDE.md`](CLAUDE.md) — Claude eşgüdüm talimatı
- [`docs/PROJECT-CHARTER.md`](docs/PROJECT-CHARTER.md) — kapsam ve başarı kapıları
- [`docs/coordination/`](docs/coordination/) — ajan görev kayıtları

## Yerel ve uzak konum

Yerel: `C:\Users\hasan\OneDrive\Desktop\Nonlinear-3D-FDTD-Photonic-Reservoir`  
GitHub: `https://github.com/hasanklnc011-alt/Nonlinear-3D-FDTD-Photonic-Reservoir`

## Plan 2 kapsamı (2026-09-14)

[Plan 2 Kerr ADR](docs/decisions/2026-09-14-plan2-kerr-reservoir.md) ayrı araştırma hattını tanımlar.
Eski silikon geometri kısıtları bu hatta uygulanmaz; eski sonuçlar korunur.
Plan 2: Si3N4/SiO2 ve AlGaAsOI adayları, 1550 nm, tek/iki halka,
10 mW ortalama / 100 mW tepe araştırma tavanı, 20 slot × 2 port = 40 özellik.
Kaynaklı keşif EM öncesi yapılabilir; fiziksel kabul/kör kilit için P6 kanıtı gerekir.
Ortak benchmark ve kör suite kopyalanmaz; hatlar arasında yalnız tek nihai kör aday.
Plan 2 için ek 47 FC tahsis edilmedi; bütçe, 20 FC rezerv ve B25 ortaktır.
Kod/test Claude; P0 teknik kabulü ve P1–P6 tamamlanmış değildir.
