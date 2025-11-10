#!/bin/bash
set -e

echo "Deploying RabbitMQ Demo to Kubernetes..."

# Create namespace
echo ""
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Create Harbor pull secret
echo ""
echo "Creating Harbor pull secret..."
kubectl apply -f k8s/harbor-pullsecret.yaml

# Deploy applications
echo ""
echo "Deploying Spring Boot producer..."
kubectl apply -f k8s/spring-producer-deployment.yaml

echo ""
echo "Deploying Key Generator Consumer..."
kubectl apply -f k8s/key-generator-consumer-deployment.yaml

echo ""
echo "Creating ingress..."
kubectl apply -f k8s/ingress.yaml

echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=120s \
  deployment/key-producer deployment/key-generator-consumer -n rabbitmq-demo

echo ""
echo "Deployment complete!"
echo ""
echo "Check status:"
echo "  kubectl get all -n rabbitmq-demo"
echo ""
echo "Access application:"
echo "  kubectl port-forward -n rabbitmq-demo svc/key-producer 8080:80"
echo "  Then open: http://localhost:8080"
echo ""
echo "View logs:"
echo "  kubectl logs -n rabbitmq-demo deployment/key-producer -f"
echo "  kubectl logs -n rabbitmq-demo deployment/key-generator-consumer -f"
