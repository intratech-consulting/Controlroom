import pika

# Your XML content
xml_content = """<?xml version="1.0" encoding="UTF-16"?>
<root>
<events>
    <event>
        <id>1</id>
        <datum>2024-04-01</datum>
        <startuur>09:00</startuur>
        <einduur>11:00</einduur>
        <locatie>Lokaal 101</locatie>
        <spreker>
            <naam>John Doe</naam>
            <email>john.doe@example.com</email>
            <bedrijf>XYZ Corporation</bedrijf>
        </spreker>
        <max_inschrijvingen>50</max_inschrijvingen>
        <beschikbare_plaatsen>25</beschikbare_plaatsen>
        <beschrijving>Introduction to XML</beschrijving>
    </event>
    <event>
        <id>2</id>
        <datum>2024-04-05</datum>
        <startuur>14:00</startuur>
        <einduur>16:00</einduur>
        <locatie>Lokaal 201</locatie>
        <spreker>
            <naam>Jane Smith</naam>
            <email>jane.smith@example.com</email>
            <bedrijf>ABC Corporation</bedrijf>
        </spreker>
        <max_inschrijvingen>30</max_inschrijvingen>
        <beschikbare_plaatsen>10</beschikbare_plaatsen>
    </event>
    <!-- You can add more events here -->
</events>
<user>
    <user_id>789</user_id>
    <user_name>Alice</user_name>
    <user_email>alice@example.com</user_email>
    <user_company>ABC Corp</user_company>
    <user_role>Participant</user_role>
</user>

<registration>
    <registration_id>987</registration_id>
    <user_id>789</user_id>
    <session_id>456</session_id>
    <registration_date>2024-05-10</registration_date>
    <registration_status>Confirmed</registration_status>
</registration>

<purchases>
    <purchase_id>654</purchase_id>
    <user_id>789</user_id>
    <product_id>123</product_id>
    <quantity>2</quantity>
    <purchase_date>2024-05-15</purchase_date>
    <total_amount>20.00</total_amount>
    <payment_method>Cash</payment_method>
</purchases>

<factuur>
    <verkoper>
        <naam></naam>
        <adress>
            <land></land>
            <staat></staat>
            <gemeente></gemeente>
            <postcode></postcode>
            <straat></straat>
            <huisnummer></huisnummer>
        </adress>
        <contact>
            <telefoonnummer></telefoonnummer>
            <e-mail></e-mail>
        </contact>
    </verkoper>
    <koper>
        <naam></naam>
        <adress>
            <land></land>
            <staat></staat>
            <gemeente></gemeente>
            <postcode></postcode>
            <straat></straat>
            <huisnummer></huisnummer>
        </adress>
        <contact>
            <telefoonnummer></telefoonnummer>
            <e-mail></e-mail>
        </contact>
    </koper>
    <factuurgegevens>
        <Factuurnummer></Factuurnummer>
        <Factuurdatum></Factuurdatum>
        <Betalingsvoorwaarden></Betalingsvoorwaarden>
        <Vervaldatum></Vervaldatum>
    </factuurgegevens>
    <products>
        <Product>
            <naam></naam>
            <Beschrijving></Beschrijving>
            <hoeveelheid></hoeveelheid>
            <prijsHT></prijsHT> <!-- zonder taxes per eenheid-->
        </Product>
        <Product>
            <naam></naam>
            <Beschrijving></Beschrijving>
            <hoeveelheid></hoeveelheid>
            <prijsExBtw></prijsExBtw> <!-- zonder taxes per eenheid-->
            <prijsIncBtw></prijsIncBtw> <!-- met taxes -->
        </Product>

    </products>
    <Belasting>
        <BTW-nummer></BTW-nummer>
        <prijsExBtw></prijsExBtw> <!-- zonder taxes -->
        <prijsIncBtw></prijsIncBtw> <!-- met taxes -->
    </Belasting>
    <Betaalinstructies>
        <bankgegevens>
            <bankrekeningnummer></bankrekeningnummer>
            <IBAN></IBAN>
            <BIC></BIC>
        </bankgegevens>
        <Betalingswijze>

        </Betalingswijze>
    </Betaalinstructies>
    <opmerkingen></opmerkingen>
    <instructies></instructies>
    <Bijlagen>
        <!-- ... -->
    </Bijlagen>
</factuur>
</root>"""

# Connect to a local RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()

# Create a queue named 'xml_queue'
channel.queue_declare(queue='xml_queue')

# Publish the XML content to the queue
channel.basic_publish(exchange='',
                      routing_key='xml_queue',
                      body=xml_content.encode('utf-16'))

print(" [x] Sent XML content")
connection.close()
