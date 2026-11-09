ITCH_TARGET ?= anersisy/pac-man-42:mac

.PHONY: install run debug clean lint lint-strict test package deploy

install:
	uv sync

run:
	uv run python pac-man.py config.json

debug:
	uv run python -m pdb pac-man.py config.json

package:
	uv run --with pyinstaller pyinstaller --noconfirm --clean pac-man.spec

deploy: package
	@test -n "$(ITCH_TARGET)" || (echo "Usage: make deploy ITCH_TARGET=owner/game:mac"; exit 2)
	butler push dist/Pac-Man.app $(ITCH_TARGET)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 . --exclude .venv,__pycache__,.git,llm_sdk
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude llm_sdk

lint-strict:
	flake8 . --exclude .venv,__pycache__,.git,llm_sdk
	mypy . --strict --exclude llm_sdk
	
test:
	pytest -q
