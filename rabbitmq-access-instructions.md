# Accessing and Validating RabbitMQ from Your Local Development Environment

> **Prerequisites**: You need `kubectl` configured with access to a Kubernetes cluster with Rabbitmq running.

## Option 1: Using kubectl port-forward (Recommended)

This is the easiest and most secure method to access RabbitMQ.

### Step 1: Set up port forwarding

Forward RabbitMQ management port to your laptop:

```bash
kubectl get services -n rabbitmq
kubectl port-forward -n rabbitmq svc/rabbitmq 15672:15672 5672:5672
```

The command will output:

```bash
Forwarding from 127.0.0.1:15672 -> 15672
Forwarding from [::1]:15672 -> 15672
Forwarding from 127.0.0.1:5672 -> 5672
Forwarding from [::1]:5672 -> 5672
Handling connection for 15672
Handling connection for 15672
```

Now you can:
- Access UI at: `http://localhost:15672`
- Connect AMQP clients to: `localhost:5672`

### Step 2: Access the UI

Open your browser and navigate to:
```
http://localhost:15672
```

### Step 3: Login

- **Username**: `admin`
- **Password**: `admin`

### Keep the port-forward running

The port-forward command needs to stay running. Open a new terminal for other work.

To stop port forwarding, press `Ctrl+C` in the terminal.

## Troubleshooting

### Port already in use

If you get "bind: address already in use" error:

Find what's using port 15672:
```bash
lsof -i :15672  # On macOS/Linux
netstat -ano | findstr :15672  # On Windows
```

Use a different local port:
```bash
kubectl port-forward -n rabbitmq svc/rabbitmq 8080:15672 5672:5672
```

Then access at `http://localhost:8080`

### Connection refused

If the port-forward succeeds but browser shows connection refused:

Check if RabbitMQ pod is running:
```bash
kubectl get pods -n rabbitmq
```

Check if management plugin is enabled:
```bash
kubectl exec -it rabbitmq-0 -n rabbitmq -- rabbitmq-plugins list | grep management
```

### Lost connection

If port-forward disconnects, run with automatic reconnection:

```bash
while true; do
    kubectl port-forward -n rabbitmq svc/rabbitmq 15672:15672 5672:5672
    sleep 1
done
```

## Quick Access Script

Create a script for easy access:

```bash
#!/bin/bash
# save as: rabbitmq-admin.sh

echo "Starting RabbitMQ admin port-forward..."
echo "Access UI at: http://localhost:15672"
echo "Connect AMQP clients to: localhost:5672"
echo "Username: admin"
echo "Password: admin"
echo "Press Ctrl+C to stop"
echo ""

kubectl port-forward -n rabbitmq svc/rabbitmq 15672:15672 5672:5672
```

Make it executable:
```bash
chmod +x rabbitmq-admin.sh
./rabbitmq-admin.sh
```

## What You'll See in the Admin Interface

1. **Overview**: Cluster status, message rates, and node health
2. **Connections**: Active client connections and their details
3. **Channels**: Open channels per connection
4. **Exchanges**: Message routing rules
5. **Queues**: Queue list, messages, and consumers
6. **Admin**: User management and permissions
7. **Cluster**: Node status and clustering information

## Useful Admin Tasks

### Monitor Queue Depth

1. Click on "Queues" tab
2. See message count in "Ready" and "Unacked" columns
3. Click queue name for detailed metrics

### Check Connection Health

1. Click on "Connections" tab
2. Look for high channel counts or idle connections
3. Force close problematic connections if needed

### Create a Test Queue

1. Go to "Queues" tab
2. Click "Add a new queue"
3. Enter name: `test-queue`
4. Click "Add queue"
5. Test by publishing a message directly from UI

### View Message Rates

1. Stay on "Overview" tab
2. Watch real-time graphs for:
   - Publish rate
   - Deliver rate
   - Acknowledge rate

---

# RabbitMQ Quick Start - Testing from Your Laptop

Now that you have port-forwarding set up, you can test RabbitMQ directly from your laptop without deploying to Kubernetes.

## Connection Configuration

> **Note**: All examples use environment variables for configuration. This allows the same code to work in both local development (with port-forward) and Kubernetes deployments.

**Environment Variables:**

For local development with port-forward:
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=admin
export RABBITMQ_PASS=admin
```

For Kubernetes deployments (set in pod manifests):
```bash
export RABBITMQ_HOST=rabbitmq.rabbitmq.svc.cluster.local
export RABBITMQ_USER=admin
export RABBITMQ_PASS=admin
```

**Authentication**: All connections require credentials. RabbitMQ restricts the default `guest` user to localhost connections only.

```python
import os
import pika

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

