import argparse
import json
from .schema_loader import load_openapi_spec
from .payload import generate_report_resource_payload
from .utils import *
import os

LOGGING_ENABLED = True
INVENTORY_ID = None

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


    args = parser.parse_args()
    LOGGING_ENABLED = not args.quiet
    INVENTORY_ID = args.inventory_id

    log("Parsed arguments:")
    log(vars(args))
    log("Starting payload inference...")

    openapi = load_openapi_spec()

    if args.post or args.output:
        payload = generate_report_resource_payload(openapi, args.resource, args.reporter)

    elif args.delete:
        payload = {
            "localResourceId": args.local_resource_id,
            "reporterType": args.reporter
        }

    print("Final Payload:")
    print(json.dumps(payload, indent=2))

    if args.post:
        send_request(args.post, payload)

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(payload, f, indent=2)
        log(f"Wrote payload to {args.output}")
