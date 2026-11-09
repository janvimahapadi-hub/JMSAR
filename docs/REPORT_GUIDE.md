# Individual report worksheet (fill only with real completed work)

**Project:** JMSAR: Retrospective Sentinel-1 Land-Cover Study for 2021

**Student:** [Student name]

**Research question:** [e.g., How stable are class-share distributions over 2021 in two contrasting geographic environments?]

## 1. Objective

Explain the precise analysis question, region choices, and what SAR can and cannot measure.

## 2. Source and scientific provenance

Acknowledge the SARScope checkpoint, original training and benchmark work by Keyur Chaudhari. Document your own contributions separately. Cite Sentinel-1, Dynamic World and, if used, WorldCover 2021.

## 3. Data and methods

Record 2021 coordinates, fixed 10 m grid, actual Sentinel-1 observations, model input channels, labels, preprocessing, and which code/artifacts were reused. Document how you interpreted monthly class shares and class-mix shifts.

## 4. Implementation

Describe the JMSAR reader, 2021-only scope, interactive overlay and additional summary calculations. Only claim an implementation if you actually worked on it.

## 5. Results

Include **real** application screenshots, the twelve months' actual class-share values, the largest month-to-month mix shift, and a map of a case needing closer review. If no fresh inference was run, explicitly say the study used the saved Mannheim result.

## 6. Critical evaluation

Discuss the difference between held-out weak-label model benchmarking and independent local accuracy. Consider class dominance, reference mismatch, seasonal effects, scene availability and the limits of 10 m resolution. Never state a monthly share shift as a measured physical conversion.

## 7. Conclusions

Explain what you learned and what evidence would be needed before operational use. Distinguish proven functions from hypothetical upgrades.

## 8. References

- SARScope: https://github.com/keyurck7/SARScope
- Sentinel-1 Earth Engine guide: https://developers.google.com/earth-engine/guides/sentinel1
- Dynamic World V1: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
- ESA WorldCover 2021 v200: https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200
