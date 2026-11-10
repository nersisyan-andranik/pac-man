CONFIG ?= config.json
ITCH_TARGET ?= anersisy/pac-man-42:mac
LINT_EXCLUDE = .venv,__pycache__,.git,build,dist

.PHONY: install run debug clean lint lint-strict test package deploy

install:
	uv sync

run:
	uv run python pac-man.py $(CONFIG)

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

package:
	uv run --with pyinstaller pyinstaller --noconfirm --clean pac-man.spec

deploy: package
	butler push dist/Pac-Man.app $(ITCH_TARGET)

clean:
	find . -path ./.venv -prune -o -type d \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".pytest_cache" \) -exec rm -rf {} +
	find . -path ./.venv -prune -o -type f -name "*.pyc" -delete

lint:
	uv run flake8 . --exclude $(LINT_EXCLUDE)
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude '(build|dist)/'

lint-strict:
	uv run flake8 . --exclude $(LINT_EXCLUDE)
	uv run mypy . --strict --exclude '(build|dist)/'

test:
	uv run pytest -q
