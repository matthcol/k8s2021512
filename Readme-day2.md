# Kubernetes (day 2)

## Secrets
Recreer la config map sans les credentials:
```
kubectl delete cm db-env
 kubectl create  cm db-env --from-env-file   .env
 kubectl get  cm db-env -o jsonpath='{.data}'   # {"DBNAME":"dbmovie"}
 ```

Creer le secret :
```
kubectl create secret generic db-secret --from-env-file .env-secret
 kubectl get secret  db-secret -o jsonpath='{.data}'       # {"PASSWORD":"bW9ucGFzc3dvcmRlbmNsYWly","USER":"bW92aWU="}
  kubectl get secret  db-secret -o jsonpath='{.type}'      # Opaque
```

8 types natifs :
1. `Opaque`
2. `kubernetes.io/service-account-token`
3. `kubernetes.io/dockercfg`
4. `kubernetes.io/dockerconfigjson`
5. `kubernetes.io/basic-auth`
6. `kubernetes.io/ssh-auth`
7. `kubernetes.io/tls`
8. `bootstrap.kubernetes.io/token`

Fournis par 1 tier: exemple HashiCorp Vault

Recreer le pod:
```
kubectl delete po dbmovie
kubectl apply -f db.pod.yml
kubectl logs dbmovie
kubectl exec -it  dbmovie -- psql -U movie -d dbmovie
```

## Config Map avec fichiers
Equivalent à un dossier avec des petits fichiers que l'on peut monter sur 1 pod

```
kubectl create cm sql-init --from-file sql-init 
kubectl get cm sql-init  -o jsonpath='{.data}'   # {"01-tables.sql":"\r\ncreate table person .... "}
```

Recreer le pod:
```
kubectl delete po dbmovie
kubectl apply -f db.pod.yml
kubectl logs dbmovie
kubectl exec -it  dbmovie -- bash
    cd /docker-entrypoint-initdb.d/
    ls
    cat 01-tables.sql
    history
    psql -U movie -d dbmovie
        \d
        select * from movie;
        insert into movie(title, year) values ('Titre original : Avatar: Fire and Ash', 2025);
        select * from movie;
kubectl delete po dbmovie
kubectl apply -f db.pod.yml
kubectl exec -it  dbmovie -- psql -U movie -d dbmovie -c "select * from movie"
```

## Persistent Volume
Recreer le pod avec 1 volume persistant
```
kubectl delete po dbmovie
kubectl apply -f db.pvc.yml
kubectl apply -f db.pod.yml
kubectl get pvc,pv
kubectl logs dbmovie
kubectl exec -it  dbmovie -- psql -U movie -d dbmovie
    select * from movie;
    insert into movie(title, year) values ('Titre original : Avatar: Fire and Ash', 2025);
    select * from movie;
```

Recreer le pod : pas de perte de données stockées dans le PV
```
kubectl delete po dbmovie;
kubectl apply -f db.pod.yml
kubectl exec -it  dbmovie -- psql -U movie -d dbmovie -c "select * from movie"
```

## StatefulSet + PersistentVolume

```
kubectl delete po dbmovie
kubectl delete pvc db-pvc  # delete both pv and pvc
kubectl apply -f db.statefulset.yml 
kubectl get pv,pvc                          # PVC: db-data-dbmovie-0
kubectl get statefulset,po -l app=dbmovie   # POD: dbmovie-0

kubectl exec -it  dbmovie-0 -- psql -U movie -d dbmovie
    select * from movie;
    insert into movie(title, year) values ('Titre original : Avatar: Fire and Ash', 2025);
    select * from movie;
```

Resistance aux pannes
```
kubectl delete po dbmovie-0
kubectl get po -l app=dbmovie
kubectl exec -it  dbmovie-0 -- psql -U movie -d dbmovie -c "select * from movie"
kubectl logs dbmovie-0 
    # PostgreSQL Database directory appears to contain a database; Skipping initialization
```

## Service Headless
```
kubectl delete statefulset dbmovie  
kubectl get pv,pvc,sts                      # PV+PVC are still here
kubectl apply -f db.service.yml 
kubectl get svc,sts,po -l app=dbmovie       # Service ClusterIP: None
```

Test du service avec 1 client DB postgresql:
```
kubectl run -it --rm --restart=Never test-dbmovie --image=postgres:18 -- bash 
    psql -U movie -d dbmovie -h dbmovie-0.dbmovie-service.default.svc.cluster.local
    select * from movie;
```

Nommage DNS avec 1 service Headless: <pod-name>.<headless-service>.<namespace>.svc.cluster.local

### Changer le nb de replicas
- par la clé replicas de db.statefulset.yml (1 => 2)  + apply
- scale

```
kubectl apply -f db.statefulset.yml    
kubectl get po -l app=dbmovie           # dbmovie-0, dbmovie-1
kubectl scale sts dbmovie --replicas=3
kubectl get po -l app=dbmovie           # dbmovie-0, dbmovie-1, dbmovie-3
kubectl get pv,pvc                      # 3 fois PVC+PV
```

### DNS avec FQDN (nom complet)
```
kubectl run -it --rm --restart=Never test-dbmovie --image=postgres:18 -- `
    psql -U movie -d dbmovie -h dbmovie-0.dbmovie-service.default.svc.cluster.local
        select * from movie;

kubectl run -it --rm --restart=Never test-dbmovie --image=postgres:18 -- `
    psql -U movie -d dbmovie -h dbmovie-1.dbmovie-service.default.svc.cluster.local
        select * from movie;
```

