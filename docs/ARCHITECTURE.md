# Architecture

```text
market quote sheet
   ↓
eSSVI arbitrage-free surface
   ↓
Dupire local-vol extraction
   ↓
Heston-SLV calibration
   ↓
frozen 3D price / delta / vega surfaces
   ↓
Heston-SLV control-world hedge runs
   ↓
Rough-SLV realized-world hedge runs
   ↓
pathwise hedge P&L arrays
   ↓
ES / hedge-transfer diagnostics
   ↓
XVA exposure / WWR / CVA-style summaries
   ↓
public evidence tables and figures

