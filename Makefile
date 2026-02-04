build:
	docker build -t bubthegreat/pyrom:latest .

push: build
	docker push bubthegreat/pyrom:latest

deploy: push
	kubectl config use-context homelab-k3s
	kubectl apply -k k8s/overlays/prod

deploy-dev: push
	kubectl config use-context homelab-k3s
	kubectl apply -k k8s/overlays/dev

deploy-staging: push
	kubectl config use-context homelab-k3s
	kubectl apply -k k8s/overlays/staging

install-deps:
	uv pip install --system -r requirements.txt
	uv pip install --system -e .

run-local:
	@echo "Running pyrom locally..."
	rom24

test:
	pytest tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

.PHONY: build push deploy deploy-dev deploy-staging install-deps run-local test clean

