# DE2-GithubAnalytics

To start the pods with consumers/producers, run the following commands (with flag --use-mongo to use mongoDB)
```bash
./run_all.sh --use-mongo
```

To get the data from the pods, run the following commands:
```bash
microk8s kubectl cp default/frequently-updated-projects-consumer-pod:most_commits.csv most_commits.csv
microk8s kubectl cp default/programming-languages-consumer-pod:top_languages.csv top_languages.csv
microk8s kubectl cp default/devops-consumer-pod:devops.csv devops.csv
microk8s kubectl cp default/test-driven-development-consumer-pod:test_driven_development.csv test_driven_development.csv
```
