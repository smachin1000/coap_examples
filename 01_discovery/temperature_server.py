import sys
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
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
    """

    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.addParam(resource.LinkParam("title", "Temperature resource"))

        # Allow 01_discovery of this resource
        self.visible = True

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
        if platform.platform == 'xxxx':
            return float(os.popen("tshwctl --cputemp|grep external|cut -f2 -d'='").read().rstrip())
        else:
            return 30 + random.random()

# Next class is needed to allow 01_discovery.
class CoreResource(resource.CoAPResource):
    """
    Example Resource that provides list of links hosted by a server.
    Normally it should be hosted at /.well-known/core

    Resource should be initialized with "root" resource, which can be used
    to generate the list of links.

    For the response, an option "Content-Format" is set to value 40,
    meaning "application/link-format". Without it most clients won't
    be able to automatically interpret the link format.

    Notice that self.visible is not set - that means that resource won't
    be listed in the link format it hosts.
    """

    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        print payload
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = resource.CoAPResource()

    well_known = resource.CoAPResource()
    root.putChild('.well-known', well_known)
    core = CoreResource(root)
    well_known.putChild('core', core)
    
    temperature_resouce = TempResource()
    root.putChild('temperature', temperature_resouce)

    endpoint = resource.Endpoint(root)

    # Listen on default CoAP port 5683
    reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))

    # Run Twister'd event loop
    reactor.run()
