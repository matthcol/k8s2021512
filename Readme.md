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

### Gestion des Pods
```
kubectl get pod                     # default namespace
kubectl get pod -A                  # all namespaces
kubectl get pod -n kube-system      # namespace kube-system

kubectl run echo-solo --image=kicbase/echo-server:1.0
kubectl get po
kubectl get pod
kubectl get pods

kubectl run nginx-solo --image=nginx:alpine-slim
kubectl get po
kubectl exec -it nginx-solo -- sh
    ps

Vue détaillée:
kubectl get pod nginx-solo -o wide       #  shop container IP : 10.244.0.16
kubectl get pod  nginx-solo -o json
kubectl get pod  nginx-solo -o yaml

kubectl get pod  nginx-solo -o jsonpath='{.status.podIP}'  # 10.244.0.16

Faire des commandes à l'intérieur du minikube (conteneur master)
```
minikube ssh                            # interactive mode
    curl 10.244.0.16

minikube ssh "curl 10.244.0.16"         # non interactive mode
minikube ssh "curl 10.244.0.14:8080"    # idem avec echo-solo
```

Describe (équivalent de docker inspect)
```
kubectl describe pod nginx-solo
```


Cycle de vie d'1 pod standalone:

kubectl get pod nginx-solo
kubectl get pod/nginx-solo

kubectl delete pod nginx-solo
kubectl delete pod/nginx-solo
```

## Déploiement avec replica set
```
kubectl create deployment echo --image=kicbase/echo-server:1.0 --replicas=2

kubectl get deployments      # echo
kubectl get deployment
kubectl get deploy
kubectl get deploy/echo

kubectl get replicasets     # echo-55df65f494
kubectl get replicaset
kubectl get rs

kubectl get po              # echo-55df65f494-b2lhm, echo-55df65f494-z4hn8

kubectl delete pod echo-55df65f494-z4hn8        # le pod supprimé va être recrée
kubectl get po              # echo-55df65f494-b2lhm, echo-55df65f494-lcp9l

kubectl scale deploy echo --replicas=5
kubectl get po

pod/echo-55df65f494-8qmv5   1/1     Running   0          9s
pod/echo-55df65f494-lcp9l   1/1     Running   0          5m10s
pod/echo-55df65f494-r94wm   1/1     Running   0          9s
pod/echo-55df65f494-rvkhc   1/1     Running   0          2m40s
pod/echo-55df65f494-xqg8x   1/1     Running   0          9s

kubectl scale deploy echo --replicas=2    # downscale 5 => 2

pod/echo-55df65f494-lcp9l   1/1     Running   0          6m9s
pod/echo-55df65f494-rvkhc   1/1     Running   0          3m39s
```

## Labels / Etiquettes
- https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
- https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#label

### Visualiser les labels
```
kubectl get deploy,rs,po --show-labels
```

Convention d'étiquettes:
- deployment : app=echo sur les 3 niveaux deployment, replicaset, pod
- run        : run=echo-solo

### Sélection par label
```
kubectl get deploy,rs,po -l app=echo
```

### Gestion des labels
Ajout d'un label:
```
kubectl label deploy echo environment=dev
```

Modif d'1 label:
```
kubectl label deploy echo environment=staging --overwrite
```

Supprimer d'1 label:
```
kubectl label deploy echo environment-
```

### Exemple d'utilisation du label
Suppression du déploiement:
```
kubectl get deploy,rs,po -l app=echo
kubectl delete deploy -l app=echo
kubectl get deploy,rs,po -l app=echo
```


## Déploiement avec Yaml
Répertoire echo-application et fichier echo.deployment.yml

### Premier déploiement
```
kubectl apply -f .\echo.deployment.yml
kubectl get deploy,rs,po --show-labels
```

### Modification statique du déploiement
Ajout d'un label, nombre de replicas, image dans le Yaml:
```
kubectl apply -f .\echo.deployment.yml
kubectl get deploy,rs,po --show-labels
```

### Modification dynamique
```
kubectl scale deploy echo --replicas=10
kubectl label deploy echo environment=staging
```

NB: en cas de suppression/recréation on repart sur les paramètres de base
```
kubectl delete deploy echo
kubectl apply -f .\echo.deployment.yml
kubectl get deploy,rs,po --show-labels
```

kubectl get pod --show-labels
kubectl get pod -l app=echo
kubectl get pod -l app=echo -o wide
minikube ssh "curl 10.244.0.57:8080" 
minikube ssh "curl 10.244.0.41:8080"


## Services
### Service ClusterIp 
kubectl expose pod echo-solo --port 8080
kubectl get services
kubectl get service
kubectl get svc 

echo-solo    ClusterIP   10.97.208.250   <none>        8080/TCP   63s

minikube ssh 
    curl 10.97.208.250:8080
```
kubectl delete svc echo-solo
kubectl expose pod echo-solo --port 8081 --target-port 8080 --name echo-service
kubectl get svc
# res: echo-service   ClusterIP   10.110.182.115   <none>        8081/TCP   7s

minikube ssh  curl 10.110.182.115:8081 
```

