# Sample Paper Brief (Step 1 output)

> Illustrative example with a fictional project. Shows the shape of the brief, not real results.

## Working title candidates

1. **DRAPE: Draping Garments with Latent Displacement Fields** (recommended — pronounceable, relevant to clothing, searchable)
2. Towards Fast Garment Fitting from a Single Scan
3. On the Equivalence of Pose and Cloth Latent Spaces

## Hypothesis

My hypothesis is that modeling garment displacement in a shared pose-aware latent space is more accurate than modeling pose and cloth separately. Test: compare against the separate-model baseline on the same data, ablating only the shared space.

## Goal → Problem → Solution

| | |
|---|---|
| Goal | Dress any 3D body in realistic clothing quickly |
| Problem 1 | Prior models treat pose and cloth separately, so wrinkles ignore pose |
| Solution 1 (nugget) | Pose and cloth are hard separately but easier jointly: one shared latent space |
| Problem 2 | Shared latent space collapses to the mean on loose garments |
| Solution 2 | Displacement fields on the body surface with a per-garment prior |

## Nugget

Field works on pose and cloth separately, each hard. Solving them in one latent space makes each easier.

## Elevator pitch (3 sentences)

Dressing 3D bodies is hard because wrinkles depend on pose. We model pose and cloth jointly in a single latent space. This yields more accurate garments than separate models on `<dataset>`.

## Teaser

Left: baseline output with pose-independent wrinkles. Right: proposed output, same body and garment.

## Prior work and limits

- Separate pose/cloth models → wrinkles ignore pose.
- Physics simulation → accurate but slow.

## Evaluation and demo

- Metric: vertex error vs. ground truth simulation. Baseline: simple linear blend model first.
- Ablation: shared vs. separate latent space (one change).
- Demo: animation video on held-out poses.

## Risks and data

- Risk: loose garments (skirts) may fail → report as limitation.
- Data: `[TODO: confirm licensed simulation dataset]`

## Open items

1. `[TODO]` dataset license
2. `[TODO]` baseline numbers

**Next action:** confirm the nugget sentence, then draft the abstract with the skeleton.
