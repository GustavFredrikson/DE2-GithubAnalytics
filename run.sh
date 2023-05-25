#!/bin/bash

# Step 0: If not root, echo error and exit
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Step 1: Create logs directory if it doesn't exist
mkdir -p /home/ubuntu/DE2-GithubAnalytics/logs/

# Step 1.5 Remove previous logs
rm /home/ubuntu/DE2-GithubAnalytics/logs/*

# Step 2: Install Python packages
pip3 freeze | xargs pip3 uninstall -y

python3 -m pip install -r /home/ubuntu/DE2-GithubAnalytics/requirements.txt

# Step 2.5: Check if port 6650 is open
# microk8s kubectl port-forward pulsar-proxy-0 6650:6650 -n pulsar &

# Step 3: Copy the supervisord.conf to /etc/supervisor/conf.d/
cp /home/ubuntu/DE2-GithubAnalytics/supervisord.conf /etc/supervisor/supervisord.conf

# If running, stop
supervisorctl stop all

# Step 4: Reread, update and start supervisor tasks
supervisorctl reread
supervisorctl update
supervisorctl start all

# Step 5: Print the status of supervisor tasks
supervisorctl status