Test avec un pod provisoire:
```
kubectl run -it --rm --restart=Never --image=busybox -- bash
    wget 10.110.182.115:8081 -O -
    wget echo-service.default.svc.cluster.local:8081 -O -       # FQDN : <nom-service>.<namespace>.svc.cluster.local
```

### Service NodePort
Recreer le service avec le type NodePort (accès de l'exterieur possible)

kubectl delete svc echo-service
kubectl expose pod echo-solo --type NodePort --port 8081 --target-port 8080 --name echo-service
kubectl get svc
    echo-service   NodePort    10.111.160.187   <none>        8081:31131/TCP   30s

Tests en interne
minikube ssh  curl 10.111.160.187:8081
kubectl run -it --rm --restart=Never --image=busybox -- bash 
    wget echo-service.default.svc.cluster.local:8081 -O -

Tests en externe:
* NB : sous Linux, utiliser l'IP external-ip

curl http://<external-ip>:8081

* sous windows avec docker desktop:
 minikube service echo-service --url
    http://127.0.0.1:61625

curl http://127.0.0.1:61625

### Service LoadBalancer (CLI)

kubectl delete svc echo-service 
kubectl expose deploy echo --type LoadBalancer --port 8090 --target-port 8080 --name echo-service
kubectl get svc
    NAME           TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
    echo-service   LoadBalancer   10.104.248.70   <pending>     8090:32083/TCP   13s


Test exterieur:
* Pour minikube avec Docker Desktop sous Windows:  minikube tunnel (expose tous les services de type LoadBalancer)
 
```
curl localhost:8090 
```

Test en interne:
* minikube ssh curl 10.104.248.70:8090
* kubectl run -it --rm --restart=Never --image=busybox -- bash 
    wget echo-service.default.svc.cluster.local:8090 -O -

Résistance au pannes:
kubectl delete po echo-79548f6d55-d2c9g echo-79548f6d55-hwklz echo-79548f6d55-wb7f8


### Service LoadBalancer (Yaml)
kubectl delete svc echo-service 

kubectl apply -f echo.service.yml

Tests identique à la version CLI

## Conteneur paramétrable

### Gestion du registry d'images
Dans le cluster:
minikube ssh 
docker image ls
docker pull python:3.13-slim

Sur la machine hôte : dind
minkube docker-env      # apply output
docker image ls
docker pull python:3.13-slim

Sur la machine hôte : load (image host -> cluster)
docker pull python:3.12-slim  # machine hôte
docker image ls
minikube image load python:3.12-slim
minikube ssh "docker image ls | grep python"

### Deploiement avec variables d'environnement
Dans la specificication:  
```
        env:
          - name: NGINX_HOST
            value: k8s.nginx.org
          - name: NGINX_PORT
            value: "90"
```

```
kubectl apply -f nginx.deployment.yml
kubectl get po -l app=nginx
$POD_NAME='nginx-67f699b6c-n7w94'
kubectl logs $POD_NAME

$POD_NAME=$(kubectl get po -l app=nginx -o name)
$POD_NAME=$(kubectl get po -l app=nginx -o jsonpath='{.items[*].metadata.name}')

kubectl exec -it  $POD_NAME -- sh
    env    # OK: NGINX_HOST et NGINX_PORT sont bien définies

```

### Environnement dans une ConfigMap : CLI --from-litteral
```
kubectl create configmap web-env --from-literal NGINX_HOST=k8s.nginx.org --from-literal NGINX_PORT=90  
kubectl get configmaps
kubectl get configmap
kubectl get cm 
kubectl get cm web-env -o jsonpath='{.data}'  # {"NGINX_HOST":"k8s.nginx.org","NGINX_PORT":"90"}
kubectl delete cm web-env
```

### Environnement dans une ConfigMap : CLI --from-env-file
```
kubectl create configmap web-env --from-env-file .env
kubectl get cm web-env -o jsonpath='{.data}'  # {"NGINX_HOST":"k8s.nginx.org","NGINX_PORT":"90"}
kubectl delete cm web-env
```

### Environnement dans une ConfigMap Yaml
```
kubectl apply -f .\nginx.configmap.yml
kubectl get cm web-env -o jsonpath='{.data}'  # {"NGINX_HOST":"k8s.nginx.org","NGINX_PORT":"90"}
```

### Utilisation de l'environnement stocké dans la configmap
```
kubectl apply -f .\nginx.deployment.yml
kubectl get deploy,rs,po -l app=nginx
$POD_NAME=$(kubectl get po -l app=nginx -o jsonpath='{.items[*].metadata.name}')
kubectl exec -it  $POD_NAME -- sh
    env | grep "^NGINX_"
kubectl exec -t  $POD_NAME -- sh -c 'env | grep "^NGINX_"'
```


## Atelier BDD Postgres
Image : postgres

1er deploiement (pod standalone ou deployment avec rs 1) avec les 3 variables 
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD