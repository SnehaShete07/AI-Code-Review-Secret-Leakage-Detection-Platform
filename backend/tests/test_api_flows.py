from pathlib import Path


def test_repository_scan_api(client):
    repo_path = str(Path(__file__).resolve().parents[2] / "demo" / "vulnerable_repo")
    resp = client.post("/api/scans/repository", json={"repo_path": repo_path})
    assert resp.status_code == 200
    assert resp.json()["scan"]["summary"]["total"] >= 1


def test_diff_scan_api(client):
    diff = """diff --git a/app.py b/app.py\n+++ b/app.py\n@@ -1,1 +1,1 @@\n+x = eval(user_input)\n"""
    resp = client.post("/api/scans/diff", json={"diff_text": diff, "source": "unit-test"})
    assert resp.status_code == 200
    assert resp.json()["scan"]["scan_type"] == "diff"


def test_webhook_simulation(client):
    payload = {
        "action": "opened",
        "pull_request": {
            "html_url": "https://example/pr/1",
            "diff_text": "diff --git a/a.py b/a.py\n+++ b/a.py\n@@ -1,1 +1,1 @@\n+import subprocess; subprocess.run(cmd, shell=True)",
        },
    }
    resp = client.post("/api/webhooks/github", json={"payload": payload})
    assert resp.status_code == 200
    assert "pr_summary" in resp.json()
