# DE2-GithubAnalytics


To get the data from the pods, run the following commands:
```bash
microk8s kubectl cp default/frequently-updated-projects-consumer-pod:most_commits.csv most_commits.csv
microk8s kubectl cp default/programming-languages-consumer-pod:top_languages.csv top_languages.csv
microk8s kubectl cp default/devops-consumer-pod:devops.csv devops.csv
microk8s kubectl cp default/test-driven-development-consumer-pod:test_driven_development.csv test_driven_development.csv
```

Using standard kubectl:
```bash
kubectl cp default/main-repo-producer-pod:mrp_time_start mrp_time_start
kubectl cp default/main-repo-producer-pod:mrp_time_end mrp_time_end
kubectl cp default/frequently-updated-projects-consumer-pod:most_commits.csv most_commits.csv
kubectl cp default/programming-languages-consumer-pod:top_languages.csv top_languages.csv
kubectl cp default/devops-consumer-pod:devops.csv devops.csv
kubectl cp default/test-driven-development-consumer-pod:test_driven_development.csv test_driven_development.csv
```
