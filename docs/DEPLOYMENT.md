# SimpleSim Deployment Guide

This guide covers deploying SimpleSim using Docker containers and Kubernetes on AWS.

## Prerequisites

- Docker and Docker Compose installed
- AWS CLI configured with appropriate permissions
- kubectl configured to connect to your EKS cluster
- AWS Load Balancer Controller installed on your EKS cluster

## Project Structure

```
SimpleSim/
├── Dockerfile.backend          # Backend container definition
├── Dockerfile.frontend         # Frontend container definition
├── nginx.conf                  # Nginx configuration for frontend
├── docker-compose.yml          # Local development setup
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
└── scripts/
    ├── build-and-push.sh       # Build and push to ECR
    └── deploy-k8s.sh          # Deploy to Kubernetes
```

## Docker Development Setup

### 1. Local Development with Docker Compose

```bash
# Build and run locally
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### 2. Build Individual Images

```bash
# Build backend
docker build -f Dockerfile.backend -t simplesim-backend:latest .

# Build frontend
docker build -f Dockerfile.frontend -t simplesim-frontend:latest .
```

## AWS Deployment Setup

### 1. Prerequisites Setup

#### Create EKS Cluster
```bash
# Using eksctl (recommended)
eksctl create cluster --name simplesim-cluster --region us-east-1 --nodes 3

# Or using AWS CLI/Console
# Follow AWS EKS documentation for manual setup
```

#### Install AWS Load Balancer Controller
```bash
# Create IAM policy
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

# Create service account
eksctl create iamserviceaccount \
  --cluster=simplesim-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name "AmazonEKSLoadBalancerControllerRole" \
  --attach-policy-arn=arn:aws:iam::ACCOUNT:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# Install controller using Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=simplesim-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

### 2. Build and Push Images to ECR

```bash
# Set your AWS account ID and region
export AWS_ACCOUNT_ID=123456789012
export AWS_REGION=us-east-1

# Run the build script
./scripts/build-and-push.sh $AWS_REGION $AWS_ACCOUNT_ID latest
```

### 3. Update Kubernetes Manifests

Update the image URLs in the deployment files:

```yaml
# In k8s/backend-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: backend
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/simplesim-backend:latest

# In k8s/frontend-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/simplesim-frontend:latest
```

### 4. Configure Ingress

Update `k8s/ingress.yaml` with your domain and SSL certificate:

```yaml
metadata:
  annotations:
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:ACCOUNT:certificate/CERTIFICATE_ID
spec:
  rules:
  - host: simplesim.yourdomain.com
```

### 5. Deploy to Kubernetes

```bash
# Deploy the application
./scripts/deploy-k8s.sh

# Check deployment status
kubectl get all -n simplesim

# Get ingress URL
kubectl get ingress -n simplesim
```

## Configuration

### Environment Variables

Configure the following in `k8s/configmap.yaml`:

- `PYTHONPATH`: Python path for backend
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `REACT_APP_API_URL`: API URL for frontend

### Secrets

For sensitive data, create Kubernetes secrets:

```bash
# Create ECR pull secret
kubectl create secret docker-registry aws-ecr-secret \
  --docker-server=ACCOUNT.dkr.ecr.REGION.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region REGION) \
  -n simplesim
```

## Scaling and Monitoring

### Horizontal Pod Autoscaling

The HPA configuration automatically scales pods based on CPU and memory usage:
- Backend: 2-10 replicas
- Frontend: 2-5 replicas

### Monitoring

```bash
# Check pod status
kubectl get pods -n simplesim

# View logs
kubectl logs -f deployment/simplesim-backend -n simplesim
kubectl logs -f deployment/simplesim-frontend -n simplesim

# Check HPA status
kubectl get hpa -n simplesim

# Check resource usage
kubectl top pods -n simplesim
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Ensure ECR authentication is configured
   - Check image URLs in deployment manifests
   - Verify aws-ecr-secret exists

2. **Backend Health Check Failures**
   - Check if the `/health` endpoint is accessible
   - Verify PYTHONPATH environment variable
   - Check application logs for startup errors

3. **Frontend Not Loading**
   - Verify nginx configuration
   - Check if frontend can reach backend service
   - Ensure ingress is configured correctly

4. **Ingress Not Working**
   - Verify AWS Load Balancer Controller is installed
   - Check ingress annotations
   - Ensure SSL certificate ARN is correct

### Debugging Commands

```bash
# Describe resources for detailed information
kubectl describe deployment simplesim-backend -n simplesim
kubectl describe pod <pod-name> -n simplesim

# Check events
kubectl get events -n simplesim --sort-by='.lastTimestamp'

# Port forward for local testing
kubectl port-forward svc/simplesim-backend 8000:8000 -n simplesim
kubectl port-forward svc/simplesim-frontend 3000:3000 -n simplesim
```

## Security Considerations

1. **Use specific image tags** instead of `latest` in production
2. **Enable Pod Security Standards** in your namespace
3. **Configure Network Policies** to restrict pod-to-pod communication
4. **Use secrets** for sensitive configuration data
5. **Regularly update base images** for security patches
6. **Configure resource limits** to prevent resource exhaustion

## Updating the Application

```bash
# Build new images with version tag
./scripts/build-and-push.sh us-east-1 123456789012 v1.1.0

# Update deployment manifests with new image tag
# Then apply changes
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Monitor rollout
kubectl rollout status deployment/simplesim-backend -n simplesim
kubectl rollout status deployment/simplesim-frontend -n simplesim
```

## Cleanup

```bash
# Delete the application
kubectl delete namespace simplesim

# Delete ECR repositories (optional)
aws ecr delete-repository --repository-name simplesim-backend --force --region us-east-1
aws ecr delete-repository --repository-name simplesim-frontend --force --region us-east-1

# Delete EKS cluster (if no longer needed)
eksctl delete cluster --name simplesim-cluster --region us-east-1
``` 