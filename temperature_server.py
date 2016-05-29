import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

import os


class TempResource(resource.CoAPResource):
    """
    Example CoAP server to return the current ambient temperature.
    """

    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.addParam(resource.LinkParam("title", "Temperature resource"))

    def render_GET(self, request):
        temp = self._get_temperature()
        response = coap.Message(code=coap.CONTENT, payload='%.1f' % temp)

        return defer.succeed(response)

    def _get_temperature(self):
        """
        Temperature is obtained via the embedded board's tshwctl utility, it outputs both
        CPU & ambient temperature in this format:
        
        external_temp=32.1648
        internal_temp=62.985

        this function returns the ambient temperature as a float.
        """
        return float(os.popen("tshwctl --cputemp|grep external|cut -f2 -d'='").read().rstrip())

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = resource.CoAPResource()
    temperature_resouce = TempResource()
    root.putChild('temperature', temperature_resouce)

    endpoint = resource.Endpoint(root)

    # Listen on default CoAP port 5683
    reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))

    # Run Twister'd event loop
    reactor.run()
