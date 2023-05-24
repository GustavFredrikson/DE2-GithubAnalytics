helm uninstall pulsar -n pulsar
kubectl delete ns pulsar
./pulsar-helm-chart/scripts/pulsar/cleanup_helm_release.sh --namespace pulsar --release pulsar
kubectl create ns pulsar
./pulsar-helm-chart/scripts/cert-manager/install-cert-manager.sh 
./pulsar-helm-chart/scripts/pulsar/prepare_helm_release.sh -n pulsar -k pulsar
helm install pulsar apache/pulsar \
    --namespace pulsar \
    --values pulsar-values.yaml \
