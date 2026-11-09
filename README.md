<div align="center">

# JMSAR
### Satellite intelligence. Reproducible by design.

**2021 Sentinel-1 Radar · Land-Cover Segmentation · Geospatial Analytics**

[Overview](#overview) · [Architecture](#architecture) · [Installation](#deployment-and-reproducibility) · [Model setup](#phase-2-enable-verified-inference) · [Verification](#verification-and-quality-gates) · [Operations](#operations-and-troubleshooting)

</div>

---

> **Project status:** Local-first research system. The browser workspace, 2021-only analysis API, saved-case exploration and automated offline checks are implemented. New-location inference requires an authorized, separately supplied model checkpoint, its normalization metadata and Google Earth Engine access. This is **not** an independently hosted production inference service.

## Overview

**JMSAR** is an interactive research workspace for examining satellite-radar-based land-cover predictions across the twelve months of **January–December 2021**. It unifies geospatial visualization, temporal class-distribution analysis and traceable result artifacts in a single local workflow.

Rather than displaying a segmentation image without context, JMSAR exposes the underlying radar view, class composition, time series, distribution shifts and limitations to make each prediction easier to inspect.

| Capability | Implemented specification |
| :--- | :--- |
| Study interval | **01 Jan 2021 to 31 Dec 2021**, fixed |
| Satellite data | Copernicus **Sentinel-1 SAR**, VV/VH |
| Spatial footprint | **256 × 256** pixels at approximately **10 m** resolution, or **2.56 × 2.56 km** |
| Model | Frozen **ResNet34 U-Net**, nine land-cover classes, provided as a verified external dependency |
| Backend | **Python 3.12**, FastAPI, HTTP/JSON |
| Frontend | Responsive **HTML5 / CSS / JavaScript** with no Node build required |
| Ports | Web/API: **8899**; local inference service: **8765** |
| Artifacts | Monthly class maps, radar previews, class-share CSVs, provenance, GeoTIFFs and recorded case exports |
| Deployment modes | Offline-from-cloud saved example; authorized new-location inference |

### Research experience

- **Visual explorer:** georeferenced land-cover previews with radar/classification opacity control.
- **Temporal navigator:** exactly twelve monthly observations for 2021. The application deliberately has no alternative-year selector.
- **Class composition:** interactive nine-class distribution, individual class trends and a dominant-class indicator.
- **Analytical review:** class-mix diversity and largest month-to-month distribution shift, explicitly distinguished from physical land-cover change.
- **Evidence access:** source-quality notes, recorded model identity and available exports.
- **Location processing:** coordinate-based Earth Engine acquisition and actual model inference when the verified runtime is installed.

## Architecture

The system separates experience, orchestration, scientific inference and source-data access. It keeps the model asset outside the application repository.

~~~mermaid
flowchart TD
  U["Researcher: coordinates / month"] --> W["JMSAR interface<br/>HTML · CSS · JavaScript"]
  W --> A["JMSAR FastAPI<br/>127.0.0.1:8899"]
  A --> G{"Saved 2021 case<br/>or new location?"}
  G -->|Saved| C["Recorded maps + source metadata"]
  G -->|New| V["Validate coordinates<br/>Fix start to 2021-01"]
  V --> S["Local inference service<br/>127.0.0.1:8765"]
  S --> E["Google Earth Engine<br/>Sentinel-1 monthly VV/VH"]
  S --> M["Verified model checkpoint<br/>Normalization · manifest"]
  E --> P["Geospatial processing<br/>12 monthly composites"]
  P --> F["Frozen segmentation inference"]
  M --> F
  F --> O["Prediction artifacts<br/>GeoTIFF · PNG · CSV · receipts"]
  O --> C
  C --> R["JMSAR study analytics<br/>class mix · trends · evidence"]
  R --> W
~~~

### Engineering boundaries

| Layer | Files | Role |
| :--- | :--- | :--- |
| Experience | `web/index.html`, `web/styles.css`, `web/app.js` | Map viewer, monthly interaction, charts, status and exports |
| Study API | `app.py` | Input validation, fixed-year enforcement, analysis and bounded local proxy |
| Setup | `SETUP_WINDOWS.cmd`, `scripts/setup.ps1` | Local environments, dependency installation and source checkout |
| Scientific engine | `vendor/SARScope/`, fetched during setup | Satellite acquisition, checkpoint validation, predictions and geospatial exports |
| Verification | `tests/test_api.py`, `.github/workflows/check.yml` | Offline API tests and JS syntax checks |
| Research record | `docs/` | Methodology, model restoration, reporting and validation |

The upstream scientific engine is downloaded into an ignored directory. For strict repeatability, a reviewer should record its Git commit, the archive checksum, Python dependencies, Earth Engine project and location used. The current setup script clones the latest default branch rather than pinning a historical commit.

### Repository structure

~~~text
JMSAR/
├── app.py
├── web/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── scripts/setup.ps1
├── tests/test_api.py
├── docs/
│   ├── MODEL_SETUP.md
│   ├── METHODOLOGY.md
│   ├── LOCAL_VALIDATION.md
│   ├── REPORT_GUIDE.md
│   └── RECORDING_GUIDE.md
├── .github/workflows/check.yml
├── .gitignore
├── requirements.txt
├── SETUP_WINDOWS.cmd
├── START_JMSAR.cmd
└── vendor/SARScope/     # Generated on setup; excluded from Git
~~~

---

# Deployment and reproducibility

Two supported paths serve different reviewer needs. **Phase 1** reproduces the application with saved 2021 imagery. **Phase 2** enables genuine new-location inference with a separately authorized model and Earth Engine project.

## Prerequisites

| Dependency | Saved-case study | New-location inference |
| :--- | :---: | :---: |
| Windows 11, 64-bit | Required for supplied launchers | Required for supplied launchers |
| Python **3.12**, 64-bit | Required | Required |
| Git for Windows | Required | Required |
| Internet during first setup | Required | Required |
| Verified inference checkpoint archive | No | **Yes** |
| Authorized Google Earth Engine and Cloud project | No | **Yes** |
| CPU PyTorch and geo-inference stack | No | **Yes** |
| Node.js | Not required | Not required |

## Phase 1: Rebuild the application

### 1. Get the source

Open **PowerShell** or a VS Code integrated terminal.

~~~powershell
cd C:\
git clone https://github.com/janvimahapadi-hub/JMSAR.git
cd JMSAR
~~~

The installation directory is flexible. The commands below run relative to the repository root.

### 2. Install

~~~powershell
.\SETUP_WINDOWS.cmd
~~~

This does the following:

1. Verifies the availability of Git and 64-bit Python 3.12.
2. Retrieves the credited scientific engine into `vendor/SARScope/`.
3. Creates independent Python virtual environments for the application and engine.
4. Installs the viewer dependencies. The script **does not download weights, training data or credentials**.

### 3. Launch

~~~powershell
.\START_JMSAR.cmd
~~~

Open **http://127.0.0.1:8899**. The launcher attempts to start the core on **http://127.0.0.1:8765**.

By default, examine the saved **Mannheim 2021** example: select individual months, compare radar and predicted maps, inspect class shares and download available results. These are saved predictions, **not** synthetic placeholders or a newly executed inference.

**Expected mode:** `SAVED STUDY` is normal until the model runtime is installed. The viewer should not claim that new inference is available before the runtime checks pass.

## Phase 2: Enable verified inference

### 1. Obtain the authorized model asset

A fresh checkout **does not contain** the model's `best.pt` weights or the prepared training dataset.

Obtain the genuine `SARScope_selected_restore.zip` archive from an authorized source. Its required inference contents are:

~~~text
RESTORE_MANIFEST.json
sarscope-baseline-20261108/
├── fp32_control_seed42/temporal/best.pt
└── prepared/
    ├── stats.json
    └── manifest.json
~~~

**Required model SHA-256**

~~~text
a52e9f4f69d4647dfad7b6b01fb3613070f91201aa4dceb004db410f6b79b2b5
~~~

The importer verifies checkpoint size, identity and hashes as well as normalization and manifest metadata. It does not accept arbitrary substituted weights. The full prepared dataset is unnecessary for inference with the existing checkpoint; it is required for re-running training.

### 2. Install the CPU inference environment

Stop existing services, open PowerShell at the JMSAR root, then run:

~~~powershell
cd .\vendor\SARScope

.\02_ENABLE_INFERENCE.cmd --bundle "C:\path\to\SARScope_selected_restore.zip"
~~~

The upstream bootstrap installs the CPU inference dependencies, imports verified assets and performs a runtime check. Initial dependency installation can be substantial.

Then verify the restored state:

~~~powershell
.\.venv\Scripts\python.exe scripts\model_assets.py status
.\.venv\Scripts\python.exe local_tools.py smoke
~~~

Confirm `weights_verified = true` and a passing runtime check. **Do not bypass asset-integrity checks.**

### 3. Authenticate Google Earth Engine

Use an Earth Engine-enabled **Google Cloud project the current account has permission to use**:

~~~powershell
.\03_SIGN_IN.cmd --project YOUR_AUTHORIZED_EARTH_ENGINE_PROJECT
~~~

A successful Google login does not guarantee project access. A permission error mentioning `serviceusage.services.use` means the current Google identity needs the appropriate IAM permission on the requested project, commonly the **Service Usage Consumer** role. Do not assume another person's project ID will work.

Earth Engine credentials must remain in the authorized user's local credentials store. Never commit account tokens, service-account keys or other secrets.

### 4. Start JMSAR and run an actual 2021 case

~~~powershell
cd ..\..
.\START_JMSAR.cmd
~~~

At **http://127.0.0.1:8899**, select **New location**, provide valid latitude and longitude, and enter the authorized Cloud project ID. Click **Run 2021 analysis**.

The request is deliberately constrained to **`start_month = 2021-01`**, yielding twelve calendar months in 2021. The server rejects alternate years rather than silently processing them.

**Execution stages**

1. Validate the coordinates, input schema and fixed 2021 window.
2. Retrieve or reuse checksum-verified Sentinel-1 monthly radar observations.
3. Apply the source engine's georeferenced preparation and recorded normalization.
4. Run the verified frozen FP32 segmentation checkpoint.
5. Produce twelve map predictions and the corresponding geospatial/statistical artifacts.
6. Read the completed case into JMSAR for map exploration and derived class-composition analysis.

**Job semantics:** A successful HTTP submission returns a **job ID**, not a completed result. Only report new inference as complete when the job reaches `state = complete` and a case ID is available.

### 5. Locate actual jobs and outputs

The inference service determines its own workspace. Do not assume it is inside JMSAR or its `vendor/` folder, especially if another core service is already running on port 8765.

~~~powershell
$ws = (Invoke-RestMethod http://127.0.0.1:8765/api/status).workspace
Write-Host "Actual inference workspace: $ws"

Get-ChildItem -Path (Join-Path $ws "jobs") -Filter "*.status.json" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 5 |
  ForEach-Object { Get-Content $_.FullName -Raw }
~~~

For a failed job, inspect the matching `*.log` in the same `jobs` directory. Successful cases are recorded under the active core's case-output workspace and are served through its API.

## Verification and quality gates

### Reviewer acceptance checklist

- [ ] Application loads on `http://127.0.0.1:8899`.
- [ ] The UI has twelve 2021 months and no switch to another year.
- [ ] Mannheim 2021 saved maps load successfully without model credentials.
- [ ] Switching months changes the displayed recorded results.
- [ ] The opacity slider changes visualization only, not predicted class shares.
- [ ] Nine-class distribution, class-specific trend and annual indicators are available.
- [ ] The case export is downloadable and contains recognizable provenance.
- [ ] With authorized assets, checkpoint hash and CPU runtime checks pass.
- [ ] With an authorized Cloud project, a fresh 2021 location reaches `complete` and exposes actual outputs.
- [ ] Saved-case evidence is clearly distinguished from new inference.

### Automated checks

After Phase 1 setup, run from the JMSAR repository root:

~~~powershell
.\.venv\Scripts\python.exe -m pip install httpx==0.28.1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

Optional Node.js syntax validation:

~~~powershell
node --check .\web\app.js
~~~

GitHub Actions runs these offline API tests and a frontend syntax check. **Continuous integration does not test Earth Engine permissions or execute a real satellite inference job.**

## Research methodology

### Scientific input

The external trained model uses Sentinel-1 VV and VH radar measurements with channel differences, annual radar statistics and an observation-support mask, forming **eight input channels**. Its ResNet34-encoder U-Net predicts nine Dynamic World-aligned labels:

|  |  |  |
| :--- | :--- | :--- |
| Water | Trees | Grass |
| Flooded vegetation | Crops | Shrub & scrub |
| Built-up land | Bare ground | Snow & ice |

The source model was trained on **2021** data representing **52 geographic regions** and **1,300 chips**, with region-separated train/validation/test partitions. Labels were derived from **Dynamic World**, providing weak supervision rather than independently surveyed ground truth.

**Upstream pretrained-model benchmark:** **74.17% overall accuracy; 42.39% mean IoU** against held-out Dynamic World-derived weak labels. These are not independent JMSAR model-training results and do not guarantee accuracy at new locations.

### Analysis measures

JMSAR computes these measures from actual monthly predicted class-share values:

| Metric | Definition | Interpretation boundary |
| :--- | :--- | :--- |
| Annual average share | Arithmetic mean of a class's 12 predicted shares | Model-based share, not surveyed area |
| Dominant class | Highest annual average predicted share | Does not imply every pixel belongs to that class |
| Adjacent-month class-mix shift | Half the sum of absolute changes in nine predicted class percentages | Distribution shift in **percentage points**, not verified physical pixel changes |
| Class-mix diversity | Shannon entropy of the predicted class distribution normalized by `ln(9)` | Diversity of represented classes, **not** model confidence or error probability |
| Radar/map opacity | UI layer blending | Does not change model inference |

### Scientific constraints

- Retrospective use of all twelve months; this is not real-time observation or forecasting.
- SAR measurements vary with moisture, scattering geometry and surface structure.
- Rare classes can be confused even when overall accuracy looks strong.
- High spatial coverage does not establish prediction correctness.
- A distribution shift can occur without confirmed physical land-cover conversion.
- The roughly **2.56 × 2.56 km** study tile and **10 m** pixel resolution cannot resolve individual buildings as surveyed footprints.
- Any ESA WorldCover comparison is an external map comparison, not verified monthly field truth.

For definitions and the evaluation protocol, see [Methodology](docs/METHODOLOGY.md).

## API interface

The two services communicate on loopback. JMSAR proxies a limited set of supported operations to the local inference core.

| Method | Route | Purpose |
| :--- | :--- | :--- |
| GET | `/api/status` | Read core and inference availability |
| GET | `/api/cases` | List cases restricted to 2021 |
| GET | `/api/cases/{id}/summary` | Return monthly shares and derived indicators |
| GET | `/api/cases/{id}/image/{month}/{kind}` | Serve recorded 2021 radar or class-map PNG |
| GET | `/api/cases/{id}/export/{filename}` | Download an allowlisted recorded artifact |
| POST | `/api/analyze` | Submit a location with fixed 2021 analysis |
| GET | `/api/jobs/{id}` | Read real upstream worker state |

Example local request after Phase 2:

~~~powershell
$body = @{ latitude = 49.4875; longitude = 8.4660; project = "YOUR_AUTHORIZED_EARTH_ENGINE_PROJECT" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8899/api/analyze -Method Post -ContentType "application/json" -Body $body
~~~

The backend supplies the fixed year internally. An accepted request should be followed by job-state polling and result inspection.

## Operations and troubleshooting

| Observation | Diagnosis | Resolution |
| :--- | :--- | :--- |
| `CORE OFFLINE` | Scientific engine not reachable on 8765 | Start/check the upstream server and query `/api/status` |
| Viewer works, new request rejected | Missing model, dependencies, credentials or verified smoke test | Complete Phase 2 and inspect core readiness |
| Earth Engine permission failure | Authenticated identity lacks rights to selected Google Cloud project | Use an authorized project or obtain project IAM access |
| Status files missing from `vendor/SARScope/workspace` | Active engine uses a different workspace | Read the real `workspace` from core `/api/status` |
| `Address already in use` | Another process owns 8765 or 8899 | Stop the existing service before relaunching |
| Job remains queued or fails | Acquisition or worker error | Read `*.status.json` and the corresponding `*.log` |
| Checkpoint rejected | Missing or incorrect archive/weights | Restore the genuine verified archive; never disable hashes |
| New output absent in UI | Job not complete, outside 2021, or different core workspace | Check `/api/jobs/{id}` and `/api/cases` |

### Security and scalability boundary

- Both application processes are designed for **trusted local use**. Do **not** expose the local ports directly to the public internet.
- Do not commit checkpoints, source training arrays, Google Earth Engine credentials or local runtime folders.
- The implementation uses a local inference worker and is **not** a multi-tenant production system.
- Production deployment would require authenticated access, queues, monitoring, resource quotas, durable job storage, rate limiting and security evaluation. These are potential future enhancements, **not implemented guarantees**.

## Reproducibility matrix

| Goal | What a reviewer needs | Status |
| :--- | :--- | :--- |
| Rebuild the user interface | This GitHub repository, Git, Python 3.12 and installation network | Supported |
| Explore a saved 2021 case | Installed viewer and bundled upstream saved-case evidence | Supported |
| Execute a fresh 2021 prediction | Verified model archive + normalization metadata + authorized Earth Engine project | Supported when configured and successful at runtime |
| Reproduce original model training | Separate prepared dataset, source training configuration and computational environment | Not delivered by this application repository |
| Establish accuracy at a new geography | Independent reference labels and a defensible evaluation protocol | Not established by a successful viewer run |

## Provenance and acknowledgements

**JMSAR is a dedicated 2021 research interface and analytical workflow integrating an existing satellite-segmentation engine.** The original trained model, training dataset, preprocessing pipeline and benchmark results originate from [SARScope](https://github.com/keyurck7/SARScope), developed by **Keyur Chaudhari**. They are not claimed as independently trained within JMSAR.

Any academic report or demonstration should distinguish the pre-existing scientific foundation from the specific interface, analysis, interpretation and validation work actually performed for the submission.

---

<div align="center">

**JMSAR · JANUARY–DECEMBER 2021**

*Inspect the signal. Examine the evidence. Respect the uncertainty.*

[Model setup](docs/MODEL_SETUP.md) · [Research methodology](docs/METHODOLOGY.md) · [Local validation](docs/LOCAL_VALIDATION.md) · [Report guide](docs/REPORT_GUIDE.md) · [Video guide](docs/RECORDING_GUIDE.md)

</div>
