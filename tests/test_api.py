"""Offline sanity tests for the JMSAR 2021 analysis adapter."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import app as study


def fixture():
    classes = [{"id": i, "name": str(i), "color": "#777777"} for i in range(9)]
    months = []
    for i in range(12):
        values = [0.0] * 9
        values[6] = 75.0 - i
        values[0] = 25.0 + i
        months.append({
            "month": f"2021-{i + 1:02d}",
            "shares": [{"class_id": k, "percent": v} for k, v in enumerate(values)],
            "coverage": 100.0,
            "radar": True
        })
    return {
        "name": "Test site",
        "spec": {"start_month": "2021-01", "latitude": 49.48, "longitude": 8.46},
        "months": months,
        "classes": classes,
        "reference": {},
        "identity": {},
        "exports": ["monthly_shares.csv"]
    }


class MetricsTests(unittest.TestCase):
    def test_total_variation_share_shift(self):
        result = study.metrics(fixture())
        self.assertEqual(len(result["monthly_mix_shifts"]), 11)
        self.assertAlmostEqual(result["monthly_mix_shifts"][0]["pp"], 1.0)
        self.assertEqual(result["dominant_class_id"], 6)
        self.assertAlmostEqual(result["annual_mean_dominant_share"], 69.5)
        self.assertTrue(0 <= result["average_class_mix_diversity"] <= 1)

    def test_2021_case_and_2021_only_image(self):
        client = TestClient(study.app)
        with patch.object(study, "core_get") as get:
            get.side_effect = lambda path, **kwargs: (
                [{"id": "mannheim", "name": "Mannheim", "period": "2021-01"},
                 {"id": "later", "name": "Later", "period": "2025-11"}]
                if path == "/api/cases" else fixture()
            )
            response = client.get("/api/cases")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)
            self.assertEqual(response.json()[0]["id"], "mannheim")
            summary = client.get("/api/cases/mannheim/summary")
            self.assertEqual(summary.status_code, 200)
            self.assertEqual(summary.json()["spec"]["start_month"], "2021-01")
            self.assertEqual(client.get("/api/cases/mannheim/image/2025-01/map").status_code, 404)
            self.assertEqual(client.get("/api/cases/ffffffffffffffff/summary").status_code, 404)

    def test_post_forces_january_2021(self):
        client = TestClient(study.app)
        with patch.object(study, "core_post", return_value={"job_id": "a" * 32}) as post:
            response = client.post("/api/analyze", json={
                "latitude": 49.4875, "longitude": 8.466,
                "project": "test-project"
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(post.call_args.args[1]["start_month"], "2021-01")
            self.assertEqual(post.call_args.args[1]["period_mode"], "historical")
            self.assertEqual(client.post("/api/analyze", json={
                "latitude": 49.48, "longitude": 8.46,
                "project": "test-project", "start_month": "2025-01"
            }).status_code, 422)


if __name__ == "__main__":
    unittest.main()
