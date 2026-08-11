#!/bin/bash

echo "=== ArgoCD Applications Status ==="
echo ""

# Switch to a different context to avoid Tilt interference
export KUBECONFIG=~/.kube/config

echo "Checking pyrom applications..."
kubectl get applications -n argocd --context homelab-k3s 2>/dev/null | grep pyrom || echo "No pyrom apps found"

echo ""
echo "Checking ApplicationSets..."
kubectl get applicationsets -n argocd --context homelab-k3s 2>/dev/null | grep pyrom || echo "No pyrom applicationsets found"

echo ""
echo "=== App of Apps Status ==="
kubectl get application pyrom-app-of-apps -n argocd --context homelab-k3s -o jsonpath='{.status.sync.status}' 2>/dev/null && echo "" || echo "App of Apps not found or not synced yet"

echo ""
echo "=== TCP ConfigMap Status ==="
kubectl get configmap tcp-services -n ingress-nginx --context homelab-k3s -o jsonpath='{.data}' 2>/dev/null && echo "" || echo "TCP ConfigMap not found"

