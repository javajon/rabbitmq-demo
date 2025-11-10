# RabbitMQ Async Processing Demo

This example demonstrates asynchronous message processing using RabbitMQ in a cloud-native application. It consists of two microservices that communicate through message queues to generate API keys asynchronously.

## Architecture

```
┌─────────────────────┐         ┌─────────────────┐         ┌─────────────────────┐
│   Spring Boot App   │         │    RabbitMQ     │         │  Python Consumer    │
│   (Java Producer)   │────────▶│  Message Broker │────────▶│  (Key Generator)    │
│                     │         │                 │         │                     │
│  - Web UI           │         │  key-requests   │         │  - Listens to queue │
│  - REST API         │         │  queue          │         │  - Generates UUIDs  │
│  - Queue Publisher  │         │                 │         │  - Publishes results│
│  - Result Consumer  │◀────────│  generated-keys │◀────────│                     │
└─────────────────────┘         │  queue          │         └─────────────────────┘
                                └─────────────────┘
```

## Learning Objectives

Students will learn:

1. **Asynchronous Processing**: How to decouple services using message queues
2. **Event-Driven Architecture**: Publishing and consuming events across services
3. **Polyglot Microservices**: Java and Python services working together
4. **Message Broker Patterns**: Request/response pattern via RabbitMQ
5. **Kubernetes Deployments**: Multi-service deployment with proper networking

## Components

### 1. Spring Boot Producer (Java)
- **Location**: `key-request-producer/`
- **Technology**: Spring Boot 3.5.7, Java 21 (LTS), Gradle
- **Type**: Long-running web application (Deployment)
- **Responsibilities**:
  - Serves a web UI for requesting key generation
  - Publishes key requests to `key-requests` queue
  - Consumes generated keys from `generated-keys` queue
  - Displays results in real-time via polling
- **Container**: Built with Spring Boot's native buildpacks (no Dockerfile needed)
- **Registry**: Stored in Harbor private registry

### 2. Key Generator Consumer
- **Location**: `key-generator-consumer/`
- **Technology**: Python 3.11, Pika RabbitMQ client
- **Type**: Long-running message consumer (Deployment)
- **Responsibilities**:
  - Listens to `key-requests` queue continuously
  - Generates UUID keys with simulated processing delay
  - Publishes results to `generated-keys` queue
  - Demonstrates message acknowledgment and error handling

## Prerequisites

### For Development
- **Java Development Kit 21** (LTS - for building Spring Boot app locally)
- **Docker** (for building and running containers locally)
- **kubectl** (for deploying to Kubernetes)

### For CI/CD (Automated)
- **GitHub Account** with this repository
- **GitHub Secrets** configured (see [GITHUB-SETUP.md](GITHUB-SETUP.md))
- **Harbor Registry Access** with robot account credentials

### For Deployment
- **Kubernetes Access**: kubectl configured for homelab cluster
- **RabbitMQ**: Running in `rabbitmq` namespace (already deployed)
- **NGINX Ingress Controller**: Installed in the cluster

## CI/CD Pipeline

**GitHub Actions automatically builds and pushes images to Harbor on every commit to `main`.**

### Automated Workflows

Two GitHub Actions workflows handle image builds:

1. **Build Spring Boot Producer** (`.github/workflows/build-spring.yml`)
   - Triggers on: Push to `main`, changes in `key-request-producer/`
   - Builds with: Gradle + Spring Boot Buildpacks
   - Tags: `1.0.0-<git-sha>` and `1.0.0`
   - Pushes to: `harbor.javajon.duckdns.org/jj/key-request-producer`

2. **Build Python Consumer** (`.github/workflows/build-python.yml`)
   - Triggers on: Push to `main`, changes in `key-generator-consumer/`
   - Builds with: Docker
   - Tags: `1.0.0-<git-sha>` and `1.0.0`
   - Pushes to: `harbor.javajon.duckdns.org/jj/key-generator-consumer`

### Setup GitHub Secrets

