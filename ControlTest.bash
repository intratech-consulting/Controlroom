#!/bin/bash

# Initialize return value to 0 (success)
returnvalue=0

# Navigate to the appropriate directory
cd Controlroom-Monitoring || echo "Already in Controlroom-Monitoring directory"

# Ensure Docker Compose is installed
echo "Installing Docker Compose if not already installed..."
sudo apt-get update && sudo apt-get install docker-compose -y

network_name="my_shared_network"
if ! docker network ls | grep -qw $network_name; then
  echo "Network $network_name does not exist, creating..."
  docker network create $network_name
fi

# Start all services as defined in docker-compose.yml
echo "Starting services defined in docker-compose..."
docker-compose up -d

# Check the docker-compose configuration
echo "Checking docker-compose configuration..."
docker-compose config --quiet && docker_compose="Docker-compose OK" || docker_compose="Docker-compose ERROR"

check_container() {
  local container_name="$1"
  echo "Checking $container_name..."
  if [ "$(docker inspect -f '{{.State.Running}}' $container_name)" == "true" ]; then
    echo "$container_name is running."
  else
    echo "Failed to start $container_name."
    returnvalue=1
  fi
}

# Validate containers are running
echo "Validating Elasticsearch (es01)..."
check_container es01

echo "Validating Kibana..."
check_container kibana

echo "Validating Logstash..."
check_container logstash01

# Optionally, shut down services after validation
echo "Tearing down services..."
docker-compose down

# Exit with the appropriate status
exit $returnvalue