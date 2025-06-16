#!/bin/bash

# Build and push Docker images to AWS ECR
# Usage: ./scripts/build-and-push.sh [AWS_REGION] [AWS_ACCOUNT_ID] [IMAGE_TAG]

set -e

# Default values
AWS_REGION=${1:-"us-east-1"}
AWS_ACCOUNT_ID=${2:-"123456789012"}
IMAGE_TAG=${3:-"latest"}

# ECR repository URLs
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
BACKEND_REPO="${ECR_REGISTRY}/simplesim-backend"
FRONTEND_REPO="${ECR_REGISTRY}/simplesim-frontend"

echo "Building and pushing SimpleSim Docker images..."
echo "Registry: ${ECR_REGISTRY}"
echo "Tag: ${IMAGE_TAG}"

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
docker build -f Dockerfile.backend -t simplesim-backend:${IMAGE_TAG} .
docker tag simplesim-backend:${IMAGE_TAG} ${BACKEND_REPO}:${IMAGE_TAG}

# Build frontend image
echo "Building frontend Docker image..."
docker build -f Dockerfile.frontend -t simplesim-frontend:${IMAGE_TAG} .
docker tag simplesim-frontend:${IMAGE_TAG} ${FRONTEND_REPO}:${IMAGE_TAG}

# Push images to ECR
echo "Pushing backend image to ECR..."
docker push ${BACKEND_REPO}:${IMAGE_TAG}

echo "Pushing frontend image to ECR..."
docker push ${FRONTEND_REPO}:${IMAGE_TAG}

echo "Successfully built and pushed images:"
echo "  Backend: ${BACKEND_REPO}:${IMAGE_TAG}"
echo "  Frontend: ${FRONTEND_REPO}:${IMAGE_TAG}"
echo ""
echo "Update your Kubernetes manifests with these image URLs before deploying." 