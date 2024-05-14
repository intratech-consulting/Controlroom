# Service Monitoring System

This service is designed to monitor other services, checking if they are up or down. It also notifies administrators via email when a system is down.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Ports](#ports)
- [Technologies](#technologies)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Prerequisites
- Docker
- Docker Compose

## Setup

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Initialize the users and set up the project by running:

    ```bash
    docker-compose up setup
    ```

3. Once the setup is complete, start the services:

    ```bash
    docker-compose up
    ```

## Usage

After starting the services, the system will automatically monitor the specified services. If any service goes down, an email notification will be sent to the administrators.

### Accessing Services

- **Elasticsearch**: [http://localhost:9200](http://localhost:9200)
- **Kibana**: [http://localhost:5601](http://localhost:5601)
- **Logstash**: [http://localhost:9600](http://localhost:9600)

## Ports

- **9200**: Elasticsearch
- **5601**: Kibana
- **9600**: Logstash

## Technologies

This project utilizes the ELK stack:

- **Elasticsearch**: For storing and indexing logs.
- **Logstash**: For collecting, parsing, and transforming logs.
- **Kibana**: For visualizing data and logs.

## Acknowledgements

This project was inspired by and built upon the setup provided by the [docker-elk](https://github.com/deviantony/docker-elk) repository by deviantony.

## Contact

For any issues or inquiries, please contact [admin@example.com](mailto:admin@example.com).
