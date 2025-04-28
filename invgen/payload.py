from .schema_loader import get_resource_reporter_schemas
from .utils import log, fake_semver, fake
from .constants import *
import random

def generate_value(schema, path=None):
    path = path or []

    if "enum" in schema:
        value = random.choice(schema["enum"])
        log(f"Selected enum value at {'.'.join(path)}: {value}")
        return value

    if schema.get("type") == "string":
        key = path[-1].lower() if path else ""
        if key == "type":
            return RESOURCE_TYPE
        elif key == "reportertype":
            return REPORTER_TYPE
        elif key == "inventoryid" and INVENTORY_ID:
            return INVENTORY_ID
        elif key == "inventoryid":
            return None
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
        log(f"Generating OpenAPI object at {'.'.join(path)}...")
        return generate_openapi_object(schema, path)

    return fake.word()


def generate_from_json_schema(schema, path=None):
    path = path or []

    if "enum" in schema:
        return random.choice(schema["enum"])

    if schema.get("type") == "string":
        key = path[-1].lower() if path else ""
        if schema.get("format") == "uuid" or "id" in key:
            return str(fake.uuid4())
        elif "version" in key:
            return fake_semver()
        return fake.word()

    if schema.get("type") == "integer":
        return random.randint(1, 100)

    if schema.get("type") == "boolean":
        return random.choice([True, False])

    if schema.get("type") == "array":
        return [generate_from_json_schema(schema.get("items", {}), path + ["[]"])]

    if schema.get("type") == "object":
        obj = {}
        props = schema.get("properties", {})
        for k, v in props.items():
            val = generate_from_json_schema(v, path + [k])
            if val is not None:
                obj[k] = val
        return obj

    return fake.word()



def generate_openapi_object(openapi_schema, path):
    props = openapi_schema.get("properties", {})
    obj = {}

    for k, v in props.items():
        new_path = path + [k]

        # Special-case: switch to JSON schema
        if new_path == ["resource", "representations", "reporter"]: # Change paths when json schema moves, or new json schema is added
            log(f"Generating JSON schema for reporterData.resourceData at {'.'.join(new_path)}")
            obj[k] = generate_from_json_schema(reporter_schema, new_path)
            continue

        if new_path == ["resource","representations", "common"]:  # Change paths when json schema moves, or new json schema is added
            log(f"Generating JSON schema for commonRepresentation at {'.'.join(new_path)}")
            obj[k] = generate_from_json_schema(common_schema, new_path)
            continue

        # Otherwise, recurse normally
        val = generate_value(v, new_path)
        if val is not None:
            obj[k] = val

    return obj


def generate_report_resource_payload(openapi, resource_type, reporter_type):
    global RESOURCE_TYPE, REPORTER_TYPE, common_schema, reporter_schema
    RESOURCE_TYPE = resource_type
    REPORTER_TYPE = reporter_type

    schema = openapi["components"]["schemas"]["kessel.inventory.v1beta2.ReportResourceRequest"]
    common_schema, reporter_schema = get_resource_reporter_schemas(resource_type, reporter_type)

    return generate_value(schema, path=[])
