# Kubernetes

## Minikube
https://minikube.sigs.k8s.io/docs/start

### Minikube management
```
minikube start|stop|status

# dind transparent:
minikube docker-env  

minikube dashboard
```

## Kubectl
CLI management of kubernetes

```
kubectl version
```

Manage context (cluster): can be stored in ~/.kube/config
```
kubectl config current-context      
kubectl config get-contexts
kubectl config use-context <name_of_context>
kubectl config view
```

