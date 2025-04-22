import random
import requests
from faker import Faker
from .constants import *
import re

fake = Faker()

def log(message):
    print(message)

def fake_semver():
    return f"{random.randint(0, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}"

def send_request(endpoint, payload, method="post"):
    log(f"Sending {method.upper()} request to {endpoint}...")
    try:
        response = requests.request(method, endpoint, json=payload)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(response.text)
    except Exception as e:
        print(f"Failed to send request: {e}")

def get_valid_combinations(remote=REMOTE):
    if remote:
        response = requests.get(SCHEMA_BASE_URL)
        response.raise_for_status()
        resources = response.json()

        combos = []
        for resource in resources:
            resource_name = resource["name"]
            reporters_url = f"{resource['url']}/reporters"
            reporters_resp = requests.get(reporters_url)
            if reporters_resp.status_code != 200:
                continue

            reporters = reporters_resp.json()
            for reporter in reporters:
                if re.search(f"{resource_name}\\.json$", reporter["name"]):
                    combos.append((resource_name, reporter["name"].split(".")[0].upper()))

        return combos
    else:
        combos = []
        for resource_dir in SCHEMA_DIR.iterdir():
            if (resource_dir / "reporters").exists():
                for reporter_dir in (resource_dir / "reporters").iterdir():
                    if (reporter_dir / f"{resource_dir.name}.json").exists():
                        combos.append((resource_dir.name, reporter_dir.name.upper()))
        return combos



