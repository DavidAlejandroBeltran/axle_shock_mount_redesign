A parametric engineering study to redesign a folded weld-on rear axle
shock bracket for 3.25" axle housings (F-150 / Tacoma class light trucks).

## Problem:
Standard aftermarket folded brackets fail in three ways under off-road
dynamic loading:
1. Bending fatigue and weld cracking at the axle saddle radius
2. Oval slotting and wall tearing around the shock bolt hole
3. Debris entrapment causing localized corrosion along weld seams

## Goal:
Prove a >30% stress reduction and infinite fatigue life (>10^6 cycles)
via parametric design changes: progressive bend radii, bolt-hole doubler
rings, DFM drain notches, and optimized gusset geometry.

## Roadmap:
- [x] **Phase 1** — Python load engine & material database
- [ ] **Phase 2** — Baseline CAD model & FEA failure mapping
- [ ] **Phase 3** — Parametric redesign & DFM
- [ ] **Phase 4** — Comparative FEA validation & portfolio PDF

## Running the Tool:

```bash
pip install customtkinter pandas
python shock_mount_engine.py
