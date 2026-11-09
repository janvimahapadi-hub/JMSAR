# JMSAR · Sentinel-1 Land-Cover Study (2021)

A focused, local-first research interface for examining **January–December 2021** radar-based land-cover segmentation. JMSAR provides a separate visual and analytical workflow: class-distribution timelines, adjacent-month change indicators, radar/prediction overlay, and reproducible region exports.

**Provenance:** This is a credited derivative study and interface built on the [SARScope](https://github.com/keyurck7/SARScope) pipeline and pretrained model developed by Keyur Chaudhari. The original model, 52-region 2021 weak-label training dataset, and benchmark metrics are not independent training contributions of this repository. This repository does not include trained weights or credentials.

**First-run setup:** Run `SETUP_WINDOWS.cmd` (Python 3.12 and Git required), then `START_JMSAR.cmd`. The first script clones the original SARScope core into ignored `vendor/SARScope` and installs its viewer dependencies. Open **http://127.0.0.1:8899** after both local servers start. Browse the preserved Mannheim 2021 example without Earth Engine credentials.

For new coordinates in 2021, follow `docs/MODEL_SETUP.md` to install a *verified, authorized* copy of the SARScope checkpoint and authenticate Earth Engine locally. New inference is disabled if those assets are absent. All analysis uses the fixed **2021-01** start month, yielding twelve calendar months in 2021. No synthetic imagery or substitute model is used.

See `docs/METHODOLOGY.md` for metrics and limitations and `docs/REPORT_GUIDE.md` for the analysis write-up.
