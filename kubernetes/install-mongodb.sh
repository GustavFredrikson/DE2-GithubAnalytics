microk8s helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-mongodb bitnami/mongodb --set mongodbRootPassword=secretpassword,mongodbUsername=gustavfredrikson,mongodbPassword=my-password,mongodbDatabase=my-database

# my-mongodb.default.svc.cluster.local