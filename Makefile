.PHONY: test sample-json sample-markdown

test:
	python -m unittest discover -s tests

sample-json:
	python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format json --dry-run

sample-markdown:
	python -m cost_optimizer.cli --inventory examples/sample_inventory.json --format markdown --dry-run