# All examples use this connection pattern:
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
```

## Prerequisites

### 1. Set Up Port Forwarding and Environment Variables

Open a terminal and run these commands:

Set environment variables for local development:
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=admin
export RABBITMQ_PASS=admin
```

Forward both management UI and AMQP port (keep this running):
```bash
kubectl port-forward -n rabbitmq svc/rabbitmq 15672:15672 5672:5672
```

> **For Kubernetes deployments**: Set `RABBITMQ_HOST=rabbitmq.rabbitmq.svc.cluster.local` in your pod environment variables or ConfigMap.

### 2. Install Python RabbitMQ Client

Install pika (Python RabbitMQ client):
```bash
pip install pika
```

Or if using pip3:
```bash
pip3 install pika
```

### 3. Test Connection

Create a file `test_connection.py`:

```python
import os
import pika

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

try:
    # Connect to RabbitMQ with credentials
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
    )
    print("✅ Successfully connected to RabbitMQ!")
    print(f"   Connected to: {RABBITMQ_HOST}")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_connection.py
```

## Example 1: Simple Message Queue

### Producer (Send Messages)

Create `produce.py`:

```python
#!/usr/bin/env python
import os
import pika

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

# Connect to RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

# Create a queue (this is idempotent - safe to run multiple times)
channel.queue_declare(queue='hello')

# Send a message
message = "Hello World!"
channel.basic_publish(exchange='', routing_key='hello', body=message)
print(f" [x] Sent '{message}'")

# Close connection
connection.close()
```

### Consumer (Receive Messages)

Create `consume.py`:

```python
#!/usr/bin/env python
import os
import pika

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

# Connect to RabbitMQ
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

# Make sure the queue exists
channel.queue_declare(queue='hello')

# Define callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

# Set up consumer
channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
```

### Run the Examples

Assuming port-forward is already running from the Prerequisites section:

**Terminal 1** - Start the consumer (keep this running):
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=admin
export RABBITMQ_PASS=admin
python consume.py
```

You'll see: `[*] Waiting for messages. To exit press CTRL+C`

**Terminal 2** - Run the producer:
```bash
export RABBITMQ_HOST=localhost
export RABBITMQ_USER=admin
export RABBITMQ_PASS=admin
python produce.py
```

Run multiple times to send more messages.

Watch Terminal 1 to see messages appear!

## Example 2: Task Queue Pattern

This pattern distributes time-consuming tasks among multiple workers.

### Producer (`produce_task.py`)

```python
#!/usr/bin/env python
import os
import pika
import sys

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

# Durable queue survives RabbitMQ restart
channel.queue_declare(queue='task_queue', durable=True)

# Get message from command line or use default
message = ' '.join(sys.argv[1:]) or "Hello World!"

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # Make message persistent
    ))

print(f" [x] Sent {message}")
connection.close()
```

### Consumer (`consume_task.py`)

```python
#!/usr/bin/env python
import os
import pika
import time

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    # Simulate work (1 second per dot in message)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    # Acknowledge message processing
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Process one message at a time
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
```

### Run the Task Queue Example

Assuming port-forward is already running:

**Terminal 1** - Start the consumer (keep running):
```bash
python consume_task.py
```

**Terminal 2** - Run the producer (send multiple tasks):
```bash
python produce_task.py First task.
python produce_task.py Second task..
python produce_task.py Third task...
python produce_task.py Fourth task....
python produce_task.py Fifth task.....
```

Watch Terminal 1 to see the consumer processing tasks!

**Optional**: Start a second consumer in Terminal 3 to see load distribution.

## Example 3: Publish/Subscribe Pattern

Send messages to multiple consumers simultaneously.

### Producer (`produce_log.py`)

```python
#!/usr/bin/env python
import os
import pika
import sys

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

# Declare a fanout exchange
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)

print(f" [x] Sent {message}")
connection.close()
```

### Consumer (`consume_log.py`)

```python
#!/usr/bin/env python
import os
import pika

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials)
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

# Create temporary queue for this subscriber
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind queue to exchange
channel.queue_bind(exchange='logs', queue=queue_name)

