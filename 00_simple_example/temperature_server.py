import sys

from twisted.internet import defer
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

import platform
import os
import random


class TempResource(resource.CoAPResource):
    """
    Example CoAP server to return the current ambient temperature.
    No 01_discovery or any other advanced features are supported in
    this example.
    """

    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.addParam(resource.LinkParam("title", "Temperature resource"))

        # Disable 01_discovery for now, we'll cover that next
        # self.visible = True

    # noinspection PyUnusedLocal
    def render_GET(self, request):
        temp = self._get_temperature()
        response = coap.Message(code=coap.CONTENT, payload='%.1f' % temp)

        return defer.succeed(response)

    @staticmethod
    def _get_temperature():
        """
        Temperature is obtained via the embedded board's tshwctl utility, it outputs both
        CPU & ambient temperature in this format:
        
        external_temp=32.1648
        internal_temp=62.985

        this function returns the ambient temperature as a float.
        """

        # If running on real hardware, read from onboard temperature sensor
        # otherwise return a simulated value.
        if platform.machine() == 'armv5tejl':
            return float(os.popen("tshwctl --cputemp|grep external|cut -f2 -d'='").read().rstrip())
        else:
            return 30 + random.uniform(0, 5)

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
