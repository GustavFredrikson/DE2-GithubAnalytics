#!/bin/bash

# copy the configuration file to the appropriate directory
sudo cp /home/ubuntu/DE2-GithubAnalytics/supervisord.conf /etc/supervisor/supervisord.conf

# reload supervisor with the new configuration
sudo supervisorctl reread

# update and start services
sudo supervisorctl update
sudo supervisorctl start all
