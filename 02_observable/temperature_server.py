"""
This Coap server extends the work done in the previous example (see 02 directory), by making
the current temperature an observable resource.
"""

import sys

from twisted.internet import defer
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

import platform
import os
import random
import datetime


class TempResource(resource.CoAPResource):
    """
    Example CoAP server to return the current ambient temperature.

    This will the real value from the temperature sensor when running on the embedded board,
    otherwise a simulated value in degrees C.
    """

    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.addParam(resource.LinkParam('title', 'Temperature Resource'))

        # Additional metadata about a resource can be added using the addParam call.
        self.addParam(resource.LinkParam('units', 'degrees C'))

        # Allow discovery of this resource
        self.visible = True

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
        # If running on real hardware *my ARM server in this case), read from onboard temperature sensor
        # otherwise return a simulated value.
        if platform.machine() == 'armv5tejl':
            return float(os.popen("tshwctl --cputemp|grep external|cut -f2 -d'='").read().rstrip())
        else:
            return 30 + random.uniform(0, 5)


class ObservableTempResource(TempResource):
    """
    Example CoAP server that implements an observable resource (temperature).
    """
    def __init__(self):
        TempResource.__init__(self)
        self.visible = True
        self.observable = True
        self.notify()

    def notify(self):
        self.updatedState()
        # send a respone every second
        reactor.callLater(1, self.notify)


# Next class is needed to allow resource discovery.
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

    An example of how to discover the properties on a server using a CoAP client would be:

    python coap_client.py 192.168.1.100 .well-known/core
    """
    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    # noinspection PyUnusedLocal
    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        print payload
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']

        # note that nothing else needs to be done from here for the resources to be discovered;
        # the framework will take care of it.

        return defer.succeed(response)


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = resource.CoAPResource()

    # Define each resource here, creating the resource heirarchy
    well_known = resource.CoAPResource()
    root.putChild('.well-known', well_known)
    core = CoreResource(root)
    well_known.putChild('core', core)
    
    temperature_resouce = TempResource()
    root.putChild('temperature', temperature_resouce)

    observable_temperature_resouce = ObservableTempResource()
    root.putChild('observable_temperature', observable_temperature_resouce)


    endpoint = resource.Endpoint(root)

    # Listen on default CoAP port 5683
    reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint))

    # Run Twister'd event loop
    reactor.run()

