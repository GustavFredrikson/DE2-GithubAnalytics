#!/bin/bash

# Define the namespace for your pods
NAMESPACE="default"

# Define your Docker image
IMAGE="gustavfredrikson/de2python"

# Define your pod names and script names
declare -A PRODUCER_PODS=(
  ["main-repo-producer-pod"]="producers/main_repo_producer.py"
  ["frequently-updated-projects-producer-pod"]="producers/frequently_updated_projects_producer.py"
  ["programming-languages-producer-pod"]="producers/programming_languages_producer.py"
  ["devops-producer-pod"]="producers/devops_producer.py"
  ["test-driven-development-producer-pod"]="producers/test_driven_development_producer.py"
)

declare -A CONSUMER_PODS=(
  ["main-repo-consumer-pod"]="consumers/main_repo_consumer.py"
  ["frequently-updated-projects-consumer-pod"]="consumers/frequently_updated_projects_consumer.py"
  ["programming-languages-consumer-pod"]="consumers/programming_languages_consumer.py"
  ["devops-consumer-pod"]="consumers/devops_consumer.py"
  ["test-driven-development-consumer-pod"]="consumers/test_driven_development_consumer.py"
)

# Function to create a pod, copy a script to it, and run the script
function create_and_run_pod {
  local -n PODS=$1
  for POD_NAME in "${!PODS[@]}"; do
    SCRIPT_NAME=${PODS[$POD_NAME]}

    # Copy data from existing pods, similiar to this: microk8s kubectl cp default/frequently-updated-projects-consumer-pod:most_commits.csv most_commits.csv, microk8s kubectl cp default/programming-languages-consumer-pod:top_languages.csv top_languages.csv
    if [ $POD_NAME == "frequently-updated-projects-consumer-pod" ]; then
      echo "Copying most_commits.csv from pod $POD_NAME to local directory..."
      microk8s kubectl cp $NAMESPACE/$POD_NAME:most_commits.csv most_commits.csv
    fi

    if [ $POD_NAME == "programming-languages-consumer-pod" ]; then
      echo "Copying top_languages.csv from pod $POD_NAME to local directory..."
      microk8s kubectl cp $NAMESPACE/$POD_NAME:top_languages.csv top_languages.csv
    fi

    if [ $POD_NAME == "test-driven-development-consumer-pod" ]; then
      echo "Copying tdd_counts.csv from pod $POD_NAME to local directory..."
      microk8s kubectl cp $NAMESPACE/$POD_NAME:tdd_counts.csv tdd_counts.csv
    fi

    if [ $POD_NAME == "devops-consumer-pod" ]; then
      echo "Copying tdd_devops_counts.csv from pod $POD_NAME to local directory..."
      microk8s kubectl cp $NAMESPACE/$POD_NAME:tdd_devops_counts.csv tdd_devops_counts.csv
    fi

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

    # If it is frequently-updated-projects-consumer-pod, copy most_commits.csv to the pod
    # if [ $POD_NAME == "frequently-updated-projects-consumer-pod" ]; then
    #   echo "Copying most_commits.csv to pod $POD_NAME..."
    #   microk8s kubectl cp most_commits.csv $NAMESPACE/$POD_NAME:/tmp/most_commits.csv
    # fi

    # # If it is programming-languages-consumer-pod, copy top_languages.csv to the pod
    # if [ $POD_NAME == "programming-languages-consumer-pod" ]; then
    #   echo "Copying top_languages.csv to pod $POD_NAME..."
    #   microk8s kubectl cp top_languages.csv $NAMESPACE/$POD_NAME:/tmp/top_languages.csv
    # fi

    # # If it is test-driven-development-consumer-pod, copy tdd_counts.csv to the pod
    # if [ $POD_NAME == "test-driven-development-consumer-pod" ]; then
    #   echo "Copying tdd_counts.csv to pod $POD_NAME..."
    #   microk8s kubectl cp tdd_counts.csv $NAMESPACE/$POD_NAME:/tmp/tdd_counts.csv
    # fi

    # # If it is devops-consumer-pod, copy tdd_devops_counts.csv to the pod
    # if [ $POD_NAME == "devops-consumer-pod" ]; then
    #   echo "Copying tdd_devops_counts.csv to pod $POD_NAME..."
    #   microk8s kubectl cp tdd_devops_counts.csv $NAMESPACE/$POD_NAME:/tmp/tdd_devops_counts.csv
    # fi

    # Run the script in the pod
    echo "Running script $SCRIPT_NAME in pod $POD_NAME..."
    microk8s kubectl exec $POD_NAME -n $NAMESPACE -- /bin/bash -c "python /tmp/$(basename $SCRIPT_NAME)" &
  done
}

# Run the functions
create_and_run_pod PRODUCER_PODS
create_and_run_pod CONSUMER_PODS