Before using GitHub Actions, configure these secrets in your repository:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HARBOR_USERNAME` | `robot$jj+jj-deployer` | Harbor robot account |
| `HARBOR_PASSWORD` | `<your-token>` | Harbor robot token |

**See [GITHUB-SETUP.md](GITHUB-SETUP.md) for detailed setup instructions.**

## Quick Start

### 1. Development Workflow

**Build images locally** (for testing only, does NOT push to Harbor):

```bash
./build.sh
```

This builds both images locally for testing with docker-compose.

**Test locally** with Docker Compose:

```bash
docker-compose up
# Open http://localhost:8080
```

**Push to Harbor** via GitHub Actions:

```bash
# Make changes
git add .
git commit -m "Update: add new feature"
git push origin main

# GitHub Actions automatically builds and pushes to Harbor
# Check Actions tab on GitHub for build status
```

### 2. Setup Harbor Pull Secret

**IMPORTANT**: Before deploying, you must create the Harbor pull secret with your credentials.

```bash
# Create the secret from template
cp k8s/harbor-pullsecret.yaml.template k8s/harbor-pullsecret.yaml

# OPTION 1: Use kubectl to generate the secret (recommended)
kubectl create secret docker-registry harbor-pull-secret \
  --docker-server=harbor.javajon.duckdns.org \
  --docker-username='YOUR_ROBOT_USERNAME' \
  --docker-password='YOUR_HARBOR_TOKEN' \
  --namespace=rabbitmq-demo \
  --dry-run=client -o yaml > k8s/harbor-pullsecret.yaml

# OPTION 2: Manually edit harbor-pullsecret.yaml
# Replace <REPLACE_WITH_YOUR_BASE64_ENCODED_DOCKERCONFIGJSON> with your base64 credentials
```

**Get your Harbor credentials from:**
- Your instructor
- Team credentials file: `homelab/scripts/harbor-team-credentials/<team>-harbor-credentials.txt`

**Security Note**: `harbor-pullsecret.yaml` is in `.gitignore` - never commit it to git!

### 3. Deploy to Kubernetes

Use the deploy script:

```bash
# Deploy everything (namespace, pull secret, apps, ingress)
./deploy.sh
```

Or manually:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create Harbor pull secret (must be created first - see step 2)
kubectl apply -f k8s/harbor-pullsecret.yaml

# Deploy applications
kubectl apply -f k8s/spring-producer-deployment.yaml
kubectl apply -f k8s/key-generator-consumer-deployment.yaml

# Create ingress
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
kubectl get all,ingress -n rabbitmq-demo
```

Expected output (both pods should be Running):
```
NAME                                        READY   STATUS    RESTARTS   AGE
pod/key-generator-consumer-7dcc5746-xxxxx   1/1     Running   0          2m
pod/key-producer-794cfc7d8c-xxxxx           1/1     Running   0          2m

NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/key-producer   ClusterIP   10.106.140.60   <none>        80/TCP    2m

NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/key-generator-consumer   1/1     1            1           2m
deployment.apps/key-producer             1/1     1            1           2m

NAME                                             CLASS   HOSTS                               ADDRESS          PORTS   AGE
ingress.networking.k8s.io/key-producer-ingress   nginx   rabbitmq-demo.javajon.duckdns.org   192.168.50.210   80      2m
```

### 5. Access the Application

**Via Ingress (recommended):**

Open your browser to: **https://rabbitmq-demo.javajon.duckdns.org**

*Note: Requires Tailscale VPN connection*

**Via Port Forward (for testing):**

```bash
kubectl port-forward -n rabbitmq-demo svc/key-producer 8080:80
```

Then open: `http://localhost:8080`

## Usage

1. **Request a Key**: Click the "Request New Key" button in the web UI
2. **Observe Async Processing**:
   - The request is immediately sent to RabbitMQ
   - Python consumer picks it up (1-second processing delay)
   - Generated key appears in the UI automatically (2-second polling)
