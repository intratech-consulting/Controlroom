#!/bin/bash

# Initialize return value to 0 (success)
returnvalue=0

# Navigate to the appropriate directory
cd Controlroom-Monitoring || echo "Already in Controlroom-Monitoring directory"

# Ensure Docker Compose is installed
echo "Installing Docker Compose if not already installed..."
sudo apt-get update && sudo apt-get install docker-compose -y

# Start all services as defined in docker-compose.yml
echo "Starting services defined in docker-compose..."
docker-compose up -d

# Check the docker-compose configuration
echo "Checking docker-compose configuration..."
docker-compose config --quiet && docker_compose="Docker-compose OK" || docker_compose="Docker-compose ERROR"

# Check Elasticsearch service
echo "Validating Elasticsearch (es01)..."
until curl -s --cacert config/certs/ca/ca.crt https://es01:9200 | grep -q "You Know, for Search"; do
    echo "Waiting for Elasticsearch to become available..."
    sleep 10
done
echo "Elasticsearch is up and running."

# Check Kibana service
echo "Validating Kibana..."
until curl -s -I http://localhost:${KIBANA_PORT} | grep -q 'HTTP/1.1 302 Found'; do
    echo "Waiting for Kibana to become available..."
    sleep 10
done
echo "Kibana is up and running."

# Check Logstash service
echo "Validating Logstash..."
logstash_health_check=$(curl -s -u elastic:${ELASTIC_PASSWORD} https://localhost:9600)  # Update with Logstash monitoring port if different
if [[ $logstash_health_check == *"status"*"green"* ]]; then
    echo "Logstash is up and running."
else
    echo "Failed to validate Logstash status."
    returnvalue=1
fi

# Optionally, shut down services after validation
echo "Tearing down services..."
docker-compose down

# Exit with the appropriate status
exit $returnvalue