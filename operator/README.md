# Predictive Autoscaler Kubernetes Operator

A Kubernetes-native predictive autoscaling operator built in **Go** using **controller-runtime**, fulfilling **Sahil Kukreja's** role in the project proposal.

## Architecture

```
[ Tanay: Python + Prophet ML Service (FastAPI) ]
                       │
                       │ HTTP GET /api/v1/forecast/{workload}
                       ▼
[ Sahil: Go Operator Controller (Reconcile Loop) ]
                       │
                       │ Kubernetes API (scale Deployment)
                       ▼
[ Target Workload Deployment (Pods on Kind Nodes) ]
```

## Folder Structure

```text
operator/
├── api/v1alpha1/
│   └── types.go         # CRD struct definitions (Spec, Status, DeepCopy)
├── controllers/
│   └── controller.go    # Reconciler loop (queries FastAPI & scales pods)
├── config/
│   ├── crd.yaml         # Kubernetes CRD manifest
│   ├── demo_app.yaml    # Sample Nginx deployment for testing
│   └── scaler.yaml      # Sample PredictiveAutoscaler resource
├── Dockerfile           # Minimal distroless container image build
├── Makefile             # One-command workflows (make run, make demo)
├── main.go              # Operator manager entrypoint
└── README.md
```

## Quick Start with Kind

### 1. Install CRD into Kind
```bash
make install
# or: kubectl apply -f config/crd.yaml
```

### 2. Start the Operator
Ensure Tanay's FastAPI service is running on port 8000, then in the `operator/` directory run:
```bash
make run
# or: go run main.go
```

### 3. Deploy Demo App & Autoscaler
In another terminal:
```bash
make demo
```

### 4. Observe Scaling in Real-time
```bash
# Watch the custom resource status
kubectl get pa -w

# Watch pods scaling across Kind worker nodes
kubectl get pods -o wide -w
```
