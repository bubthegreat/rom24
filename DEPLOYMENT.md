# Pyrom Deployment Setup

This document describes the complete deployment setup for Pyrom (ROM24 Python MUD) with dev/staging/prod environments, similar to the KBK deployment.

## Overview

Pyrom now has a complete Kubernetes deployment setup with:
- **Docker containerization** using Python 3.12 and UV package manager
- **Three environments**: dev, staging, and prod
- **Persistent storage** for player data, world data, and system files
- **ArgoCD GitOps** integration for automated deployments
- **TCP ingress** routing for telnet access

## File Structure

```
rom24/
├── Dockerfile                          # Docker image definition
├── .dockerignore                       # Docker build exclusions
├── Makefile                            # Build and deployment commands
├── k8s/
│   ├── README.md                       # Kubernetes deployment documentation
│   ├── base/                           # Base Kubernetes manifests
│   │   ├── kustomization.yaml
│   │   ├── pyrom-deployment.yaml      # Main deployment
│   │   ├── pyrom-service.yaml         # ClusterIP service
│   │   ├── pyrom-ingress.yaml         # HTTP ingress
│   │   ├── pyrom-pvc.yaml             # Persistent volume claims
│   │   └── pyrom-configmap.yaml       # Configuration
│   ├── overlays/
│   │   ├── dev/                        # Development environment
│   │   │   ├── namespace.yaml
│   │   │   ├── kustomization.yaml
│   │   │   ├── ingress-patch.yaml
│   │   │   └── pyrom-configmap.yaml
│   │   ├── staging/                    # Staging environment
│   │   │   ├── namespace.yaml
│   │   │   ├── kustomization.yaml
│   │   │   ├── ingress-patch.yaml
│   │   │   └── pyrom-configmap.yaml
│   │   └── prod/                       # Production environment
│   │       ├── namespace.yaml
│   │       ├── kustomization.yaml
│   │       └── pyrom-configmap.yaml
│   └── ingress-nginx/
│       └── tcp-services-configmap.yaml # TCP port routing
└── argocd/
    ├── pyrom-applicationset.yaml       # ArgoCD ApplicationSet
    └── ingress-nginx-tcp-config.yaml   # ArgoCD TCP config app
```

## Environments

| Environment | Namespace      | Telnet Port | Hostname                      | Log Level |
|-------------|----------------|-------------|-------------------------------|-----------|
| Production  | pyrom-prod     | 1337        | pyrom.bubtaylor.com           | WARNING   |
| Staging     | pyrom-staging  | 1338        | pyrom-staging.bubtaylor.com   | INFO      |
| Development | pyrom-dev      | 1339        | pyrom-dev.bubtaylor.com       | DEBUG     |

## Quick Start

### 1. Build and Push Docker Image

```bash
cd rom24
make build
make push
```

### 2. Deploy with ArgoCD (Recommended)

```bash
# Deploy all environments
kubectl apply -f argocd/pyrom-applicationset.yaml

# Deploy TCP routing config
kubectl apply -f argocd/ingress-nginx-tcp-config.yaml
```

### 3. Deploy Manually (Alternative)

```bash
# Deploy production
make deploy

# Deploy staging
make deploy-staging

# Deploy development
make deploy-dev
```

## Persistent Storage

Each environment has three persistent volumes:

1. **pyrom-player-pvc** (1Gi): Player character data
2. **pyrom-world-pvc** (1Gi): World instances and area data
3. **pyrom-system-pvc** (500Mi): System files and logs

Data is automatically initialized from the Docker image on first deployment via init containers.

## Configuration

Environment-specific settings are managed via ConfigMaps:

- **PYROM_PORT**: Server port (default: 1337)
- **PYROM_LOG_LEVEL**: Logging verbosity
  - Production: WARNING (minimal logging)
  - Staging: INFO (standard logging)
  - Development: DEBUG (verbose logging)

## Accessing the MUD

### Telnet Access

```bash
# Production
telnet 192.168.0.20 1337
# or
telnet pyrom.bubtaylor.com 1337

# Staging
telnet 192.168.0.20 1338
# or
telnet pyrom-staging.bubtaylor.com 1338

# Development
telnet 192.168.0.20 1339
# or
telnet pyrom-dev.bubtaylor.com 1339
```

## Monitoring

### Check Deployment Status

```bash
# Production
kubectl get all,pvc,ingress -n pyrom-prod

# Staging
kubectl get all,pvc,ingress -n pyrom-staging

# Development
kubectl get all,pvc,ingress -n pyrom-dev
```

### View Logs

```bash
# Production logs
kubectl logs -n pyrom-prod deployment/pyrom-deployment -f

# Staging logs
kubectl logs -n pyrom-staging deployment/pyrom-deployment -f

# Development logs
kubectl logs -n pyrom-dev deployment/pyrom-deployment -f
```

## Comparison with KBK

| Feature              | KBK                    | Pyrom                  |
|----------------------|------------------------|------------------------|
| Language             | C                      | Python 3.12            |
| Package Manager      | make/gcc               | UV                     |
| Default Port         | 8989                   | 1337                   |
| Prod Port            | 8989                   | 1337                   |
| Staging Port         | 8988                   | 1338                   |
| Dev Port             | 8987                   | 1339                   |
| Storage Volumes      | 3 (player/sys/data)    | 3 (player/world/system)|
| Health Check         | TCP + HTTP             | TCP                    |
| Special Features     | GDB debugging          | Python hot-reload      |

## Next Steps

1. **Set up CI/CD**: Create GitHub Actions workflow for automated builds
2. **Add monitoring**: Integrate Prometheus metrics
3. **Configure backups**: Set up automated PVC backups
4. **DNS configuration**: Add DNS entries for hostnames
5. **NAT forwarding**: Configure router to forward ports 1337-1339

## Troubleshooting

See [k8s/README.md](k8s/README.md) for detailed troubleshooting steps.

## Notes

- Pyrom uses the same GitOps approach as KBK
- All configuration is version-controlled
- ArgoCD automatically syncs changes from the repository
- Persistent storage ensures data survives pod restarts and redeployments

