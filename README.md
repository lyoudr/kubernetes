### Tools
---
- App: FastAPI to build my app. 
- ORM: SQLalchemy as my orm tool.
- DataBase: PostgreSQL as my database.
- Platform : Google Cloud Platform

#### Cluster
--- 
- Type: Autopilot Cluster, which I don't need to manage the underlying VMs.
![Example Image](https://drive.google.com/file/d/1WWaf2Crm3h0AOw8uU1f1XDjniYoiuHb0/view?usp=sharing)

#### Sales Service
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

#### Product Service


#### DataBase
- To access the data in your database in stance, you create a `PersistentVolumeClaim(PVC)` 
- A database that runs as a Service in a Kubernetes cluster and its database files in a `PersistentVolumeClaim`
    - PostgreSQL Installation
    `gcloud compute addresses create pg-static-ip --region=asia-east1` 