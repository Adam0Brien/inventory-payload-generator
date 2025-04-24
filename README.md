# Inventory Payload Generator

This CLI tool generates valid example payloads for the [Kessel inventory-api](https://github.com/project-kessel/inventory-api), based on its OpenAPI spec and JSON schemas.

It supports:
- Inferring values from the OpenAPI + JSON Schema filesystem structure
- Sending POST and DELETE requests to the inventory-api resource endpoint
- Saving generated payloads to disk

![demo](https://github.com/Adam0Brien/inventory-payload-generator/blob/main/demo.gif)

## Setup

```bash
make setup
```

## Usage

CLI arguments are used to decide what type of resource you want to generate along with where you want to send it. 

#### Example:
"I want a `host` resource with reporter type `HBI` and I would like the payload saved to `payloads/host_HBI.json`"

```py
invgen \
  --resource host \
  --reporter HBI \
  --output payloads/host_HBI.json
```

### CLI arguments

```py
invgen --help

```

| Option                | Description                                                   |
|-----------------------|---------------------------------------------------------------|
| `--post URL`          | Send the payload as a POST to the given endpoint              |
| `--delete URL`        | Send the payload as a DELETE request                          |
| `--resource`          | Resource type (e.g. `host`, required for POST)          |
| `--reporter`          | Reporter type (e.g. `HBI`, required for both POST and DELETE) |
| `--local-resource-id` | Local resource ID to delete (required for DELETE)             |
| `--inventory-id`      | Optionally set the inventory ID in the payload                |
| `--output FILE.json`  | Save the generated payload to a file                          |
| `--quiet`             | Suppress logs                                                 |


#### Another example

Generating a hbi host, posting the payload, saving to file
```py
invgen \
  --resource host \
  --reporter HBI \
  --post http://localhost:8000/api/inventory/v1beta2/resources \
  --output payloads/host_HBI.json --quiet

Logging disabled via --quiet
Final Payload:
{
  "resource": {
    "resourceType": "host",
    "reporterType": "HBI",
    "reporterInstanceId": "776225b7-c857-4690-ae22-d6e66bbab519",
    "resourceRepresentation": {
      "representationMetadata": {
        "localResourceId": "4fcc4047-7133-4ac9-9405-9064496ad9c2",
        "apiHref": "http://morris.com/",
        "consoleHref": "http://matthews.info/",
        "reporterVersion": "1.0.6"
      },
      "common": {
        "workspace_id": "44aab1e1-c323-4d7c-88e0-79ac4d468ff6"
      },
      "reporter": {
        "satellite_id": "c7c73f12-7dd6-41ce-a7ed-1158e06b652a",
        "sub_manager_id": "1a159006-d2dc-4604-95fd-d727d0d16e5c",
        "insights_inventory_id": "4296814e-d050-4cc5-a9e6-5f71360c3569",
        "ansible_host": "police"
      }
    }
  }
}

Status: 200
Response:
{}
```

Deleting the hbi host (Ensure `local-resource-id` is the same)
```py
invgen \
  --reporter HBI \
  --local-resource-id 4fcc4047-7133-4ac9-9405-9064496ad9c2 \
  --delete http://localhost:8000/api/inventory/v1beta2/resources --quiet

Logging disabled via --quiet
Final Payload:
{
  "localResourceId": "4fcc4047-7133-4ac9-9405-9064496ad9c2",
  "reporterType": "HBI"
}
Status: 200
Response:
{}

```

# Note
If the cli does not work run with python
```sh
python main.py --resource host --reporter HBI --output HBI_host.json
```