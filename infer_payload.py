# infer_payload.py
import json
import random
import argparse
from pathlib import Path

import yaml
import jsonref
import requests
from faker import Faker

fake = Faker()

REPO_PATH = Path("inventory-api")

if not REPO_PATH.exists():
    print("'inventory-api' repo not found. Run `make setup` first.")
    exit(1)


SCHEMA_DIR = REPO_PATH / "data" / "schema" / "resources"
OPENAPI_PATH = REPO_PATH / "openapi.yaml"

common_schema = None
reporter_schema = None
LOGGING_ENABLED = True
RESOURCE_TYPE = ""
REPORTER_TYPE = ""
INVENTORY_ID = None


def log(message):
    if LOGGING_ENABLED:
        print(message)

def fake_semver():
    return f"{random.randint(0, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}"

def load_openapi_spec():
    log("Loading OpenAPI spec...")
    with open(OPENAPI_PATH) as f:
        raw = yaml.safe_load(f)
    log("OpenAPI spec loaded and references resolved.")
    return jsonref.JsonRef.replace_refs(raw)

def load_json_schema(path):
    log(f"Loading schema from: {path}")
    with open(path) as f:
        schema = json.load(f)
    log("Schema loaded.")
    return schema

def generate_value(schema, path=None):
    path = path or []

    if "enum" in schema:
        value = random.choice(schema["enum"])
        log(f"Selected enum value at {'.'.join(path)}: {value}")
        return value

    if schema.get("type") == "string":
        key = path[-1].lower() if path else ""
        if key == "resourcetype":
            return RESOURCE_TYPE
        elif key == "reportertype":
            return REPORTER_TYPE
        elif key == "inventoryid" and INVENTORY_ID:
            return INVENTORY_ID
        elif key == "inventoryid" and not INVENTORY_ID:
            return None  # Skip if not explicitly provided
        elif "email" in key:
            return fake.email()
        elif "href" in key or "url" in key:
            return fake.url()
        elif "id" in key:
            return str(fake.uuid4())
        elif "version" in key:
            return fake_semver()
        return fake.word()

    if schema.get("type") == "integer":
        return random.randint(1, 100)
    if schema.get("type") == "boolean":
        return random.choice([True, False])
    if schema.get("type") == "array":
        item = generate_value(schema.get("items", {}), path + ["[]"])
        log(f"Generated array at {'.'.join(path)}: {item}")
        return [item]

    if schema.get("type") == "object":
        log(f"Generating object from schema properties at {'.'.join(path)}...")
        props = schema.get("properties", {})
        obj = {}
        for k, v in props.items():
            new_path = path + [k]
            if k == "commonResourceData": ## TODO change later
                log(f"Injecting common schema into {'.'.join(new_path)}")
                obj[k] = generate_value(common_schema, new_path)
            elif k == "resourceData": ## TODO change later
                log(f"Injecting reporter schema into {'.'.join(new_path)}")
                reporter_data = generate_value(reporter_schema, new_path)
                obj[k] = reporter_data
            else:
                val = generate_value(v, new_path)
                if val is not None:
                    obj[k] = val
        log(f"Generated object at {'.'.join(path)}: {obj}")
        return obj

    return fake.word()

def get_valid_combinations():
    combos = []
    for resource_dir in SCHEMA_DIR.iterdir():
        if (resource_dir / "reporters").exists():
            for reporter_dir in (resource_dir / "reporters").iterdir():
                if (reporter_dir / f"{resource_dir.name}.json").exists():
                    combos.append((resource_dir.name, reporter_dir.name.upper()))
    return combos

def get_resource_reporter_schemas(resource_type, reporter_type):
    resource_path = SCHEMA_DIR / resource_type
    reporter_path = resource_path / "reporters" / reporter_type.lower()

    log(f"Getting schemas for resource '{resource_type}' and reporter '{reporter_type}'...")
    common = load_json_schema(resource_path / "common_resource_data.json")
    reporter = load_json_schema(reporter_path / f"{resource_type}.json")
    return common, reporter

