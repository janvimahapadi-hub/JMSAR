# Local validation checklist

The repository includes a complete JMSAR source implementation, but the original checkpoint and full training dataset are **not committed**. A source commit does not imply successful live Earth Engine inference.

## Basic validation

From a Python 3.12 environment:

1. Install requirements.txt plus httpx==0.28.1 for offline API tests.
2. Run \`python -m unittest discover -s tests -v\`.
3. If Node 22 is installed, run \`node --check web/app.js\`.
4. Run \`SETUP_WINDOWS.cmd\` and \`START_JMSAR.cmd\`. Open http://127.0.0.1:8899.
5. Confirm 12 month buttons, no year switch, Mannheim 2021 case, real map PNGs, and changing class-share charts. Confirm range opacity affects display only.
6. Without the verified assets, the UI must say SAVED STUDY rather than INFERENCE READY. A new request must show a truthful failure, not mock predictions.
7. With the authorized original restore ZIP, configure model and Earth Engine as described in docs/MODEL_SETUP.md. Then test a **new 2021 site** and verify an actual worker job finishes.
8. Confirm downloadable results, output identity and georeferenced files match the baseline engine.

## What is independently implemented here

- A new single-page visual explorer built with HTML/CSS/JavaScript, no Node build dependency
- A FastAPI proxy that limits time windows to 2021 and exposes bounded study endpoints
- Class-share entropy and total-variation metrics calculated from actual monthly model output
- A model-adapter setup workflow with a credited upstream dependency

The research model remains upstream SARScope work by Keyur Chaudhari; it has not been retrained by this repository.
