from convertAvailableElements import fromXML
from updateInx import updateInx
from xmotoExtensionTkinter import XmotoExtensionTkinter
import urllib2, bz2, md5
import logging, log

class refreshMenu(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)
        self.OptionParser.add_option("--xmlfile",   type="string", dest="xmlfile",   help="xml file")
        self.OptionParser.add_option("--urlbase",   type="string", dest="urlbase",   help="web site url")
        self.OptionParser.add_option("--connexion", type="string", dest="connexion", help="update method. (web, proxy, local)")
        self.OptionParser.add_option("--host",      type="string", dest="host",      help="proxy hostname")
        self.OptionParser.add_option("--port",      type="string", dest="port",      help="proxy port")
        self.OptionParser.add_option("--user",      type="string", dest="user",      help="proxy user")
        self.OptionParser.add_option("--password",  type="string", dest="password",  help="proxy password")
        self.OptionParser.add_option("--tab",       type="string", dest="tab",       help="selected tab")
        self.OptionParser.add_option("--dummy",     type="string", dest="dummy",     help="dummy")

    def urlopenread(self, url):
        """ urlopen with try/except
        """
        try:
            content = urllib2.urlopen(url).read()
        except urllib2.HTTPError, exc:
            log.writeMessageToUser("HTTP request failed with error code %d (%s)." % (exc.code, exc.msg))
            raise Exception("Error accessing to the url: %s" % url)
        except urllib2.URLError, exc:
            log.writeMessageToUser("URL error. Cause: %s." % exc.reason)
            raise Exception("Error accessing to the url: %s" % url)
        return content

    def getXmlFromTheWeb(self):
        # get local md5 sum
        try:
            localXmlFile = open(self.inkscapeDir + '/listAvailableElements.xml', 'rb')
            self.localXmlContent = localXmlFile.read()
            localMd5content = md5.new(self.localXmlContent).hexdigest()
            localXmlFile.close()
        except IOError, (errno, strerror):
            self.localXmlContent = ""
            localMd5content = ""

        # get web md5 sum
        url = self.options.urlbase
        url += 'listAvailableElements.xml.md5'
        webMd5content = self.urlopenread(url)

        if localMd5content != webMd5content:
            # if different, download new bz2 file
            url = self.options.urlbase
            url += 'listAvailableElements.xml.bz2'
            webBz2content = self.urlopenread(url)
            webContent = bz2.decompress(webBz2content)

            # update local xml file
            localXmlFile = open(self.inkscapeDir + '/listAvailableElements.xml', 'wb')
            localXmlFile.write(webContent)
            localXmlFile.close()

            self.localXmlContent = webContent
            self.update = True
        else:
            pass

    def effect(self):
        self.update = False
        self.inkscapeDir = self.getInkscapeExtensionsDir()

        # create the window showing what's going on

        # get the xml file
        self.connexion = self.options.connexion
        if self.connexion == 'Direct Connexion':
            self.getXmlFromTheWeb()

        elif self.connexion == 'Connexion through HTTP Proxy':
            proxy_info = {'host': self.options.host,
                          'port': self.options.port}
            if self.options.user not in [None, '', 'None']:
                proxy_info['user'] = self.options.user
                proxy_info['password'] = self.options.password

            proxy_support = urllib2.ProxyHandler({"http": "http://%(user)s:%(password)s@%(host)s:%(port)d" % proxy_info})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)
            self.getXmlFromTheWeb()

        elif self.connexion == 'Local file':
            if self.options.xmlfile in [None, '', 'None']:
                xmlFile = open(self.inkscapeDir + '/listAvailableElements.xml', 'rb')
            else:
                xmlFile = open(self.options.xml, 'rb')

            self.localXmlContent = xmlFile.read()
            xmlFile.close()

            self.update = True
        else:
            raise Exception('Bad connexion method: %s' % (str(self.connexion)))

        if self.update == True:
            # update the listAvailableElements.py file with the infos from the xml
            content = fromXML(self.localXmlContent)
            # update the listAvailableElements.py file
            f = open(self.inkscapeDir + '/listAvailableElements.py', 'wb')
            f.write(content)
            f.close()

            # update the inx files with the infos from the listAvailableElements.py file
            updateInx(content, self.inkscapeDir)

            infos = "Please restart Inkscape to update the X-Moto menus."
        else:
            infos = "Nothing new from the Internet. X-Moto menus not updated."

        log.writeMessageToUser(infos)

e = refreshMenu()
e.affect()