3. **View Results**: All generated keys are displayed with timestamps
4. **Clear Keys**: Use "Clear All Keys" to reset the display

## How It Works

### Message Flow

1. **User clicks button** → Spring Boot receives HTTP POST
2. **Spring publishes message** → `key-requests` queue in RabbitMQ
3. **Python consumer receives** → Processes request from queue
4. **Python generates UUID** → Simulates work with 1-second delay
5. **Python publishes result** → `generated-keys` queue in RabbitMQ
6. **Spring consumes result** → RabbitListener receives message
7. **UI updates** → JavaScript polls every 2 seconds and displays new keys

### Queue Configuration

Both queues are **durable** (survive broker restarts) and configured identically in both services:

- `key-requests`: Holds pending key generation requests
- `generated-keys`: Holds completed keys ready for display

### Message Format

**Key Request Message**:
```json
{
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-11-02T10:30:00"
}
```

**Generated Key Message**:
```json
{
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "key": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "generatedAt": "2025-11-02T10:30:01"
}
```

## Harbor Registry Integration

This example demonstrates modern container registry practices using Harbor.

### Spring Boot Buildpacks

The Spring Boot application uses **Cloud Native Buildpacks** instead of a Dockerfile:

- **No Dockerfile needed**: Spring Boot 3.x includes native buildpack support
- **Optimized layers**: Automatic layer caching for faster builds
- **Security**: Regularly updated base images from Paketo Buildpacks
- **Standards-compliant**: OCI-compliant images

### Build Configuration

The `build.gradle` file configures the Harbor registry:

```gradle
tasks.named('bootBuildImage') {
    imageName = "harbor.javajon.duckdns.org/jj/${project.name}:${project.version}"
    publish = false

    docker {
        publishRegistry {
            url = "https://harbor.javajon.duckdns.org"
            username = "robot\$jj+jj-deployer"
            password = "<token-from-credentials-file>"
        }
    }
}
```

### Building and Pushing

```bash
# Build and push to Harbor in one command
./gradlew bootBuildImage --publishImage

# Image will be available at:
# harbor.javajon.duckdns.org/jj/key-request-producer:1.0.0
```

### Kubernetes Pull Secret

The deployment uses a Harbor pull secret to authenticate:

```yaml
spec:
  imagePullSecrets:
  - name: harbor-pull-secret
  containers:
  - name: key-producer
    image: harbor.javajon.duckdns.org/jj/key-request-producer:1.0.0
```

**Create the secret from the template** (see "Setup Harbor Pull Secret" section above):
```bash
# Use kubectl to generate (recommended)
kubectl create secret docker-registry harbor-pull-secret \
  --docker-server=harbor.javajon.duckdns.org \
  --docker-username='YOUR_ROBOT_ACCOUNT' \
  --docker-password='YOUR_TOKEN' \
  --namespace=rabbitmq-demo \
  --dry-run=client -o yaml > k8s/harbor-pullsecret.yaml

# Then apply
kubectl apply -f k8s/harbor-pullsecret.yaml
```

**Security**: Never commit `harbor-pullsecret.yaml` to git - it contains sensitive credentials!

### Viewing Images in Harbor

1. Open https://harbor.javajon.duckdns.org
2. Login with robot account credentials
3. Navigate to project `jj`
4. View `key-request-producer` repository
5. See all tagged versions and vulnerability scans

## Development

### Run Locally with Docker Compose

```bash
# From rabbitmq/ directory
docker-compose up --build
```

This starts:
- RabbitMQ broker on port 5672 (management UI on 15672)
- Spring Boot producer on port 8080
- Python consumer

Access RabbitMQ Management UI: `http://localhost:15672` (guest/guest)

### Local Development

**Spring Boot**:
```bash
cd spring-producer
mvn spring-boot:run
```

**Python Consumer**:
```bash
cd python-consumer
pip install -r requirements.txt
python consumer.py
```

Make sure RabbitMQ is accessible at the configured host.

## Troubleshooting

### Pods not starting

