helm install mdb-repl stable/mongodb --debug --kube-insecure-skip-tls-verify --debug \
    --set mongodbRootPassword="104gfdij32i5235s29j",mongodbUsername=root,mongodbPassword="104gfdij32i5235s29j",mongodbDatabase=default \
    --set arbiter.enabled=false \
    --set replicaSet.enabled=true \
    --set replicaSet.pdb.enabled=false \
    --set ingress.enabled=true \
    --set global.storageClass="local-path" 
