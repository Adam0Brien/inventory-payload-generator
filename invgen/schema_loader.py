import json, yaml
from pathlib import Path
import jsonref
from .utils import log
from .constants import *
import requests
import yaml
import json
import jsonref

def load_openapi_spec_from_url():
    response = requests.get(OPENAPI_URL)
    response.raise_for_status()
    raw = yaml.safe_load(response.text)
    return jsonref.JsonRef.replace_refs(raw)


def load_json_schema_from_url(resource, reporter=None, ):
    if reporter:
        url = f"{SCHEMA_BASE_URL}/{resource}/reporters/{reporter.lower()}/{resource}.json"
    else:
        url = f"{SCHEMA_BASE_URL}/{resource}/common_representation.json"

    response = requests.get(url)
    response.raise_for_status()
    return response.json()



def load_openapi_spec(remote=REMOTE):
    if remote:
        log("Loading OpenAPI spec (remote)...")
        return load_openapi_spec_from_url()
    else:
        log("Loading OpenAPI spec (local)...")
        with open(OPENAPI_PATH) as f:
            raw = yaml.safe_load(f)
        return jsonref.JsonRef.replace_refs(raw)


def load_json_schema(path, remote=REMOTE, resource=None, reporter=None):
    if remote:
        return load_json_schema_from_url(resource, reporter)
    else:
        with open(path) as f:
            return json.load(f)

def get_resource_reporter_schemas(resource_type, reporter_type, remote=REMOTE):
    if remote:
        common = load_json_schema_from_url(resource_type)
        reporter = load_json_schema_from_url(resource_type, reporter_type)
    else:
        resource_path = SCHEMA_DIR / resource_type
        reporter_path = resource_path / "reporters" / reporter_type.lower()

        log(f"Getting schemas for resource '{resource_type}' and reporter '{reporter_type}'...")
        common = load_json_schema(resource_path / "common_representation.json", remote=False)
        reporter = load_json_schema(reporter_path / f"{resource_type}.json", remote=False)

    return common, reporter
