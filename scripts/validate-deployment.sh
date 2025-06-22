#!/bin/bash

# Validate SimpleSim deployment configuration
# Usage: ./scripts/validate-deployment.sh

set -e

echo "Validating SimpleSim deployment configuration..."

# Check if required files exist
echo "Checking required files..."

REQUIRED_FILES=(
    "Dockerfile.backend"
    "Dockerfile.frontend"
    "docker-compose.yml"
    "nginx.conf"
    "requirements.txt"
    "frontend/package.json"
    "k8s/namespace.yaml"
    "k8s/configmap.yaml"
    "k8s/backend-deployment.yaml"
    "k8s/backend-service.yaml"
    "k8s/frontend-deployment.yaml"
    "k8s/frontend-service.yaml"
    "k8s/ingress.yaml"
    "k8s/hpa.yaml"
    "scripts/build-and-push.sh"
    "scripts/deploy-k8s.sh"
    "scripts/setup-local.sh"
    "scripts/setup-production.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ Missing: $file"
        exit 1
    fi
done

# Validate Docker Compose syntax
echo ""
echo "Validating Docker Compose syntax..."
if command -v docker-compose &> /dev/null; then
    docker-compose config > /dev/null
    echo "✓ docker-compose.yml is valid"
else
    echo "⚠ docker-compose not installed, skipping validation"
fi

# Validate Kubernetes manifests
echo ""
echo "Validating Kubernetes manifests..."

if command -v kubectl &> /dev/null; then
    for file in k8s/*.yaml; do
        if kubectl apply --dry-run=client -f "$file" &> /dev/null; then
            echo "✓ $(basename "$file")"
        else
            echo "✗ Invalid: $(basename "$file")"
            exit 1
        fi
    done
else
    echo "⚠ kubectl not installed, skipping Kubernetes validation"
fi

# Check script permissions
echo ""
echo "Checking script permissions..."
for script in scripts/*.sh; do
    if [ -x "$script" ]; then
        echo "✓ $(basename "$script") is executable"
    else
        echo "✗ $(basename "$script") is not executable"
        chmod +x "$script"
        echo "  → Made $(basename "$script") executable"
    fi
done

# Validate backend requirements
echo ""
echo "Validating backend requirements..."
if [ -f "requirements.txt" ]; then
    echo "✓ requirements.txt exists"
    echo "  Dependencies:"
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
            echo "    - $line"
        fi
    done < requirements.txt
else
    echo "✗ requirements.txt missing"
fi

# Validate frontend package.json
echo ""
echo "Validating frontend package.json..."
if [ -f "frontend/package.json" ]; then
    echo "✓ frontend/package.json exists"
    if command -v jq &> /dev/null; then
        VERSION=$(jq -r '.version' frontend/package.json)
        echo "  Version: $VERSION"
    fi
else
    echo "✗ frontend/package.json missing"
fi

# Check for common issues
echo ""
echo "Checking for common issues..."

# Check if ingress has placeholder values
if grep -q "yourdomain.com" k8s/ingress.yaml; then
    echo "⚠ k8s/ingress.yaml contains placeholder domain"
fi

if grep -q "CERTIFICATE_ID" k8s/ingress.yaml; then
    echo "⚠ k8s/ingress.yaml contains placeholder certificate ARN"
fi

if grep -q "123456789012" k8s/backend-deployment.yaml; then
    echo "⚠ k8s/backend-deployment.yaml contains placeholder AWS account ID"
fi

if grep -q "123456789012" k8s/frontend-deployment.yaml; then
    echo "⚠ k8s/frontend-deployment.yaml contains placeholder AWS account ID"
fi

# Check Dockerfile syntax
echo ""
echo "Validating Dockerfile syntax..."

# Check backend Dockerfile
if [ -f "Dockerfile.backend" ]; then
    echo "✓ Dockerfile.backend exists"
    if grep -q "EXPOSE 8000" Dockerfile.backend; then
        echo "  ✓ Exposes correct port (8000)"
    else
        echo "  ✗ Missing or incorrect EXPOSE directive"
    fi
fi

# Check frontend Dockerfile
if [ -f "Dockerfile.frontend" ]; then
    echo "✓ Dockerfile.frontend exists"
    if grep -q "EXPOSE 3000" Dockerfile.frontend; then
        echo "  ✓ Exposes correct port (3000)"
    else
        echo "  ✗ Missing or incorrect EXPOSE directive"
    fi
fi

echo ""
echo "Validation complete!"
echo ""
echo "Next steps:"
echo "1. For local development: ./scripts/setup-local.sh"
echo "2. For production: ./scripts/setup-production.sh <cluster-name> <region> <aws-account-id>"
echo ""
echo "Remember to update placeholder values in:"
echo "- k8s/ingress.yaml (domain and certificate ARN)"
echo "- k8s/backend-deployment.yaml (ECR image URL)"
echo "- k8s/frontend-deployment.yaml (ECR image URL)" 