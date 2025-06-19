# SimpleSim Deployment Quick Start

This guide provides quick setup instructions for deploying SimpleSim in different environments.

## Prerequisites

### For Local Development
- Docker and Docker Compose
- curl (for health checks)

### For Production (AWS)
- AWS CLI configured with appropriate permissions
- kubectl
- eksctl
- helm

## Quick Start Options

### 1. Local Development (Docker Compose)

```bash
# Clone the repository
git clone <your-repo-url>
cd simple_simulation

# Run the setup script
./scripts/setup-local.sh
```

This will:
- Build Docker images
- Start frontend (port 3000) and backend (port 8000)
- Perform health checks
- Display access URLs

### 2. Production Deployment (AWS EKS)

```bash
# Set your AWS account ID
export AWS_ACCOUNT_ID=123456789012

# Run the production setup
./scripts/setup-production.sh simplesim-cluster us-east-1 $AWS_ACCOUNT_ID
```

This will:
- Create EKS cluster
- Install AWS Load Balancer Controller
- Build and push Docker images to ECR
- Deploy to Kubernetes

## Manual Steps

### Local Development

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build and push images
./scripts/build-and-push.sh us-east-1 123456789012 latest

# Deploy to Kubernetes
./scripts/deploy-k8s.sh

# Check status
kubectl get all -n simplesim
```

## Configuration

### Environment Variables

Create a `.env` file for local development:

```env
PYTHONPATH=/app
LOG_LEVEL=INFO
REACT_APP_API_URL=http://localhost:8000
```

### Kubernetes Configuration

Update the following files before deployment:

1. **k8s/ingress.yaml**: Set your domain and SSL certificate ARN
2. **k8s/backend-deployment.yaml**: Update image URL with your ECR repository
3. **k8s/frontend-deployment.yaml**: Update image URL with your ECR repository

## Access URLs

### Local Development
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production
- Frontend: https://your-domain.com
- Backend API: https://your-domain.com/api

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Docker build failures**: Check Dockerfile syntax and dependencies
3. **Kubernetes deployment issues**: Check logs with `kubectl logs -n simplesim`
4. **Ingress not working**: Verify AWS Load Balancer Controller is installed

### Debug Commands

```bash
# Check Docker containers
docker-compose ps

# View container logs
docker-compose logs backend
docker-compose logs frontend

# Check Kubernetes resources
kubectl get all -n simplesim

# Check ingress status
kubectl get ingress -n simplesim

# View pod logs
kubectl logs -f deployment/simplesim-backend -n simplesim
kubectl logs -f deployment/simplesim-frontend -n simplesim
```

## Security Considerations

1. **Use specific image tags** instead of `latest` in production
2. **Enable Pod Security Standards** in your namespace
3. **Configure Network Policies** to restrict pod-to-pod communication
4. **Use secrets** for sensitive configuration data
5. **Regularly update base images** for security patches

## Scaling

The application includes Horizontal Pod Autoscalers (HPA):
- Backend: 2-10 replicas based on CPU usage
- Frontend: 2-5 replicas based on CPU usage

## Monitoring

```bash
# Check resource usage
kubectl top pods -n simplesim

# Check HPA status
kubectl get hpa -n simplesim

# View events
kubectl get events -n simplesim --sort-by='.lastTimestamp'
```

## Cleanup

### Local Development
```bash
docker-compose down
```

### Production
```bash
# Delete the application
kubectl delete namespace simplesim

# Delete EKS cluster (if no longer needed)
eksctl delete cluster --name simplesim-cluster --region us-east-1
```

## Support

For issues and questions:
1. Check the logs using the debug commands above
2. Review the full DEPLOYMENT.md for detailed information
3. Check the application logs for specific error messages 