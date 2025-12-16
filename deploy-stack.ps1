kubectl create namespace moviestack
kubectl config set-context --current --namespace moviestack

kubectl create configmap db-env --from-env-file db/.env 
kubectl create secret generic db-secret --from-env-file db/.env-secret
kubectl create configmap sql-init --from-file db/sql-init


kubectl apply -f db/db.statefulset.yml
kubectl apply -f db/db.service.yml

kubectl apply -f api/api.deployment.yml
kubectl apply -f api/api.service.yml

kubectl get cm,secret,pv,pvc

kubectl get all