```bash
# Check pod logs
kubectl logs -n rabbitmq-demo deployment/key-producer
kubectl logs -n rabbitmq-demo deployment/key-consumer

# Check RabbitMQ connectivity
kubectl exec -n rabbitmq-demo deployment/key-consumer -- ping rabbitmq.rabbitmq.svc.cluster.local
```

### Messages not flowing

```bash
# Access RabbitMQ management UI
kubectl port-forward -n rabbitmq svc/rabbitmq 15672:15672

# Open http://localhost:15672 (guest/guest)
# Check queues tab for message counts
```

### UI not updating

1. Check browser console for JavaScript errors
2. Verify `/api/keys/generated` endpoint returns data
3. Ensure polling is active (check Network tab)

### Consumer not processing

```bash
# View consumer logs
kubectl logs -n rabbitmq-demo deployment/key-consumer -f

# Should see:
# "Received key request: <request-id>"
# "Generated key <uuid> for request <request-id>"
```

## Teaching Notes

### Discussion Points

1. **Why use queues instead of direct HTTP calls?**
   - Decoupling: Services don't need to know about each other
   - Resilience: Messages persist if consumer is down
   - Scalability: Multiple consumers can process requests in parallel
   - Async processing: Long-running tasks don't block the UI

2. **What happens if the Python consumer crashes?**
   - Messages remain in the queue (durable queues)
   - Consumer restarts and processes pending messages
   - No data loss due to message persistence

3. **How would we scale this system?**
   - Increase consumer replicas: `kubectl scale deployment key-consumer --replicas=3`
   - RabbitMQ distributes messages across consumers
   - Watch the processing speed increase

4. **What about error handling?**
   - Messages are acknowledged only after successful processing
   - Failed messages can be requeued or sent to dead-letter queue
   - Python consumer uses `basic_ack` for success, `basic_nack` for failures

### Lab Exercises

1. **Scale the consumer**: Add more replicas and observe faster processing
2. **Add message validation**: Reject invalid requests with proper error handling
3. **Implement dead-letter queue**: Handle failed messages gracefully
4. **Add metrics**: Track processing time, queue depth, error rates
5. **Security enhancement**: Use RabbitMQ credentials from Kubernetes secrets

## Production Considerations

For a production deployment, consider:

- **Secrets Management**: Store RabbitMQ credentials in Kubernetes Secrets
- **Resource Limits**: Tune CPU/memory based on load testing
- **High Availability**: Run multiple RabbitMQ brokers in cluster mode
- **Monitoring**: Add Prometheus metrics for queue depth and processing time
- **Health Checks**: Verify RabbitMQ connectivity in liveness probes
- **Message TTL**: Set expiration for old unprocessed messages
- **Dead Letter Queues**: Route failed messages for manual review
- **TLS**: Encrypt RabbitMQ connections in production

## GitHub Setup

This repository uses GitHub Actions for automated CI/CD. Images are automatically built and pushed to Harbor on every commit to `main`.

### Required GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets → Actions):

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HARBOR_USERNAME` | `robot$jj+jj-deployer` | Harbor robot account |
| `HARBOR_PASSWORD` | `<your-token>` | Harbor robot token |

Get credentials from: `homelab/scripts/harbor-team-credentials/jj-harbor-credentials.txt`

### Automated Workflows

- **Spring Boot Producer**: Builds on changes to `key-request-producer/`
- **Python Consumer**: Builds on changes to `key-generator-consumer/`

Each build creates two image tags:
- `1.0.0-<git-sha>` (unique per commit)
- `1.0.0` (latest)

## References

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Spring AMQP Reference](https://docs.spring.io/spring-amqp/reference/)
- [Pika Python Client](https://pika.readthedocs.io/)
- [Kubernetes Patterns: Event-Driven Messaging](https://kubernetes.io/blog/2018/04/30/zero-downtime-deployment-kubernetes-jenkins/)

## License

Educational example for CPSC 415 Cloud-Native Software Development course.
