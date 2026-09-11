# ADR — FDTD provenance kapısı

- Tarih: 2026-09-10
- Karar sahibi: Astra/Codex
- Durum: Kabul edildi

`fdtd.provenance` şeması, her aday çalışması için malzeme/nonlinear kaynakları,
geometri hash'i, mesh/time/PML yakınsama merdiveni, task kimlikleri ve FlexCredit
kaydını zorunlu ve fail-closed yapar. Boş veya kanıtsız manifest ücretli solve
öncesi kabul edilmeyecektir.

Kanıt: 129/129 depo testi geçti. Bu karar fiziksel parametre, aday ailesi veya
cloud submission seçmez.
