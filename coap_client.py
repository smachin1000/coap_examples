import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address

class TemperatureClient():
    """
    Sample client program to read the value "temperature"
    from the CoAP temperature server.
    """
    def __init__(self, ip_addr):
        self._ip_addr = ip_addr
        # The reactor is Twisted's main event loop
        # Request that requestReource is called 1 second
        # from now
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        # Create a non confirmable CoAP request.  To keep as
        # simple as possible we don't specity any observer
        # callbacks either.
        request = coap.Message(code=coap.GET, mtype=coap.NON)
        request.opt.uri_path = ('temperature',)
        # COAP_PORT is 5683, the default UDP port for CoAP
        request.remote = (ip_address(self._ip_addr), coap.COAP_PORT)
        d = protocol.request(request)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

    def printResponse(self, response):
        print 'CoAP result: ' + response.payload

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure

if __name__ == '__main__':
    if len(sys.argv) == 2:
        addr = sys.argv[1]
    else:
        print 'Usage : %s <IP address>' % sys.argv[0]
        sys.exit(1)

    log.startLogging(sys.stdout)

    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = TemperatureClient(addr)

    reactor.listenUDP(61616, protocol)
    # Run the Twisted event loop
    reactor.run()
