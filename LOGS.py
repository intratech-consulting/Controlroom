from lxml import etree
import pika
from datetime import datetime

# Define your XML and XSD as strings
Loggin_xml = """
<LogEntry>
    <SystemName>ExampleSystem</SystemName>
    <FunctionName>ProcessData</FunctionName>
    <Logs>Execution started successfully.</Logs>
    <Error>false</Error>
    <Timestamp>{}</Timestamp>
</LogEntry>
"""

Loggin_xsd = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="LogEntry">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="SystemName" type="xs:string"/>
                <xs:element name="FunctionName" type="xs:string"/>
                <xs:element name="Logs" type="xs:string"/>
                <xs:element name="Error" type="xs:boolean"/>
                <xs:element name="Timestamp" type="xs:dateTime"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
"""

# Parse the XSD document
xsd_doc = etree.fromstring(Loggin_xsd.encode())

# Create a schema object
schema = etree.XMLSchema(xsd_doc)

# Setup connection and channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='Loggin_queue', durable=True)

# Format the XML with the current timestamp
formatted_Loggin_xml = Loggin_xml.format(datetime.utcnow().isoformat())

# Parse the XML
xml_doc = etree.fromstring(formatted_Loggin_xml.encode())

# Validate the XML against the schema
if schema.validate(xml_doc):
    print('XML is valid')
    # Publish the message to the queue
    channel.basic_publish(exchange='', routing_key='Loggin_queue', body=formatted_Loggin_xml)
    print('Message sent')
else:
    print('XML is not valid')

# Close the connection
connection.close()