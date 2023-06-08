OLD_RELEASE_NAME="pulsar"
NEW_RELEASE_NAME="pulsar"
helm uninstall $OLD_RELEASE_NAME -n $OLD_RELEASE_NAME
kubectl delete ns $OLD_RELEASE_NAME
./pulsar-helm-chart/scripts/pulsar/cleanup_helm_release.sh --namespace $OLD_RELEASE_NAME --release $OLD_RELEASE_NAME
kubectl create ns $NEW_RELEASE_NAME
./pulsar-helm-chart/scripts/cert-manager/install-cert-manager.sh 
./pulsar-helm-chart/scripts/pulsar/prepare_helm_release.sh -n $NEW_RELEASE_NAME -k $NEW_RELEASE_NAME
helm install $NEW_RELEASE_NAME apache/pulsar \
    --namespace $NEW_RELEASE_NAME \
    --values pulsar-values.yaml \
