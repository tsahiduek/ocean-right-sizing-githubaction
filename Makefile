VAR?=5
all: run 

.PHONY: run
run: ## Run localy
	docker run --rm --name gha-test  -v $(shell pwd)/:/app/  -e SPOT_OCEAN_ID=${SPOT_OCEAN_ID} -e SPOT_OCEAN_CONTROLLER=${SPOT_OCEAN_CONTROLLER} \
 -e SPOT_TOKEN=${SPOT_TOKEN} -e SPOT_ACCOUNT=${SPOT_ACCOUNT} gh-test

