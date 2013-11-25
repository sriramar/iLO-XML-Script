if __name__ == '__main__':
    import ilo_query_modeler
    raise SystemExit(ilo_query_modeler.main())

import sys

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import ssl, reactor

def xml():
    '''XML body for iLO request'''
    return (
        '<?xml version=\"1.0\"?>'
        '<RIBCL VERSION=\"2.21\">'
        '<LOGIN USER_LOGIN=\"username\" PASSWORD=\"password\">'
        '<SERVER_INFO MODE=\"read\">'
        '<GET_EMBEDDED_HEALTH/>'
        '</SERVER_INFO>'
        '</LOGIN>'
        '</RIBCL>'
    )
class ILOClient(LineReceiver):
    end="/r/n"
    def connectionMade(self):
        self.sendLine(xml())
        self.sendLine(self.end)

    def connectionLost(self, reason):
        print 'connection lost (protocol)'

    def lineReceived(self, line):
        print "receive:", line

class ILOClientFactory(ClientFactory):
    protocol = ILOClient

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        reactor.stop()

def main():
    factory = ILOClientFactory()
    reactor.connectSSL('192.168.0.2', 443, factory, ssl.CertificateOptions())
    reactor.run()
