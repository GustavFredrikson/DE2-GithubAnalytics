kubectl cp default/main-repo-producer-pod:mrp_time_start bench_mrp_time_start
kubectl cp default/main-repo-producer-pod:mrp_time_end bench_mrp_time_end
kubectl cp default/frequently-updated-projects-consumer-pod:most_commits.csv most_commits.csv
kubectl cp default/programming-languages-consumer-pod:top_languages.csv top_languages.csv
kubectl cp default/programming-languages-consumer-pod:plc_time_start bench_plc_time_start
kubectl cp default/programming-languages-consumer-pod:plc_time_end bench_plc_time_end
kubectl cp default/devops-consumer-pod:devops.csv devops.csv
kubectl cp default/devops-consumer-pod:dc_start bench_dc_time_start
kubectl cp default/devops-consumer-pod:dc_end bench_dc_time_end
kubectl cp default/test-driven-development-consumer-pod:test_driven_development.csv test_driven_development.csv
