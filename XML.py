from lxml import etree
import pika
import time
import datetime

# Define your XML and XSD as strings
heartbeat_xml = """
<Heartbeat>
    <Timestamp>{}</Timestamp>
    <Status>1</Status>
    <SystemName>ExampleSystem</SystemName>
</Heartbeat>
"""

heartbeat_xsd = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="Heartbeat">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="Timestamp" type="xs:dateTime" />
                <xs:element name="Status" type="xs:string" />
                <xs:element name="SystemName" type="xs:string" />
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
"""

# Parse the documents
xsd_doc = etree.fromstring(heartbeat_xsd.encode())

# Create a schema object
schema = etree.XMLSchema(xsd_doc)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

channel.queue_declare(queue='heartbeat_queue', durable=True )

# Loop to send heartbeat message every two seconds
try:
    while True:
        formatted_heartbeat_xml = heartbeat_xml.format(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f"))
        xml_doc = etree.fromstring(formatted_heartbeat_xml.encode())
        # Validate
        if schema.validate(xml_doc):
            print('XML is valid')
            channel.basic_publish(exchange='', routing_key='heartbeat_queue', body=formatted_heartbeat_xml)
            print('Message sent')
        else:
            print('XML is not valid')
        time.sleep(1)  # Wait for 2 seconds
except KeyboardInterrupt:
    # Graceful shutdown on Ctrl+C
    print("Stopping...")
finally:
    connection.close()