def generate_report_resource_payload(openapi, resource_type, reporter_type):
    global common_schema, reporter_schema, RESOURCE_TYPE, REPORTER_TYPE
    RESOURCE_TYPE = resource_type
    REPORTER_TYPE = reporter_type

    log("Generating ReportResourceRequest payload...")
    
    try:
        schema = openapi["components"]["schemas"]["kessel.inventory.v1beta2.ReportResourceRequest"]
    except KeyError as e:
        raise ValueError("OpenAPI schema is missing 'kessel.inventory.v1beta2.ReportResourceRequest'") from e

    common_schema, reporter_schema = get_resource_reporter_schemas(resource_type, reporter_type)

    log("Generating values based on schema...")
    payload = generate_value(schema, path=[])

    log("Payload generated successfully.")
    return payload


def send_request(endpoint, payload, method="post"):
    log(f"Sending {method.upper()} request to {endpoint}...")
    try:
        response = requests.request(method, endpoint, json=payload)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(response.text)
    except Exception as e:
        print(f"Failed to send request: {e}")

def main():
    global LOGGING_ENABLED, INVENTORY_ID

    combos = get_valid_combinations()
    combo_str = "\n  " + "\n  ".join([f"{r} + {t}" for r, t in combos])

    parser = argparse.ArgumentParser(
        description="Generate payload for ReportResourceRequest or DeleteResourceRequest",
        epilog=f"\nValid resource/reporter combinations:{combo_str}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    method_group = parser.add_mutually_exclusive_group(required=False)
    method_group.add_argument("--post", help="POST the payload to the given endpoint")
    method_group.add_argument("--delete", help="DELETE the payload to the given endpoint")

    parser.add_argument("--resource", help="Resource type (required for POST)")
    parser.add_argument("--reporter", help="Reporter type (required for POST and DELETE)")
    parser.add_argument("--inventory-id", help="Optional inventory ID to include in payload")
    parser.add_argument("--local-resource-id", help="Local resource ID (required for DELETE)")
    parser.add_argument("--quiet", action="store_true", help="Suppress logging output")
    parser.add_argument("--output", help="Path to write the generated payload to a file (e.g., output.json)")

    args = parser.parse_args()

    # Logging config
    LOGGING_ENABLED = not args.quiet
    if LOGGING_ENABLED:
        print("Logging enabled")
    else:
        print("Logging disabled via --quiet")

    # Determine method and endpoint
    method = None
    endpoint = None
    if args.post:
        method = "post"
        endpoint = args.post
    elif args.delete:
        method = "delete"
        endpoint = args.delete

    # Validation
    if method == "post":
        if not args.resource or not args.reporter:
            parser.error("--resource and --reporter are required with --post")
    elif method == "delete":
        if not args.reporter or not args.local_resource_id:
            parser.error("--reporter and --local-resource-id are required with --delete")
    elif not args.output:
        parser.error("Must provide either --post, --delete, or --output")

    # Inventory ID for injection
    INVENTORY_ID = args.inventory_id

    log("Parsed arguments:")
    log(vars(args))

    log("Starting payload inference...")
    openapi = load_openapi_spec()

    if method == "post":
        payload = generate_report_resource_payload(openapi, args.resource, args.reporter)
    elif method == "delete":
        payload = {
            "localResourceId": args.local_resource_id,
            "reporterType": args.reporter
        }
    else:
        # Generate payload without sending
        if not args.resource or not args.reporter:
            parser.error("--resource and --reporter are required when not using --post or --delete")
        payload = generate_report_resource_payload(openapi, args.resource, args.reporter)

    print("Final Payload:")
    print(json.dumps(payload, indent=2))

    if endpoint:
        send_request(endpoint, payload, method=method)

    if args.output:
        log(f"Writing payload to {args.output}")
        try:
            with open(args.output, "w") as f:
                json.dump(payload, f, indent=2)
            log("Payload written successfully.")
        except Exception as e:
            print(f"Failed to write payload to file: {e}")

if __name__ == "__main__":
    main()