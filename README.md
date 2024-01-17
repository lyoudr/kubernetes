### Architecture Diagram
---
![Architetcture](https://github.com/lyoudr/kubernetes/blob/main/interview.drawio.png)


### Tools
---
- App: FastAPI to build my app. 
- ORM: SQLalchemy as my orm tool.
- DataBase: PostgreSQL as my database.
- Platform : Google Cloud Platform

### Pre Install
- install kubectl 

    `
    gcloud components install kubectl
    `
### Cluster
--- 
- Type: Autopilot Cluster, which I don't need to manage the underlying VMs.
- create Cluster

    `
    gcloud container clusters create-auto ann-test \
        --location=asia-east1 \
        --project=test-project
    `



### Sales Service
---
1. Wrap app in this image

- Dockerfile

    ```
    # Dockerfile
    FROM python:3.9-slim

    WORKDIR /app 

    COPY . /app

    RUN pip install --no-cache-dir -r requirements.txt
    RUN pip install fastapi uvicorn 

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
    ```
2. Deploy this image to Artifact Registry

    `
    gcloud builds submit --tag asia-east1-docker.pkg.dev/{project_name}/ann-test/sales:v18 .
    `
3. Put this image in a Pod, and deploy this pod to GKE

- deployment.yaml

    ```
    apiVersion: apps/v1 
    kind: Deployment
    metadata:
    name: sales 
    spec:
    replicas: 1 
    selector:
        matchLabels:
        app: sales 
    template:
        metadata:
        labels:
            app: sales
        spec:
        containers:
        - name: sales
            image: asia-east1-docker.pkg.dev/ikala-cloud-swe-dev-sandbox/ann-test/sales:v3
            ports:
            - containerPort: 80
            resources:
            limits:
                memory: "10Mi"
                cpu: "10m"
            requests:
                memory: "5Mi"
                cpu: "5m" 
    ```
- deploy

    `kubectl apply -f k8s/deployment.yaml`

4. Define BackendConfig for health check

- sales/k8s/backendconfig.yaml

    ```
    apiVersion: cloud.google.com/v1
    kind: BackendConfig
    metadata:
    name: product-ingress
    spec:
    healthCheck:
        checkIntervalSec: 5
        timeoutSec: 5
        type: HTTP
        requestPath: /healthz # Adjust this to match your actual health check path
        port: 80
    ```

- deploy config file

    `
    kubectl apply -f sales/k8s/backendconfig.yaml
    `

4. Define a Service to include this Pod

- service.yaml

    ```
    apiVersion: v1
    kind: Service
    metadata:
    name: sales-service
    annotations:
        cloud.google.com/neg: '{"ingress": true}'
        beta.cloud.google.com/backend-config: '{"default": "product-ingress"}' # Reference to the BackendConfig
    spec:
    type: NodePort
    selector:
        app: sales
    ports:
    - protocol: TCP
        port: 80
        targetPort: 80
    ```

### Product Service
---
- exactly the same procedure as Sales Service

### Ingress
---
![Architetcture](https://github.com/lyoudr/kubernetes/blob/main/ingress.png)
> In GKE, an Ingress object defines rules for routing HTTP(S) traffic to applications running in a cluster. An Ingress object is associated with one or more Service objects, each of which is associated with a set of Pods.
- Two Types:
1. Ingress for external Application Load Balancers deploys the classic Application Load Balancer. This internet-facing load balancer is deployed globally across Google's edge network as a managed and scalable pool of load balancing resources. 
2. Ingress for internal Application Load Balancers deploys the internal Application Load Balancer. These internal Application Load Balancers are powered by Envoy proxy systems outside of your GKE cluster, but within your VPC network.

- product/k8s/ingress.yaml

    ```
    apiVersion: networking.k8s.io/v1
    kind: Ingress 
    metadata:
    name: product-ingress
    annotations:                             # are used to provide additional configuration
        kubernetes.io/ingress.class: "gce"   # Process the Ingress manifest and create an external Application Load Balancer.
    spec:
    rules:
    - http:
        paths:  
        - path: /product
            pathType: ImplementationSpecific
            backend:
            service:
                name: product-service
                port:
                number: 80
        - path: /product/*
            pathType: ImplementationSpecific
            backend:
            service:
                name: product-service
                port:
                number: 80
        - path: /sales
            pathType: ImplementationSpecific
            backend:
            service:
                name: sales-service
                port: 
                number: 80
        - path: /sales/*
            pathType: ImplementationSpecific
            backend:
            service:
                name: sales-service
                port: 
                number: 80
    ```

### DataBase
---
> Use a StatefulSet deploy a single-instance PostgreSQL container with a persistent volumen for data storage.
> To access the data in your database in stance, you create a `PersistentVolumeClaim(PVC)`.
> A database that runs as a Service in a Kubernetes cluster and its database files in a `PersistentVolumeClaim`

1. PostgreSQL Installation

    `gcloud compute addresses create pg-static-ip --region=asia-east1`

2. Deploy PostgreSQL Pod

- product/k8s/progresql.yaml

    ```
    ---
    apiVersion: v1 
    kind: Secret 
    metadata:
    name: pgsql
    type: Opaque  # is the tytpe of Secret. It means that the Secret can contain any arbitrary data.
    data:
    POSTGRES_PASSWORD: YW5ucGFzc3dk  # base64-encoded value of "annpasswd"
    ---
    apiVersion: apps/v1
    kind: StatefulSet                    
    metadata:
        name: pgsql 
        labels:
            app: pgsql 
    spec:
        serviceName: pgsql
        replicas: 1
        selector:      
            matchLabels:
                app: pgsql
        template:       
            metadata:
            labels:
                app: pgsql 
        spec:
            containers:
            - name: pgsql
                image: postgres:14.5
                imagePullPolicy: IfNotPresent 
                resources:
                limits:
                    memory: 2Gi
                requests:
                    memory: 2Gi 
                env:
                - name: POSTGRES_DB
                    value: ann
                - name: POSTGRES_USER
                    value: ann 
                - name: POSTGRES_PASSWORD
                    valueFrom:
                    secretKeyRef:
                        name: pgsql
                        key: POSTGRES_PASSWORD
                - name: PGDATA
                    value: /var/lib/postgresql/data/pgdata
                ports:
                - containerPort: 5432 
                    name: postgresdb 
                volumeMounts:
                - name: postgres-data 
                    mountPath: /var/lib/postgresql/data 
    volumeClaimTemplates:                  
    - metadata:
        name: postgres-data
        spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard-rwo
        resources:
            requests:
            storage: 100Gi
    ```

3. Define a PostgreSQL Service which includes Pod described above, use selector to select its pod.

- prodcut/k8s/pg_service.yaml

    ```
    ---
    apiVersion: v1 
    kind: Service 
    metadata:
    annotations:
        cloud.google.com/14-rbs: "enabled"
    name: pgsql
    labels:
        app: pgsql
    spec:
    ports:
    - port: 5432 
        name: pgsql
        targetPort: postgresdb
    type: LoadBalancer 
    selector:
        app: pgsql
    externalTrafficPolicy: Cluster 
    ```


### Communicate Between Product Service and Sales Service
---
> If Product Service wants to call API in Sales Service, use **DNS name** of Sales Service instead of internal IP. Because the IP address may change each time we deploy new pod. 

- product/main.py

    ```
    @app.get('/product/bbb')
    def get_sales():
        # res = requests.get('http://10.107.0.50/sales') # (X) Because pod IP may change
        res = requests.get('http://sales-service/sales') # (V) Instead, use service name
        return res.json()
    ```

### Product Service Connect to PostgreSQL Service
---
1. DataBase connection env is defined in product/k8s/deployment.yaml
- product/sql_app/database.py

    ```
    from sqlalchemy import create_engine 
    from sqlalchemy.ext.declarative import declarative_base 
    from sqlalchemy.orm import sessionmaker

    import os
    
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    postgres_db = os.environ.get("POSTGRES_DB", "ann")
    postgres_user = os.environ.get("POSTGRES_USER", "ann")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "")

    SQLALCHEMY_DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
    ```