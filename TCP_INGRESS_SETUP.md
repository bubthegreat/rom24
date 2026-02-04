# TCP Ingress Setup for Pyrom

## Problem

Pyrom uses **telnet (TCP protocol)**, not HTTP. The standard HTTP Ingress won't work for telnet connections. We need to configure ingress-nginx to route TCP traffic.

## Solution

### 1. Apply the TCP Services ConfigMap (Managed by ArgoCD)

The ConfigMap tells ingress-nginx which TCP ports to route to which services. This is **automatically managed by ArgoCD** via the `pyrom-app-of-apps`.

Verify it's applied:

```bash
kubectl get configmap tcp-services -n ingress-nginx -o yaml
```

You should see:

```yaml
data:
  "1337": "pyrom-prod/pyrom-service:1337"
  "1338": "pyrom-staging/pyrom-service:1337"
  "1339": "pyrom-dev/pyrom-service:1337"
```

### 2. Configure ingress-nginx Controller to Expose TCP Ports (One-Time Setup)

The ingress-nginx controller Service needs to expose these TCP ports. This is a **one-time manual step** because the Service is managed by Helm, not ArgoCD.

**Important**: The actual Service name in your cluster is `ingressnginx-ingress-nginx-controller`, not `ingress-nginx-controller`.

```bash
kubectl patch service ingressnginx-ingress-nginx-controller -n ingress-nginx --type='json' -p='[
  {"op": "add", "path": "/spec/ports/-", "value": {"name": "pyrom-prod", "port": 1337, "protocol": "TCP", "targetPort": 1337}},
  {"op": "add", "path": "/spec/ports/-", "value": {"name": "pyrom-staging", "port": 1338, "protocol": "TCP", "targetPort": 1338}},
  {"op": "add", "path": "/spec/ports/-", "value": {"name": "pyrom-dev", "port": 1339, "protocol": "TCP", "targetPort": 1339}}
]'
```

**Note**: This patch persists across ingress-nginx controller restarts, but may be lost if you upgrade or reinstall ingress-nginx via Helm. If that happens, just re-run the patch command above.

### 3. Verify the Setup

Check that the ingress-nginx controller Service has the TCP ports:

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx -o yaml | grep -A 5 "1337\|1338\|1339"
```

You should see ports 1337, 1338, and 1339 listed.

### 4. Test the Connection

```bash
# Production
telnet pyrom.bubtaylor.com 1337

# Staging
telnet pyrom-staging.bubtaylor.com 1338

# Dev
telnet pyrom-dev.bubtaylor.com 1339
```

## Important Notes

1. **The HTTP Ingress resource** (`pyrom-ingress.yaml`) is **NOT used for telnet connections**. It's only there if you want to serve HTTP content on port 80.

2. **TCP routing is configured via**:
   - ConfigMap: `tcp-services` in `ingress-nginx` namespace
   - Service: `ingress-nginx-controller` must expose the TCP ports

3. **DNS must point to the ingress-nginx controller's external IP** for the hostnames to work.

## Troubleshooting

### Check if ConfigMap is applied

```bash
kubectl describe configmap tcp-services -n ingress-nginx
```

### Check if ingress-nginx controller is using the ConfigMap

```bash
kubectl get deployment ingress-nginx-controller -n ingress-nginx -o yaml | grep tcp-services
```

You should see a reference to the `tcp-services` ConfigMap.

### Check ingress-nginx controller logs

```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller | grep -i tcp
```

### Check if ports are exposed on the Service

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

Look for ports 1337, 1338, 1339 in the PORT(S) column.

