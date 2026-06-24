FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY cost_optimizer ./cost_optimizer
COPY config ./config
COPY examples ./examples

RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 appuser

USER appuser

ENTRYPOINT ["cloud-cost-audit"]
CMD ["--inventory", "examples/sample_inventory.json", "--format", "markdown", "--dry-run"]
