#!/bin/bash

# Define the namespace for your pods
NAMESPACE="default"

# Define an array of pod names
PODS=(
  "test-driven-development-consumer-pod"
  "main-repo-consumer-pod"
  "programming-languages-consumer-pod"
  "devops-consumer-pod"
  "frequently-updated-projects-consumer-pod"
  "devops-producer-pod"
  "main-repo-producer-pod"
  "programming-languages-producer-pod"
)

# Function to show the logs of a pod
function show_pod_logs {
  local POD_NAME=$1

  echo "Logs for pod $POD_NAME:"
  microk8s kubectl logs $POD_NAME -n $NAMESPACE
  echo "--------------------------------------------------"
}

# Iterate over the pods and show their logs
for POD_NAME in "${PODS[@]}"; do
  show_pod_logs $POD_NAME
done
