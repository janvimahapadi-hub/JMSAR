# Enabling new coordinates in 2021

The JMSAR workspace is a dedicated 2021 study interface. The scientific inference engine is the externally maintained, credited [SARScope](https://github.com/keyurck7/SARScope) model and processor.

1. Run SETUP_WINDOWS.cmd; it installs the original core at vendor/SARScope.
2. Obtain the legitimate original SARScope_selected_restore.zip. A clone of the GitHub source does **not** include best.pt or the training arrays.
3. Open a Windows terminal in vendor/SARScope and run:

   02_ENABLE_INFERENCE.cmd --bundle "C:\full\path\to\SARScope_selected_restore.zip"

   This imports the three essential inference assets (checkpoint, normalization stats and prepared manifest) and verifies the exact SHA-256. Do not substitute arbitrary weights or disable its integrity check.

4. Sign into your **own authorized** Google Earth Engine account and project:

   03_SIGN_IN.cmd --project YOUR_EARTH_ENGINE_PROJECT

5. Close both local servers if running. Return to the JMSAR root and launch START_JMSAR.cmd.
6. At http://127.0.0.1:8899, enter coordinates and the Earth Engine project, then use "Run 2021 analysis". The server forces start_month=2021-01 and shows the job status. Inspect actual maps only after completion.

**Model SHA-256:** a52e9f4f69d4647dfad7b6b01fb3613070f91201aa4dceb004db410f6b79b2b5.

**No credentials in Git:** Do not upload Earth Engine credentials, tokens, original restore ZIPs, or training arrays to this public repository. Each collaborator must be authorized to access any separately hosted model/data. The repository's .gitignore excludes those artifacts.

**Limits:** Historical Sentinel-1 requests may have sparse coverage, and predictions in the fixed 2021 256 × 256 / 10 m tile are not surveyed ground truth. This model uses all 12 months as retrospective context. "New request" does not mean a real-time satellite broadcast.
