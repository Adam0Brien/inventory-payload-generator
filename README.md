# Inventory Payload Generator

This CLI tool generates valid example payloads for the [Kessel inventory-api](https://github.com/project-kessel/inventory-api), based on its OpenAPI spec and JSON schemas.

It supports:
- Inferring values from the OpenAPI + JSON Schema filesystem structure
- Sending POST and DELETE requests to the inventory-api resource endpoint
- Saving generated payloads to disk
- Keeping `inventory-api` up to date locally using `make`

## Setup

```bash
pip install -r requirements.txt
make setup
```

## Usage

CLI arguments are used to decide what type of resource you want to generate along with where you want to send it. 

#### Example:
"I want a host resource with reporter type HBI and I would like the payload saved to `payloads/host_HBI.json`"

```py
invgen \
  --resource host \
  --reporter HBI \
  --output payloads/host_HBI.json
```

### CLI arguments

### Help

Help gives the list of cli args aswell as a list of the current valid reporter_type/resource_type combos
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
    "reporterData": {
      "reporterType": "HBI",
      "reporterInstanceId": "41c2424b-aad9-4b43-a52c-9abba5e12da3",
      "reporterVersion": "3.4.18",
      "localResourceId": "6a119e1f-9f3b-4542-be60-c8a2f05275c1",
      "apiHref": "https://www.greene.org/",
      "consoleHref": "https://thomas.com/",
      "resourceData": {
        "satellite_id": "231755a4-1ae9-419e-905b-d3a73138a42f",
        "sub_manager_id": "33ce6023-164f-41c7-81a8-0906272e9efe",
        "insights_inventory_id": "4e3f4b71-f764-423e-8aed-19ad10967824",
        "ansible_host": "agreement"
      }
    },
    "commonResourceData": {
      "workspace_id": "4e7bd344-ddff-47ca-be98-f0634f22fd81"
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
  --local-resource-id 6a119e1f-9f3b-4542-be60-c8a2f05275c1 \
  --delete http://localhost:8000/api/inventory/v1beta2/resources --quiet

Logging disabled via --quiet
Final Payload:
{
  "localResourceId": "6a119e1f-9f3b-4542-be60-c8a2f05275c1",
  "reporterType": "HBI"
}
Status: 200
Response:
{}

```