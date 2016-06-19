import sys

from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address


class CoapClient:
    """
    Sample general purpose CoAP client that performs a GET to the specified IP address and path.

    Example:
        python coap_client 127.0.0.1 temperatures
    """
    def __init__(self, ip_addr, url):
        self._ip_addr = ip_addr
        self._url = url
        # The reactor is Twisted's main event loop
        # Request that requestReource is called 1 second from now
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        # Create a non confirmable CoAP request.  To keep as
        # simple as possible we don't specify any observer
        # callbacks either.
        request = coap.Message(code=coap.GET, mtype=coap.NON)
        url_tokens = self._url.split('/')
        request.opt.uri_path = tuple(url_tokens)

        # COAP_PORT is 5683, the default UDP port for CoAP
        request.remote = (ip_address(self._ip_addr), coap.COAP_PORT)
        d = protocol.request(request)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

    @staticmethod
    def printResponse(response):
        print 'CoAP result: ' + response.payload

    @staticmethod
    def noResponse(failure):
        print 'Failed to fetch resource:%s' % failure

if __name__ == '__main__':
    if len(sys.argv) == 3:
        addr = sys.argv[1]
        url = sys.argv[2]
    else:
        print 'Usage : %s <IP address> <url>' % sys.argv[0]
        print 'The url argument should not start with a "/", but use'
        print '"/" characters to separate later portions'
        sys.exit(1)

    log.startLogging(sys.stdout)

    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = CoapClient(addr, url)

    reactor.listenUDP(61616, protocol)

    # Run the Twisted event loop
    reactor.run()
