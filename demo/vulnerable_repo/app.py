import subprocess
import requests

def run(user_input: str):
    token = "Bearer sk_live_ABCDEF1234567890ABCDEF"
    subprocess.run(f"echo {user_input}", shell=True)
    return eval(user_input)

resp = requests.get("https://internal.example", verify=False)
print(resp.status_code)