### DNS avec nom simple (scope = namespace)
```
kubectl run -it --rm --restart=Never test-dbmovie --image=postgres:18 -- `
    psql -U movie -d dbmovie -h dbmovie-0.dbmovie-service
        select * from movie;
```
NB: les replicas ne sont pas synchronisés => TODO: à mettre en place (cf Helm)


## Deploiement API avec une image métier

Dans le dossier api (registry local de minikube):
```
docker build -t movieapi:1.0 api-v1.0
docker image ls              # movieapi:1.0   190M
```

DB_URL = postgresql+psycopg2://user:password@host:5432/mydatabase


```
kubectl apply -f api.deployment.yml
kubectl apply -f api.service.yml
minikube tunnel     # si pas déjà lancé
```

Test API avec Swagger:
    http://localhost:90/docs


Diagnostic:
 kubectl get svc,deploy,rs,sts,po -l app=movieapi    
 kubectl get all -l app=movieapi 
 kubectl describe po movieapi-6454c5b874-7kz5g     # NB: variables d'env + image conteneur : movieapi:1.0
 kubectl logs movieapi-6454c5b874-7kz5g
 
 kubectl get svc,deploy,rs,sts,po -l app=dbmovie    
 kubectl get all -l app=dbmovie 
 kubectl describe po dbmovie-0  
 kubectl logs dbmovie-0  

kubectl get all -l app=movieapi -o wide   # l'image est préciséee sur deployment + replicaset : movieapi:1.0
kubectl get po -l app=movieapi -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\t"}{..phase}{"\n"}{end}'

## Mise à jour d'1 déploiement

docker build -t movieapi:2.0 api-v2.0

Changer l'image du deploiement: 
- changer le YAML + apply
- CLI: kubectl set image 

```
kubectl set image deploy/movieapi movieapi=movieapi:2.0
kubectl get po -l app=movieapi -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\t"}{..phase}{"\n"}{end}'
kubectl rollout status deploy/movieapi
kubectl rollout history deploy/movieapi

kubectl rollout undo deploy/movieapi
kubectl rollout status deploy/movieapi
kubectl get po -l app=movieapi -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\t"}{..phase}{"\n"}{end}'

kubectl rollout undo deploy/movieapi --to-revision=2
kubectl rollout status deploy/movieapi
kubectl get po -l app=movieapi -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\t"}{..phase}{"\n"}{end}'
```

Test API:

```
kubectl run test-curl -it --rm --restart=Never --image=curlimages/curl -- sh
    curl -s -w "[%{remote_ip}] %{http_code} %{time_total}s\n " -G http://movieapi:90/movies/
    curl -s -w "[%{remote_ip}] %{http_code} %{time_total}s\n " -G http://movieapi:90/persons/
    seq 1000 | xargs -n1 -P10 -I{} curl -s -w "[%{remote_ip}] %{http_code} %{time_total}s\n " -G http://movieapi:90/movies/ -o /dev/null
```

## Probes
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

Catégorie de probe (délai défaut 10s):
- livenessProbe: utile pour le restart (en continu)
- readinessProbe: utile pour les services (en continu)
- startupProbe:  utilisée jusqu'au 1er succes => puis relais à liveness/readiness

Type d'outil probe:
- httpGet (API, frontend, ...) => OK si status est 2xx ou 3xx
- tcpSocket (DB, ...) => OK si réponse
- exec (any command) => OK si status 0

Application à la base de données (tcpSocket pour liveness et exec pour readiness)
```
kubectl delete sts dbmovie
kubectl delete pvc db-data-dbmovie-0 db-data-dbmovie-1 db-data-dbmovie-2

kubectl apply -f db.statefulset.yml
kubectl get pod,svc -l app=dbmovie
```

Application à l'API (httpGet pour liveness et readiness)
```
kubectl apply -f .\api.deployment.yml
kubectl get all -l app=movieapi -o wide 
```

## Namespaces
```
kubectl get all         # default namespace : default
kubectl get all -A      # all namespaces
kubetcl get -n default
kubetcl get -n kube-system
```

Avantages:
* differents environnements : dev, staging, prod
* multi-tenant
* DNS : routage relatif au namespace vs routage global (FQDN)

Exemple: 
    <pod-name>.<headless-service>.<namespace>.svc.cluster.local   # FQDN : global
    <pod-name>.<headless-service>                                 # current namespace

kubectl create namespace moviestack

### Utilisation du namespace : méthode explicite (-n)

kubectl create configmap db-env --from-env-file db/.env -n moviestack
kubectl get cm -n moviestack

### Utilisation du namespace : méthode explicite (variable d'environnement)
Powershell:
```
$env:KUBECTL_NAMESPACE='moviestack'
function kctl {
    kubectl -n $env:KUBECTL_NAMESPACE @args
}
```

Bash:
```
export KUBECTL_NAMESPACE=moviestack
alias kctl=kubectl -n $KUBECTL_NAMESPACE
```
### Utilisation du namespace : configuration kubectl

```
kubectl config get-contexts                                     # *         minikube   minikube   minikube   default
kubectl config set-context --current --namespace moviestack
kubectl config get-contexts                                     # *         minikube   minikube   minikube   moviestack
```

### Cleanup namespace default
```
kubectl delete all  --all -n default
kubectl delete pv,pvc,cm,secret --all -n default
kubectl get pv,pvc,cm,secret -n default
```

### Stack complet sur namespace particulier

```
kubectl delete ns moviestack
.\deploy-stack.ps1
```

Test DB from API:
```
kubectl run -it --rm --restart=Never --image=busybox:1.37 -- bash
```










