#!/bin/bash

# Step 0: Run as root
sudo -s

# Step 1: Create logs directory if it doesn't exist
mkdir -p /home/ubuntu/DE2-GithubAnalytics/logs/

# Step 1.5 Remove previous logs
rm /home/ubuntu/DE2-GithubAnalytics/logs/*.log

# Step 2: Install Python packages
pip3 freeze | xargs pip uninstall -y

python3 -m pip install -r /home/ubuntu/DE2-GithubAnalytics/requirements.txt

# Step 3: Copy the supervisord.conf to /etc/supervisor/conf.d/
cp /home/ubuntu/DE2-GithubAnalytics/supervisord.conf /etc/supervisor/supervisord.conf

# Step 4: Reread, update and start supervisor tasks
supervisorctl reread
supervisorctl update
supervisorctl start all

# Step 5: Print the status of supervisor tasks
supervisorctl status