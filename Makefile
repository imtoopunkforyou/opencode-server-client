# === Configuration ===
MAKEFLAGS += --silent
make:
	cat ./Makefile

# === Dev ===
.PHONY: mypy
mypy:
	poetry run mypy ./opencode_server_client --no-pretty

.PHONY: lint
lint:
	poetry run ruff format ./opencode_server_client ./tests \
	&& poetry run ruff check ./opencode_server_client ./tests \
	&& echo "✓ Ruff checks" \
	&& poetry run flake8 ./opencode_server_client \
	&& echo "✓ Flake8 checks" \
	&& make mypy \
	&& echo "✓ Mypy checks" \
	&& poetry run codespell --skip="*.lock,./htmlcov," \
	&& echo "✓ Codespell checks" \
	&& poetry run pymarkdown scan . \
	&& echo "✓ Markdown checks"

.PHONY: tests
tests:
	poetry run pytest ./tests/

.PHONY: all
all:
	make lint \
	&& make tests \
	&& echo "✓ All checks have been successfully completed!"

# === Aliases ===
l: lint
t: tests
a: all
