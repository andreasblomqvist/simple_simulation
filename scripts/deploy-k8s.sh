#!/bin/bash

# Deploy SimpleSim to Kubernetes
# Usage: ./scripts/deploy-k8s.sh [NAMESPACE]

set -e

NAMESPACE=${1:-"simplesim"}

echo "Deploying SimpleSim to Kubernetes..."
echo "Namespace: ${NAMESPACE}"

# Apply namespace first
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply ConfigMap
echo "Applying ConfigMap..."
kubectl apply -f k8s/configmap.yaml

# Apply backend resources
echo "Deploying backend..."
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# Apply frontend resources
echo "Deploying frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Apply ingress
echo "Applying ingress..."
kubectl apply -f k8s/ingress.yaml

# Apply HPA
echo "Applying Horizontal Pod Autoscalers..."
kubectl apply -f k8s/hpa.yaml

# Wait for deployments to be ready
echo "Waiting for backend deployment to be ready..."
kubectl rollout status deployment/simplesim-backend -n ${NAMESPACE} --timeout=300s

echo "Waiting for frontend deployment to be ready..."
kubectl rollout status deployment/simplesim-frontend -n ${NAMESPACE} --timeout=300s

echo "Deployment complete!"
echo ""
echo "Check the status with:"
echo "  kubectl get all -n ${NAMESPACE}"
echo ""
echo "Get the ingress URL with:"
echo "  kubectl get ingress -n ${NAMESPACE}" 