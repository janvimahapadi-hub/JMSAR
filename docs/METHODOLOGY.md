# Scientific methodology and contribution ledger

**Scope:** January–December 2021 only. JMSAR supports georeferenced monthly land-cover predictions, visual interpretation, class-share trends and exploratory stability auditing for the fixed 12-month historical period.

## Original model and data (credited external work)

The underlying SARScope study by Keyur Chaudhari trained a ResNet34 encoder/U-Net segmentation model on 2021 Sentinel-1 VV/VH imagery and Dynamic World-derived weak labels. It used 52 geographic regions and 1,300 scene chips (925 training, 200 validation, 175 test), a group-wise regional split, 8 radar/context channels and 9 land-cover classes. The selected FP32 seed-42 model achieved **74.17% overall accuracy and 42.39% mIoU** on held-out weak-label test data; these are **not independent ground-truth accuracy estimates** and are not JMSAR training results. Benchmark and checkpoint provenance are recorded in the linked SARScope source.

JMSAR imports the verified model pipeline on the local machine, and never claims new training. It does not edit the model's predictions, class map or frozen weights.

## JMSAR analysis layer

For each month, the UI reads the classified area share of each class from SARScope's saved CSV/API.

- **Annual average class share:** arithmetic mean of that class's 12 predicted percentages, not its independently observed physical area.
- **Monthly class-mix shift (percentage points):** 0.5 × sum across nine classes of |share[class,month] − share[class,previous month]|. This is total variation of aggregated share distributions. It is **not** the percentage of pixels that physically changed class; opposing location-level changes can cancel.
- **Diversity:** normalized Shannon entropy of each month's *class share distribution*: −sum p(class)log p(class)/log(9). This is different from model softmax entropy, and neither is an empirical error probability.
- **Dominant class:** the class with the greatest year-average predicted share.
- **Radar opacity comparison:** transparency is a display setting only; it has no effect on prediction.

## Study protocol for a genuine individual contribution

Choose and justify one or more 2021 sites; use exactly the same 2021 period in all comparisons. Run the original verified checkpoint, record scene support, identify and discuss two or more predictions that require scrutiny, compare against an independent reference where permitted, and document changed interpretation or new analytical code with evidence. Do not select a site only because it looks correct. Note class imbalance, temporal coupling, landscape differences, coverage and weak-label uncertainty.

## Risks and limitations

Weak-label benchmarks are not verified local truth. High built-up concentration in Mannheim does not establish parcel-scale accuracy. SAR is responsive to surface moisture, geometry, vegetation and orbit. A smooth map or class confidence display cannot certify correctness. A monthly share shift is not a change-detection accuracy metric. Restrict conclusions to the tested local cases and available external evidence.

## Academic provenance

- Segmentation model, trained weights, original dataset acquisition, validation/test numbers and underlying engine: **Keyur Chaudhari, SARScope**.
- JMSAR 2021-only interface, class-mix calculations, workflow design and documentation: this derivative project; document the actual contributions of its participants.
- Independent 2021 study region selection, new comparisons, written interpretation and narration: must be completed and attributed by the student actually performing them.

Review course policy before submitting a derivative. If independent training is mandatory, this reused model alone does not fulfill that requirement.
