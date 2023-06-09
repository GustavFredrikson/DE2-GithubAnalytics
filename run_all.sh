#!/bin/bash

NAMESPACE="default"

# Docker image name
IMAGE="gustavfredrikson/de2python"

declare -A PRODUCER_PODS=(
  ["main-repo-producer-pod"]="producers/main_repo_producer.py"
  ["frequently-updated-projects-producer-pod"]="producers/frequently_updated_projects_producer.py"
  ["programming-languages-producer-pod"]="producers/programming_languages_producer.py"
  ["devops-producer-pod"]="producers/devops_producer.py"
  ["test-driven-development-producer-pod"]="producers/test_driven_development_producer.py"
)

if [[ $1 == "--use-mongo" ]]; then
    CONSUMER_PODS=(
        ["main-repo-consumer-pod"]="consumers_mongo/main_repo_consumer.py"
        ["frequently-updated-projects-consumer-pod"]="consumers_mongo/frequently_updated_projects_consumer.py"
        ["programming-languages-consumer-pod"]="consumers_mongo/programming_languages_consumer.py"
        ["devops-consumer-pod"]="consumers_mongo/devops_consumer.py"
        ["test-driven-development-consumer-pod"]="consumers_mongo/test_driven_development_consumer.py"
    )
else
    CONSUMER_PODS=(
        ["main-repo-consumer-pod"]="consumers/main_repo_consumer.py"
        ["frequently-updated-projects-consumer-pod"]="consumers/frequently_updated_projects_consumer.py"
        ["programming-languages-consumer-pod"]="consumers/programming_languages_consumer.py"
        ["devops-consumer-pod"]="consumers/devops_consumer.py"
        ["test-driven-development-consumer-pod"]="consumers/test_driven_development_consumer.py"
    )
fi


# Function to create a pod, copy a script to it, and run the script
function create_and_run_pod {
  local -n PODS=$1
  for POD_NAME in "${!PODS[@]}"; do
    SCRIPT_NAME=${PODS[$POD_NAME]}

    # Delete the pod if it already exists
    echo "Deleting pod $POD_NAME if it already exists..."
    microk8s kubectl delete pod $POD_NAME --namespace=$NAMESPACE --ignore-not-found=true

    # Create the pod
    echo "Creating pod $POD_NAME..."
    microk8s kubectl run $POD_NAME --namespace=$NAMESPACE --image=$IMAGE --restart=Never -- sleep infinity

    # Wait for the pod to be ready
    echo "Waiting for pod $POD_NAME to be ready..."
    microk8s kubectl wait --namespace=$NAMESPACE --for=condition=ready pod/$POD_NAME --timeout=120s

    # List the available pods
    echo "Listing all available pods..."
    microk8s kubectl get pods --namespace=$NAMESPACE

    # Copy the script to the pod
    echo "Copying script $SCRIPT_NAME to pod $POD_NAME..."
    microk8s kubectl cp $SCRIPT_NAME $NAMESPACE/$POD_NAME:/tmp/$(basename $SCRIPT_NAME)

    # Copy .env to the pod
    echo "Copying .env to pod $POD_NAME..."
    microk8s kubectl cp .env $NAMESPACE/$POD_NAME:/tmp/.env

    # Run the script in the pod
    echo "Running script $SCRIPT_NAME in pod $POD_NAME..."
    microk8s kubectl exec $POD_NAME -n $NAMESPACE -- /bin/bash -c "python /tmp/$(basename $SCRIPT_NAME)" &
  done
}

# Run the functions
create_and_run_pod PRODUCER_PODS
create_and_run_pod CONSUMER_PODS
