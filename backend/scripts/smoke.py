"""Exercise every service + router path against the loaded data. No server needed.

    python scripts/smoke.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def main() -> None:
    with TestClient(app) as client:
        checks: list[tuple[str, str]] = [
            ("GET", "/api/health"),
            ("GET", "/api/overview"),
            ("GET", "/api/grid/feeders"),
            ("GET", "/api/comparison/pipeline"),
            ("GET", "/api/investigations"),
            ("GET", "/api/job-cards"),
            ("GET", "/api/field/overview"),
            ("GET", "/api/field/jobs"),
            ("GET", "/api/admin/data-sources"),
            ("GET", "/api/admin/model-services"),
            ("GET", "/api/admin/audit"),
        ]
        for method, path in checks:
            r = client.request(method, path)
            n = len(r.json()) if isinstance(r.json(), list) else "-"
            print(f"{r.status_code}  {method:4} {path:40} items={n}")
            r.raise_for_status()

        feeder_id = client.get("/api/grid/feeders").json()[0]["id"]
        pmts = client.get(f"/api/grid/feeders/{feeder_id}/pmts").json()
        print(f"      feeder {feeder_id} -> {len(pmts)} pmts")
        pmt_id = pmts[0]["id"]
        consumers = client.get(f"/api/grid/pmts/{pmt_id}/consumers").json()
        print(f"      pmt {pmt_id} -> {len(consumers)} consumers")
        client.get(f"/api/grid/pmts/{pmt_id}").raise_for_status()

        invs = client.get("/api/investigations").json()
        print(f"      investigations: {len(invs)}")
        if invs:
            cid = invs[0]["consumerId"]
            for suffix in ("", "/explanation", "/monthly", "/hourly"):
                r = client.get(f"/api/investigations/{cid}{suffix}")
                print(f"      {r.status_code}  /investigations/{cid}{suffix}")
                r.raise_for_status()
            exp = client.get(f"/api/investigations/{cid}/explanation").json()
            print(f"      top driver: {exp['treeShapContributions'][0]['featureName']}")

        # analysis job round-trip
        job = client.post(
            "/api/analyses", json={"scope": "Entire Grid", "pipelines": "Both"}
        ).json()
        print(f"      created job {job['id']} status={job['status']}")
        client.get(f"/api/analyses/{job['id']}").raise_for_status()

        # job card create + patch
        if invs:
            inv = invs[0]
            new_card = client.post(
                "/api/job-cards",
                json={
                    "consumerId": inv["consumerId"], "meterId": inv["meterId"],
                    "serviceArea": "Test Division", "feederId": inv["feederId"],
                    "pmtId": inv["pmtId"], "priority": "High",
                    "evidenceSummary": "smoke", "relevantPeriodsText": "smoke",
                    "estimatedImpactKWhMonth": 100.0, "safeguardsSummary": "smoke",
                    "recommendedChecks": ["a", "b"], "analystNotes": "smoke",
                    "assignedTeam": "Squad Alpha", "scheduledDate": "2026-09-10",
                },
            ).json()
            print(f"      created card {new_card['id']}")
            patched = client.patch(
                f"/api/job-cards/{new_card['id']}", json={"status": "Accepted"}
            ).json()
            assert patched["status"] == "Accepted"
            fr = client.post(
                f"/api/field/jobs/{new_card['id']}/findings",
                json={
                    "jobCardId": new_card["id"], "meterSealCondition": "Tampered",
                    "meterCondition": "Normal", "wiringCondition": "Bypassed",
                    "bypassEvidenceObserved": True, "loadObservedKW": 12.0,
                    "siteAccessStatus": "Accessible", "consumerPresent": True,
                    "attachmentPlaceholders": [], "inspectorNotes": "smoke",
                    "outcome": "Irregularity Observed", "submittedAt": "2026-09-03 10:00 PKT",
                    "submittedBy": "smoke.tester",
                },
            ).json()
            print(f"      finding submitted: {fr}")

    print("\nALL SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()
