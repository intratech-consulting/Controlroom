import logging
from RabbitMQConsumer import RabbitMQConsumer

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    consumer = RabbitMQConsumer('Loggin_queue')
    consumer.start_consuming()

if __name__ == '__main__':
    main()
