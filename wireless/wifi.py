"""
.. _stdlib_wifi:

.. module:: wifi

****
WiFi
****

This module implements a generic wifi interface.
To function correctly it needs a wifi driver to be loaded, so that the module can use
the driver to access the underlying hardware.

The link between the wifi module and the wifi driver is established without the programmer
intervetion by the driver itself.


This module defines the following constants:

    * `WIFI_OPEN` = 0; Open Wifi network
    * `WIFI_WEP`  = 1; Wifi Network secured with WEP
    * `WIFI_WPA`  = 2; Wifi Network secured with WPA
    * `WIFI_WPA2`  = 3; Wifi Network secured with WPA2


    """

WIFI_OPEN = 0
WIFI_WEP = 1
WIFI_WPA = 2
WIFI_WPA2 = 3


def gethostbyname(hostname):
    """
.. function:: gethostbyname(hostname)        

        Translate a host name to IPv4 address format. The IPv4 address is returned as a string, such as "192.168.0.5". 
                
    """
    return __default_net["wifi"].gethostbyname(hostname)


def select(rlist,wlist,xlist,timeout=None):
    """
.. function:: select(rlist, wlist, xlist, timeout=None)

   This is equivalent to the Unix *select* system call.
   The first three arguments are sequences of socket instances.

   * *rlist*: wait until ready for reading
   * *wlist*: wait until ready for writing
   * *xlist*: wait for an "exceptional condition" (not supported by every wifi driver)

   Empty sequences are allowed. The optional *timeout* argument specifies a time-out as an integer number
   in milliseconds.  When the *timeout* argument is omitted the function blocks until
   at least one socket is ready.  A *timeout* value of zero specifies a
   poll and never blocks.

   The return value is a triple of lists of objects that are ready: subsets of the
   first three arguments.  When the time-out is reached without a socket
   becoming ready, three empty lists are returned.
       
    """
    rrlist = [x.fileno() for x in rlist]
    wwlist = [y.fileno() for y in wlist]
    xxlist = [z.fileno() for z in xlist]
    rl,wl,xl = __default_net["wifi"].select(rrlist,wwlist,xxlist,timeout)
    rr = [x for x in rlist if x.fileno() in rl]
    ww = [y for y in wlist if y.fileno() in wl]
    xx = [z for z in xlist if z.fileno() in xl]
    return (rr,ww,xx)


def scan(duration=5000):
    """
.. function:: scan(duration=5000)        

        Return the list of available wifi networks as a tuple of tuples: (SSID, network_security, RSSI, BSSID).

        The format of RSSI depends on the specific wifi driver loaded.

        *duration* is the maximum time in milliseconds the scan can last.
    """
    return __default_net["wifi"].scan(duration)
            
def link(ssid,security,password=""):
    """
.. function:: link(ssid,security,password="")        

        Try to establish a link with the Access Point handling the wifi network identified by *ssid*. *security* must be one
        of the WIFI_ constants, and *password* is needed if *security* is different from WIFI_OPEN

        An exception can be raised if the link is not successful.

    """
    __default_net["wifi"].link(ssid,security,password)

def try_link(ssid,password,sec=WIFI_WPA2, attempts=5,delay=2000):
    """
.. function:: try_link(ssid,password,sec=WIFI_WPA2, attempts=5,delay=2000)        

        Try to establish a link for with the Access Point handling the wifi network identified by *ssid*. *security* must be one
        of the WIFI_ constants, and *password* is needed if *security* is different from WIFI_OPEN
        
        The driver will try to link through a number of *attepmts*, each attempt with a *delay* delay in ms.
        An exception can be raised if the link is not successful.

    """
    exc = None
    for _ in range(attempts):
        try:
            __default_net["wifi"].link(ssid, sec, password)
            break
        except Exception as e:
            exc = e
            sleep(delay)
    else:
        raise exc

def unlink():
    """
.. function:: unlink()        

        Disconnect from the currently linked wifi network.

    """ 
    __default_net["wifi"].unlink()

def rssi():
    """
.. function:: get_rssi()        

        Return RSSI of the current wireless connection.

    """ 
    return __default_net["wifi"].get_rssi()

def is_linked():
    """
.. function:: is_linked()        

        Return True if linked to the Access Point

    """ 
    return __default_net["wifi"].is_linked()


def set_link_info(ip,mask,gw,dns):
    """
.. function:: set_link_info(ip,mask,gw,dns)        

        Set desired wifi interface parameters:

            * ip, the static ipv4 address
            * mask, the network mask
            * gw, the default gateway
            * dns, the default dns

        If 0.0.0.0 is given, a default address will be used.

    """        
    __default_net["wifi"].set_link_info(ip,mask,gw,dns)

def link_info():
    """
.. function:: link_info()        

        Return information on the currently established AP link.

        The result is a tuple where the elements are, in order:

            * The assigned IP as a string
            * The network mask as a string
            * The gateway IP as a string
            * The DNS IP as a string
            * The MAC address of the wifi interface as a sequence of 6 bytes

    """        
    return __default_net["wifi"].link_info()

def softap_init(ssid,sec,password="",max_conn=4):
    """
.. function:: softap_init(ssid,sec,password="",max_conn=4)        

        Try to activate the Access Point operating mode exposing a wifi network identified by *ssid*. *security* must be one
        of the WIFI_ constants, and *password* is needed if *security* is different from WIFI_OPEN; *max_conn* represents the maximum number of connections available (default is 4)

        An exception can be raised if the activation is not successful.

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].softap_init(ssid,sec,password,max_conn)

def softap_config(ip="192.168.0.1",gw="192.168.0.1",net="255.255.255.0"):
    """
.. function:: softap_config(ip="192.168.0.1",gw="192.168.0.1",net="255.255.255.0")

        Try to configure the Access Point setting the IP address, the Gateway address and the Netmask address.
        Default values are: "192.168.0.1" as IP address, "192.168.0.1" as Gateway address, "255.255.255.0" as Netmask address.

        An exception can be raised if the configuration is not successful.

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].softap_config(ip,gw,net)

def softap_get_info():
    """
.. function:: softap_get_info()

        Return information on the current devices connected to the Access Point.

        The result is a tuple where every element represents a device connected and includes:

            * The assigned IP as a string
            * The MAC address of the wifi interface as a sequence of 6 bytes

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].softap_get_info()

def softap_off():
    """
.. function:: softap_off()

        Try to turn off the Access Point operating mode.

        An exception can be raised if the Access Point disabling is not successful.

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].softap_off()

def station_on():
    """
.. function:: station_on()

        Try to turn on the Station operating mode.

        An exception can be raised if the Station enabling is not successful.

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].station_on()

def station_off():
    """
.. function:: station_off()

        Try to turn off the Station operating mode.

        An exception can be raised if the Station disabling is not successful.

.. note:: Not guaranteed to be supported by every wifi driver!

    """        
    return __default_net["wifi"].station_off()
