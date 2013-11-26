import base64
import httplib
from pprint import pformat
from zope.interface import implements
from twisted.python.log import err
from twisted.web.client import Agent
from twisted.internet import ssl,reactor
from twisted.internet import defer
from collections import namedtuple
from twisted.web.client import getPage
from twisted.internet.protocol import Protocol
from twisted.internet.defer import succeed
from twisted.internet.defer import Deferred
from twisted.internet.ssl import ClientContextFactory
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.web.client import FileBodyProducer

from StringIO import StringIO

class WebClientContextFactory(ClientContextFactory):
    def __init__(self):
        self._options = ssl.CertificateOptions()

    def getContext(self, hostname, port):
        return self._options.getContext()
        
     
_MAX_PERSISTENT_PER_HOST = 200
_CACHED_CONNECTION_TIMEOUT = 24000
_CONNECT_TIMEOUT = 25000



class iloInterface:
   def __init__(self):
     global conn_detail
     print ("in ilointerface method")
     conn_detail = ConnectionInfo(
            '10.100.71.26',
            'basic',
            'hcladmin',
            'hcladmin',
            'https',
            443,
            'Keep-Alive',
            'none',
            '10.100.71.26',)
def xml():
    '''boilerplate xml body to send to the netapp filer'''
    return (
       '<?xml version=\"1.0\"?>'
        '<RIBCL VERSION=\"2.21\">'
        '<LOGIN USER_LOGIN=\"hcladmin\" PASSWORD=\"hcladmin\">'
        '<SERVER_INFO MODE=\"read\">'
        '<GET_EMBEDDED_HEALTH/>'
        '</SERVER_INFO>'
        '</LOGIN>'
        '</RIBCL>'
    )

ConnectionInfo = namedtuple(
    'ConnectionInfo',
        ['hostname',
        'auth_type',
        'username',
        'password',
        'scheme',
        'port',
        'connectiontype',
        'keytab',
        'dcip'])
        
class BeginningPrinter(Protocol):
    def __init__(self, finished):
        self.finished = finished
        #self.remaining = 1024
        self.data = []
        
    def dataReceived(self, bytes):
          self.data.append(bytes)

        # if self.remaining:
            # display = bytes[:self.remaining]
            # print 'Some data received:'
            # print display
            # self.remaining -= len(display)
          print self.data

    def connectionLost(self, reason):
        print 'Finished receiving body:', reason.getErrorMessage()
        #self.finished.callback(None)
        self.finished.callback("".join(self.data))
        
def display(response):
    print "Received response"
    print response.version
    print 'Response phrase:', response.phrase
    print pformat(list(response.headers.getAllRawHeaders()))
    # if response.code == httplib.UNAUTHORIZED:
       # print("Authorization Failed")
    # else:
       # print("Authorization Passed")
    # print 'Response headers:'
    print pformat(list(response.headers.getAllRawHeaders()))
    finished = Deferred()
    response.deliverBody(BeginningPrinter(finished))
    print 'done'
    return finished

    
def err(failure):
    print (failure.value.reasons[0].printTraceback())
    
def getHeaders():
    CONTENT_TYPE = {'Content-Type': ['application/xml']}  
    _headers = Headers(CONTENT_TYPE)
    _headers.addRawHeader('Authorization', _get_basic_auth_header())
    print('header',_headers)
    return _headers
   
class StringProducer(object):
    implements(IBodyProducer)
    """
    The length attribute must be a non-negative integer or the constant
    twisted.web.iweb.UNKNOWN_LENGTH. If the length is known, it will be used to
    specify the value for the Content-Length header in the request. If the
    length is unknown the attribute should be set to UNKNOWN_LENGTH. Since more
    servers support Content-Length, if a length can be provided it should be.
    """

    def __init__(self, body):
        self.body = body
        self.length = len(body)
        

    def startProducing(self, consumer):
        """
        This method is used to associate a consumer with the producer. It
        should return a Deferred which fires when all data has been produced.
        """
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

        
def _get_basic_auth_header():
    authstr = "{0}:{1}".format("hcladmin", "hcladmin")
    print (conn_detail.username)
    print (conn_detail.password)
    return 'Basic {0}'.format(base64.encodestring(authstr).strip())

def main():
     contextFactory = WebClientContextFactory()
     #contextFactory = ssl.CertificateOptions()
     # from twisted.web.client import HTTPConnectionPool
     # pool = HTTPConnectionPool(reactor, persistent=True)
     # pool.maxPersistentPerHost = _MAX_PERSISTENT_PER_HOST
     # pool.cachedConnectionTimeout = _CACHED_CONNECTION_TIMEOUT
     agent = Agent(reactor, contextFactory)
     body = FileBodyProducer(StringIO(xml()))
     #body = StringProducer(xml())
     headers=getHeaders()
     d= agent.request("GET", "https://10.100.71.26",headers,body)
     d.addCallbacks(display,err)
     d.addCallbacks(lambda ignored: reactor.stop())
     reactor.run()

if __name__ == "__main__":
     iloInterface()
     main()