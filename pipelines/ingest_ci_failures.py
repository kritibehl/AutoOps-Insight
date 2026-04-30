import requests

API = "http://127.0.0.1:8001/ingest"

def send_log(file_path, repo):
    with open(file_path, "rb") as f:
        res = requests.post(
            API,
            headers={
                "X-AutoOps-Token": "dev-token",
                "X-Repo-Name": repo,
                "X-Workflow-Name": "CI",
                "X-Run-Id": "pipeline-run"
            },
            files={"file": f}
        )
    print(res.json())

if __name__ == "__main__":
    send_log("../samples/kubepulse_dns.log", "kubepulse")
    send_log("../samples/faultline_timeout.log", "faultline")
    send_log("../samples/faireval_latency.log", "faireval")
