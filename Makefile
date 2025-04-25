REPO_URL=https://github.com/project-kessel/inventory-api.git
REPO_DIR=inventory-api
BRANCH_NAME=main # <-- you can change this!

.PHONY: all setup clean

all: setup

setup:
	pip install -r requirements.txt
	pip install -e .
	@if [ -d "$(REPO_DIR)" ]; then \
		echo "Repo already cloned."; \
	else \
		echo "Cloning inventory-api..."; \
		git clone --branch $(BRANCH_NAME) $(REPO_URL) $(REPO_DIR); \
	fi

update:
	@if [ -d "$(REPO_DIR)" ]; then \
		echo "Updating inventory-api..."; \
		cd $(REPO_DIR) && git pull; \
	else \
		echo "Repo not found. Run 'make setup' first."; \
		exit 1; \
	fi

clean:
	@echo "Removing inventory-api..."
	@rm -rf $(REPO_DIR)
