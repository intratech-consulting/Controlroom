Service Monitoring System
This service is designed to monitor other services, checking if they are up or down. It also notifies administrators via email when a system is down.

Table of Contents
Prerequisites
Setup
Usage
Ports
Technologies
Contact
Prerequisites
Docker
Docker Compose
Setup
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <repository_directory>
Initialize the users and set up the project by running:

bash
Copy code
docker-compose up setup
Once the setup is complete, start the services:

bash
Copy code
docker-compose up
Usage
After starting the services, the system will automatically monitor the specified services. If any service goes down, an email notification will be sent to the administrators.

Accessing Services
Elasticsearch: http://localhost:9200
Kibana: http://localhost:5601
Logstash: http://localhost:9600
Ports
9200: Elasticsearch
5601: Kibana
9600: Logstash
Technologies
This project utilizes the ELK stack:

Elasticsearch: For storing and indexing logs.
Logstash: For collecting, parsing, and transforming logs.
Kibana: For visualizing data and logs.
Contact
For any issues or inquiries, please contact admin@example.com.