def callback(ch, method, properties, body):
    print(f" [x] {body.decode()}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for logs. To exit press CTRL+C')
channel.start_consuming()
```

### Run the Pub/Sub Example

Assuming port-forward is already running:

**Terminal 1** - Start the consumer (keep running):
```bash

python consume_log.py
```

**Terminal 2** - Run the producer:
```bash
python produce_log.py "System started"
python produce_log.py "User logged in"
python produce_log.py "Processing complete"
```

Watch Terminal 1 to see all messages appear!

**Optional**: Start a second consumer in Terminal 3 to see both receiving the same messages.

## Monitoring Your Tests

While testing, you can monitor what's happening:

### Using the Management UI

1. Open http://localhost:15672 in your browser
2. Login with admin/admin
3. Go to "Queues" tab to see your queues
4. Click on a queue to see messages, rates, and consumers
5. Go to "Connections" tab to see active connections

### Verify Messages in Queues

In the management UI:
1. Click "Queues" tab
2. See your `hello` or `task_queue` queues
3. Check message counts in "Ready" and "Unacked" columns
4. Click queue name for detailed metrics

## Deploying to Kubernetes

Once you've tested locally, you're ready to deploy your application to Kubernetes!

### Update Environment Variables in Kubernetes

Your Python code doesn't need to change! Just configure the environment variables in your Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: harbor.javajon.duckdns.org/myproject/my-app:v1.0
        env:
        - name: RABBITMQ_HOST
          value: "rabbitmq.rabbitmq.svc.cluster.local"
        - name: RABBITMQ_USER
          value: "admin"
        - name: RABBITMQ_PASS
          value: "admin"
```

**Best Practice**: Use Kubernetes Secrets for credentials:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-credentials
  namespace: my-namespace
type: Opaque
stringData:
  RABBITMQ_USER: admin
  RABBITMQ_PASS: admin
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-namespace
spec:
  template:
    spec:
      containers:
      - name: app
        image: harbor.javajon.duckdns.org/myproject/my-app:v1.0
        env:
        - name: RABBITMQ_HOST
          value: "rabbitmq.rabbitmq.svc.cluster.local"
        - name: RABBITMQ_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: RABBITMQ_USER
        - name: RABBITMQ_PASS
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: RABBITMQ_PASS
```

That's it! Your code reads from environment variables, so it works seamlessly in both local development and Kubernetes.

### Complete Kubernetes Demo

For a full working example with producers and consumers running on Kubernetes, check out this demo repository:

**RabbitMQ Kubernetes Demo**: https://github.com/javajon/rabbitmq-demo

This repository demonstrates:
- Containerized producer and consumer applications
- Kubernetes Deployment manifests
- ConfigMaps for RabbitMQ connection configuration
- Best practices for running RabbitMQ clients in K8s
- Multiple messaging patterns (queues, pub/sub, RPC)

## Best Practices

1. **Always close connections** when done
2. **Use durable queues** for important data
3. **Acknowledge messages** after processing
4. **Handle connection failures** gracefully
5. **Set appropriate prefetch** for workers
6. **Use meaningful routing keys** for topic exchanges

## Troubleshooting Local Testing

### Port-forward disconnects

Run with automatic reconnection:
```bash
while true; do
    kubectl port-forward -n rabbitmq svc/rabbitmq 5672:5672 15672:15672
    sleep 1
done
```

### Connection timeout

Add connection timeout and retry logic:
```python
import os
import pika
import pika.exceptions

# Read connection settings from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')

try:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RABBITMQ_HOST,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=2
        )
    )
except pika.exceptions.AMQPConnectionError:
    print("Failed to connect to RabbitMQ")
    print("Make sure port-forward is running and RABBITMQ_HOST is set!")
```

### Can't see messages in queue
- Check if consumer is acknowledging messages (`auto_ack=True` or manual `ch.basic_ack()`)
- Verify queue names match between producer and consumer
- Look in management UI for unacknowledged messages

## Next Steps

After testing locally:
1. ✅ Containerize your application
2. ✅ Push to Harbor registry
3. ✅ Create Kubernetes manifests
4. ✅ Deploy to your team namespace
5. ✅ Check the [rabbitmq-demo repository](https://github.com/javajon/rabbitmq-demo) for complete examples

---

**Previous Section**: [Accessing RabbitMQ Admin Interface](#accessing-rabbitmq-admin-interface-from-your-laptop)

**Related Guides**:
- [Kubernetes Access Guide](./student-kubernetes-guide.md) - Setting up kubectl
- [Harbor Container Registry Guide](./student-harbor-guide.md) - Building and deploying containers