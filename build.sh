#!/bin/bash
set -e

echo "Building RabbitMQ Demo Applications for Local Testing..."
echo ""
echo "NOTE: This builds images locally for testing only."
echo "      GitHub Actions automatically builds and pushes to Harbor on commit to main."
echo ""

# Build Spring Boot Producer locally
echo "Building Spring Boot Producer (local only)..."
cd key-request-producer
./gradlew bootBuildImage
echo "✓ Spring Boot producer built: harbor.javajon.duckdns.org/jj/key-request-producer:1.0.0"

# Build Key Generator Consumer locally
echo ""
echo "Building Key Generator Consumer (local only)..."
cd ../key-generator-consumer
docker build -t key-generator-consumer:latest .
echo "✓ Key generator consumer built: key-generator-consumer:latest"

cd ..

echo ""
echo "Local build complete!"
echo ""
echo "Images built (local only, NOT pushed to Harbor):"
echo "  - harbor.javajon.duckdns.org/jj/key-request-producer:1.0.0"
echo "  - key-generator-consumer:latest"
echo ""
echo "To push to Harbor:"
echo "  1. Commit and push changes to main branch"
echo "  2. GitHub Actions will automatically build and push to Harbor"
echo ""
echo "For local testing:"
echo "  - Use docker-compose: docker-compose up"
echo "  - Or deploy to K8s: ./deploy.sh (requires Harbor images)"
