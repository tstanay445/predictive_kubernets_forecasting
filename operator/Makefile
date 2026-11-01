.PHONY: all build run install uninstall demo clean

all: build

## Install CRD into Kind cluster
install:
	kubectl apply -f config/crd.yaml

## Uninstall CRD from cluster
uninstall:
	kubectl delete -f config/crd.yaml

## Build manager binary
build:
	go build -o bin/manager main.go

## Run operator controller locally against current kubecontext
run:
	go run main.go

## Deploy sample target application and PredictiveAutoscaler CR
demo:
	kubectl apply -f config/demo_app.yaml
	kubectl apply -f config/scaler.yaml

clean:
	rm -rf bin/
