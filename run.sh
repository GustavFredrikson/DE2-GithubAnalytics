#!/bin/bash

# Step 1: Create logs directory if it doesn't exist
mkdir -p ~/DE2-GithubAnalytics/logs/

# Step 1.5 Remove previous logs
sudo rm ~/DE2-GithubAnalytics/logs/*.log

# Step 2: Install Python packages
pip3 freeze | xargs pip uninstall -y

python3 -m pip install -r ~/DE2-GithubAnalytics/requirements.txt

# Step 3: Copy the supervisord.conf to /etc/supervisor/conf.d/
sudo cp /home/ubuntu/DE2-GithubAnalytics/supervisord.conf /etc/supervisor/supervisord.conf

# Step 4: Reread, update and start supervisor tasks
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Step 5: Print the status of supervisor tasks
sudo supervisorctl status