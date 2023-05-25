#!/bin/bash

# Define the namespace for your pods
NAMESPACE="default"

# Define your Docker image
IMAGE="gustavfredrikson/de2python"

# Define your pod names and script names
declare -A PRODUCER_PODS=(
  ["devops-producer-pod"]="producers/devops_producer.py"
  ["frequently-updated-projects-producer-pod"]="producers/frequently_updated_projects_producer.py"
  ["main-repo-producer-pod"]="producers/main_repo_producer.py"
  ["programming-languages-producer-pod"]="producers/programming_languages_producer.py"
  ["test-driven-development-producer-pod"]="producers/test_driven_development_producer.py"
)

declare -A CONSUMER_PODS=(
  ["devops-consumer-pod"]="consumers/devops_consumer.py"
  ["frequently-updated-projects-consumer-pod"]="consumers/frequently_updated_projects_consumer.py"
  ["main-repo-consumer-pod"]="consumers/main_repo_consumer.py"
  ["programming-languages-consumer-pod"]="consumers/programming_languages_consumer.py"
  ["test-driven-development-consumer-pod"]="consumers/test_driven_development_consumer.py"
)

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
    microk8s kubectl wait --namespace=$NAMESPACE --for=condition=ready pod/$POD_NAME


    # List the available pods
    echo "Listing all available pods..."
    microk8s kubectl get pods --namespace=$NAMESPACE


    # Check the status of the pod
    echo "Checking status for pod $POD_NAME..."
    microk8s kubectl describe pod $POD_NAME --namespace=$NAMESPACE

    # Copy the script to the pod
    echo "Copying script $SCRIPT_NAME to pod $POD_NAME..."
    microk8s kubectl cp $SCRIPT_NAME $NAMESPACE/$POD_NAME:/tmp/

    # Run the script in the pod
    echo "Running script $SCRIPT_NAME in pod $POD_NAME..."
    microk8s kubectl exec $POD_NAME -n $NAMESPACE -- /bin/bash -c "python /tmp/$SCRIPT_NAME"
  done
}

# Run the functions
create_and_run_pod PRODUCER_PODS
create_and_run_pod CONSUMER_PODS
