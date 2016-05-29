# coap_examples
Sample Python client and server using the COaP protocol.

# Install
We use the txThings Python library from https://github.com/mwasilak/txThings.
To install this library, git clone https://github.com/mwasilak/txThings.git then run python setup.py install.
This code has been tested with version 3ad1e3aa493baaedf21b553513684919d82acd09 of the library.

# Running
On one machine run the server with "python temperature_server.py".  On another, run the client to read from the server with "python temperature_client.py <ip_addr>" where ip_addr is the IP address of the server.

Sample successful output is:

    2016-05-29 14:37:12-0700 [-] Log opened.
    2016-05-29 14:37:12-0700 [-] Coap starting on 61616
    2016-05-29 14:37:12-0700 [-] Starting protocol <txthings.coap.Coap instance at 0
x02E57A58>
    2016-05-29 14:37:13-0700 [-] Sending message to 192.168.1.100:5683
    2016-05-29 14:37:13-0700 [-] Message 'T\x01\x89\xa8\x00\x00\x0b\xec\xbbtemperatu
re' sent successfully
    2016-05-29 14:37:13-0700 [-] Sending request - Token: 00000bec, Host: 192.168.1.
100, Port: 5683
    2016-05-29 14:37:13-0700 [Coap (UDP)] Received 'TEW\xf0\x00\x00\x0b\xec\xff36.3'
 from 192.168.1.100:5683
    2016-05-29 14:37:13-0700 [Coap (UDP)] Incoming Message ID: 22512
    2016-05-29 14:37:13-0700 [Coap (UDP)] New unique CON or NON message received
    2016-05-29 14:37:13-0700 [Coap (UDP)] Received Response, token: 00000bec, host:
192.168.1.100, port: 5683
    2016-05-29 14:37:13-0700 [-] CoAP result: 36.3
