# Pyrom Kubernetes Deployment

This directory contains Kustomize-based Kubernetes manifests for deploying Pyrom (ROM24 Python MUD server).

## Structure

```
k8s/
├── base/                    # Base manifests (shared across all environments)
│   ├── pyrom-deployment.yaml
│   ├── pyrom-service.yaml
│   ├── pyrom-ingress.yaml
│   ├── pyrom-pvc.yaml
│   ├── pyrom-configmap.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── prod/                # Production environment
│   ├── staging/             # Staging environment
│   └── dev/                 # Development environment
└── ingress-nginx/
    └── tcp-services-configmap.yaml  # TCP routing configuration
```

## Environments

### Production
- **Namespace**: `pyrom-prod`
- **Telnet**: `telnet 192.168.0.20 1337` or `telnet pyrom.bubtaylor.com 1337`
- **Deploy**: `kubectl apply -k k8s/overlays/prod`

### Staging
- **Namespace**: `pyrom-staging`
- **Telnet**: `telnet 192.168.0.20 1338` or `telnet pyrom-staging.bubtaylor.com 1338`
- **Deploy**: `kubectl apply -k k8s/overlays/staging`

### Development
- **Namespace**: `pyrom-dev`
- **Telnet**: `telnet 192.168.0.20 1339` or `telnet pyrom-dev.bubtaylor.com 1339`
- **Deploy**: `kubectl apply -k k8s/overlays/dev`

## Architecture

Pyrom uses a simple architecture:
- **Deployment**: Single replica Python MUD server
- **Service**: ClusterIP service exposing port 1337
- **Ingress**: HTTP ingress (optional, for web-based access)
- **PVCs**: Three persistent volumes for player data, world data, and system files
- **ConfigMap**: Environment-specific configuration

## Prerequisites

1. **Kubernetes cluster** with kubectl configured
2. **ingress-nginx** controller installed
3. **MetalLB** for LoadBalancer services
4. **Longhorn** or another storage class for PVCs

## Deployment

### Option 1: ArgoCD (Recommended for GitOps)

See the [argocd/README.md](../argocd/README.md) for full details.

```bash
# Deploy all environments via ApplicationSet
kubectl apply -f argocd/pyrom-applicationset.yaml

# Deploy ingress-nginx TCP config
kubectl apply -f argocd/ingress-nginx-tcp-config.yaml
```

ArgoCD will automatically sync changes from the GitHub repository.

### Option 2: Manual deployment with kubectl

```bash
# Production
kubectl apply -k k8s/overlays/prod

# Staging
kubectl apply -k k8s/overlays/staging

# Development
kubectl apply -k k8s/overlays/dev

# ingress-nginx TCP config
kubectl apply -f k8s/ingress-nginx/tcp-services-configmap.yaml
```

### Check status
```bash
# List all Pyrom resources
kubectl get all,pvc,ingress -n pyrom-prod
kubectl get all,pvc,ingress -n pyrom-staging
kubectl get all,pvc,ingress -n pyrom-dev

# Check ingress-nginx service
kubectl get svc -n ingress-nginx
```

### View logs
```bash
# Pyrom server logs
kubectl logs -n pyrom-prod deployment/pyrom-deployment -f
```

## Adding New Ports to NAT

If you need to expose these ports externally, add NAT forwarding rules for:
- **1337** (Production)
- **1338** (Staging)
- **1339** (Development)

## Persistent Storage

Pyrom uses three persistent volumes:
- **pyrom-player-pvc**: Player data (1Gi)
- **pyrom-world-pvc**: World/instance data (1Gi)
- **pyrom-system-pvc**: System files (500Mi)

Data is automatically initialized from the Docker image on first deployment.

## Configuration

Environment-specific configuration is managed via ConfigMaps:
- **PYROM_PORT**: Server port (default: 1337)
- **PYROM_LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -n pyrom-prod -l app=pyrom
kubectl logs -n pyrom-prod -l app=pyrom
```

### Storage issues
```bash
kubectl get pvc -n pyrom-prod
kubectl describe pvc -n pyrom-prod pyrom-player-pvc
```

### TCP routing not working
```bash
# Check ingress-nginx TCP config
kubectl get cm -n ingress-nginx tcp-services -o yaml

# Check ingress-nginx controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Development

### Building and pushing Docker image
```bash
cd rom24
docker build -t bubthegreat/pyrom:latest .
docker push bubthegreat/pyrom:latest
```

### Testing locally with Tilt
```bash
# TODO: Add Tiltfile for local development
tilt up
```

## Notes

- Pyrom is a Python-based MUD server (ROM24 derivative)
- Default port is 1337 (configurable via ConfigMap)
- Uses UV package manager for Python dependencies
- Persistent storage ensures player data survives pod restarts

