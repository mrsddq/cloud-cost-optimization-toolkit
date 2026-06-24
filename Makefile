.PHONY: test validate lint security-scan deploy destroy local-demo docker-build docker-run sample-json sample-markdown sample-html

test:
	python -m unittest discover -s tests

validate: test sample-json sample-markdown sample-html

lint:
	python -m compileall -q cost_optimizer tests scripts

security-scan:
	python scripts/security_scan.py

deploy:
	@echo "No resources are deployed by default. Use --from-aws for read-only AWS collection after credentials are configured."

destroy:
	@echo "No resources are created by this toolkit, so there is nothing to destroy."

local-demo: sample-markdown docker-build docker-run

docker-build:
	docker build -t cloud-cost-optimizer:local .

docker-run:
	docker run --rm cloud-cost-optimizer:local

sample-json:
	python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format json --dry-run

sample-markdown:
	python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format markdown --dry-run

sample-html:
	python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format html --output sample-report.html --dry-run
