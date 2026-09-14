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
