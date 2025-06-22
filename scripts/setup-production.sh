#!/bin/bash

# Setup SimpleSim for production deployment on AWS
# Usage: ./scripts/setup-production.sh [CLUSTER_NAME] [AWS_REGION] [AWS_ACCOUNT_ID]

set -e

# Default values
CLUSTER_NAME=${1:-"simplesim-cluster"}
AWS_REGION=${2:-"us-east-1"}
AWS_ACCOUNT_ID=${3:-""}

if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_ACCOUNT_ID is required"
    echo "Usage: ./scripts/setup-production.sh [CLUSTER_NAME] [AWS_REGION] [AWS_ACCOUNT_ID]"
    exit 1
fi

echo "Setting up SimpleSim for production deployment..."
echo "Cluster Name: ${CLUSTER_NAME}"
echo "AWS Region: ${AWS_REGION}"
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"

# Check prerequisites
echo "Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if eksctl is installed
if ! command -v eksctl &> /dev/null; then
    echo "Error: eksctl is not installed. Please install eksctl first."
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo "Error: helm is not installed. Please install helm first."
    exit 1
fi

echo "All prerequisites are installed."

# Create EKS cluster
echo "Creating EKS cluster..."
eksctl create cluster \
    --name ${CLUSTER_NAME} \
    --region ${AWS_REGION} \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3 \
    --nodes-min 1 \
    --nodes-max 5 \
    --managed

# Update kubeconfig
echo "Updating kubeconfig..."
aws eks update-kubeconfig --name ${CLUSTER_NAME} --region ${AWS_REGION}

# Install AWS Load Balancer Controller
echo "Installing AWS Load Balancer Controller..."

# Create IAM policy
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json \
    --region ${AWS_REGION} || echo "Policy already exists"

# Create service account
eksctl create iamserviceaccount \
    --cluster=${CLUSTER_NAME} \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --role-name "AmazonEKSLoadBalancerControllerRole" \
    --attach-policy-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
    --approve \
    --region ${AWS_REGION}

# Install controller using Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=${CLUSTER_NAME} \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller

# Update Kubernetes manifests with correct image URLs
echo "Updating Kubernetes manifests..."

# Update backend deployment
sed -i.bak "s|123456789012.dkr.ecr.us-east-1.amazonaws.com/simplesim-backend:latest|${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/simplesim-backend:latest|g" k8s/backend-deployment.yaml

# Update frontend deployment
sed -i.bak "s|123456789012.dkr.ecr.us-east-1.amazonaws.com/simplesim-frontend:latest|${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/simplesim-frontend:latest|g" k8s/frontend-deployment.yaml

# Update ingress with correct certificate ARN (placeholder)
echo "Note: Please update the certificate ARN in k8s/ingress.yaml with your actual SSL certificate ARN"

# Build and push Docker images
echo "Building and pushing Docker images..."
./scripts/build-and-push.sh ${AWS_REGION} ${AWS_ACCOUNT_ID} latest

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
./scripts/deploy-k8s.sh

# Clean up temporary files
rm -f iam_policy.json
rm -f k8s/*.bak

echo ""
echo "Production setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the certificate ARN in k8s/ingress.yaml"
echo "2. Update the hostname in k8s/ingress.yaml"
echo "3. Apply the updated ingress: kubectl apply -f k8s/ingress.yaml"
echo ""
echo "Check deployment status:"
echo "  kubectl get all -n simplesim"
echo ""
echo "Get the ingress URL:"
echo "  kubectl get ingress -n simplesim" 