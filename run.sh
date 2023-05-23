sudo cp ~/DE2-GithubAnalytics/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
sudo supervisorctl status