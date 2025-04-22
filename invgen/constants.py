from pathlib import Path

OPENAPI_URL = "https://raw.githubusercontent.com/project-kessel/inventory-api/main/openapi.yaml"
SCHEMA_BASE_URL = "https://api.github.com/repos/project-kessel/inventory-api/contents/data/schema/resources"


# BASE_DIR is the directory where this file resides
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_PATH = BASE_DIR / "inventory-api"
SCHEMA_DIR = REPO_PATH / "data" / "schema" / "resources"
OPENAPI_PATH = REPO_PATH / "openapi.yaml"

SCHEMA_DIR = REPO_PATH / "data" / "schema" / "resources"
OPENAPI_PATH = REPO_PATH / "openapi.yaml"

## TODO get remote working properly
REMOTE = False

common_schema = None
reporter_schema = None
RESOURCE_TYPE = ""
REPORTER_TYPE = ""

LOGGING_ENABLED = True
INVENTORY_ID = None

def set_logging(enabled):
    global LOGGING_ENABLED
    LOGGING_ENABLED = enabled

def set_inventory_id(inventory_id):
    global INVENTORY_ID
    INVENTORY_ID = inventory_id
