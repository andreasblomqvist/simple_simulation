#!/bin/bash

# Build and push Docker images to AWS ECR
# Usage: ./scripts/build-and-push.sh [AWS_REGION] [AWS_ACCOUNT_ID] [COMMIT_SHA]

set -e

# Default values
AWS_REGION=${1:-"us-east-1"}
AWS_ACCOUNT_ID=${2:-"123456789012"}
COMMIT_SHA=${3:-"latest"}

# ECR repository URLs
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
BACKEND_REPO="${ECR_REGISTRY}/simplesim-backend"
FRONTEND_REPO="${ECR_REGISTRY}/simplesim-frontend"

echo "Building and pushing SimpleSim Docker images..."
echo "Registry: ${ECR_REGISTRY}"
echo "Tag: ${COMMIT_SHA}"

# Authenticate Docker to ECR
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create ECR repositories if they don't exist
echo "Creating ECR repositories if they don't exist..."
aws ecr describe-repositories --repository-names simplesim-backend --region ${AWS_REGION} || \
  aws ecr create-repository --repository-name simplesim-backend --region ${AWS_REGION}

aws ecr describe-repositories --repository-names simplesim-frontend --region ${AWS_REGION} || \
  aws ecr create-repository --repository-name simplesim-frontend --region ${AWS_REGION}

# Build backend image
echo "Building backend Docker image..."
docker build -f Dockerfile.backend -t simplesim-backend:${COMMIT_SHA} .
docker tag simplesim-backend:${COMMIT_SHA} ${BACKEND_REPO}:${COMMIT_SHA}

# Build frontend image
echo "Building frontend Docker image..."
docker build -f Dockerfile.frontend -t simplesim-frontend:${COMMIT_SHA} .
docker tag simplesim-frontend:${COMMIT_SHA} ${FRONTEND_REPO}:${COMMIT_SHA}

# Push images to ECR
echo "Pushing backend image to ECR..."
docker push ${BACKEND_REPO}:${COMMIT_SHA}

echo "Pushing frontend image to ECR..."
docker push ${FRONTEND_REPO}:${COMMIT_SHA}

echo "Successfully built and pushed images:"
echo "  Backend: ${BACKEND_REPO}:${COMMIT_SHA}"
echo "  Frontend: ${FRONTEND_REPO}:${COMMIT_SHA}"
echo ""
echo "Update your Kubernetes manifests with these image URLs before deploying." 