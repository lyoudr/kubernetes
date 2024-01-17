#### Cluster
- Network
    - VPC-native is the default network mode for all clusters in GKE

#### Service 
- Service is to group a set of Pod endpoints intot a single resource.
    - get a stable cluster IP address
    - A client sends a request to the stable IP address, and the request is routed to one of the Pods in the Service.
    - A Service identifies its member Pods with a selector.
    ```
    apiVersion: v1
    kind: Service
    metadata:
        name: my-service
    spec:
        selector:
            app: metrics
            department: engineering
        ports:
    ```
    --- 
    - Types of Kubernetes Services
        - ClusterIP (default): Internal clients send requests to a stable internal IP address
            ```
            apiVersion: v1
            kind: Service
            metadata:
                name: my-cip-service
            spec:
                selector:
                    app: metrics
                    department: sales
                type: ClusterIP
                ports:
                - protocol: TCP
                    port: 80
                    targetPort: 8080
            ```
        
        NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   POR(S)
        my-cip-service   ClusterIP   10.11.247.213   none          80/TCP
        
        - NodePort: Clients send requests to the IP address of a node on one or more nodePort values that are specified by the Service
            - When  you creaete a Service of type NodePort, Kubernetes gives you a nodePort value. Then the Service is accessible by using the IP address of any node along with the nodePort value
            ```
            apiVersion: v1
            kind: Service
            metadata:
                name: my-np-service
            spec:
            selector:
                app: products
                department: sales
            type: NodePort
            ports:
            - protocol: TCP
                port: 80
                targetPort: 8080
            ```
            - After you create the Service, you can use `kubectl get service -o yaml` to view its specification 
            ```
            spec:
            clusterIP: 10.11.254.114
            externalTrafficPolicy: Cluster
            ports:
            - nodePort: 32675
                port: 80
                protocol: TCP
                targetPort: 8080
            ```
            - For example, suppose the external IP address of one of the cluster nodes is 203.0.113.2. Then for the preceding example, the external client calls the Service at 203.0.113.2 on TCP port 32675.
        - LoadBalancer: Clientts send requests to the IP address of a network load balancer.


#### IP location
- Pod IP  - 從 node 來的 IP CIDR range
- Service IP 
    - Cluster IP
    - Kubernetes assigns a stable, reliable IP address    to each newly-created Service from the cluster's pool
    - Kubernetes also assigns a hostname to the ClusterIP, by adding a DNS entry
    - External Load Balancer
      - 如果要讓外部的 request 直接 reach Service, 設定 type : LoadBalancer
    - Internal Load Balancer 
      - 如果是在同個 vpc, 可使用 internal passsthrough Network Load Balancer


- 在 Pod 內部的 continaer，彼此可以互相使用 localhost 溝通


