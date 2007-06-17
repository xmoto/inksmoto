import logging, log
from convertAvailableElements import fromXML
from updateInx import updateInx
from xmotoExtensionTkinter import XmotoExtensionTkinter
from xmotoExtension import getInkscapeExtensionsDir
import bz2, md5
import urllib2


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

    def parse(self):
        pass
    def getposinlayer(self):
        pass
    def getselected(self):
        pass
    def output(self):
        pass
    def getdocids(self):
        pass

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
            logging.info('Local xml file found and md5 sum calculated.')
        except IOError, (errno, strerror):
            logging.info('No local xml file found.')
            self.localXmlContent = ""
            localMd5content = ""

        # get web md5 sum
        url = self.options.urlbase
        url += 'listAvailableElements.xml.md5'
        webMd5content = self.urlopenread(url)

        logging.info('Web md5 sum gotten.')

        if localMd5content != webMd5content:
            logging.info('MD5 sums differents. Downloading web bz2 file.')
            # if different, download new bz2 file
            url = self.options.urlbase
            url += 'listAvailableElements.xml.bz2'
            webBz2content = self.urlopenread(url)
            webContent = bz2.decompress(webBz2content)

            # update local xml file
            localXmlFile = open(self.inkscapeDir + '/listAvailableElements.xml', 'wb')
            localXmlFile.write(webContent)
            localXmlFile.close()

            logging.info('local xml file generated.')

            self.localXmlContent = webContent
            self.update = True
        else:
            logging.info('MD5 sums are the same. No updates done.')

    def effect(self):
        self.update = False
        self.inkscapeDir = getInkscapeExtensionsDir()

        # TODO::create the window showing what's going on

        # get the xml file
        self.connexion = self.options.connexion
        logging.info('Connexion method: %s' % self.connexion)
        if self.connexion == 'Direct Connexion':
            self.getXmlFromTheWeb()

        elif self.connexion == 'Connexion through HTTP Proxy':
            proxy_info = {'host': self.options.host,
                          'port': self.options.port}
            if self.options.user not in [None, '', 'None']:
                proxy_info['user'] = self.options.user
                proxy_info['password'] = self.options.password
                proxyDic = {"http": "http://%(user)s:%(password)s@%(host)s:%(port)s" % proxy_info}
                logging.info('proxydic: %s' % str(proxyDic))
            else:
                proxyDic = {"http": "http://%(host)s:%(port)s" % proxy_info}
                logging.info('proxydic: %s' % str(proxyDic))

	    try:
                proxy_support = urllib2.ProxyHandler(proxyDic)
            except urllib2.URLError, exc:
                log.writeMessageToUser("Error while creating proxy handler.. Cause: %s." % exc.reason)
                raise Exception("FATAL ERROR::can't create proxy handler")

	    try:
                opener = urllib2.build_opener(proxy_support)
            except Exception:
                log.writeMessageToUser('Error while creating proxy opener.')
                raise Exception("FATAL ERROR::can't create proxy opener")

	    try:
                urllib2.install_opener(opener)
            except Exception:
                log.writeMessageToUser('Error while installing proxy opener.')
                raise Exception("FATAL ERROR::can't install proxy opener")
	    
            self.getXmlFromTheWeb()

        elif self.connexion == 'Local file':
            if self.options.xmlfile in [None, '', 'None']:
                xmlFile = open(self.inkscapeDir + '/listAvailableElements.xml', 'rb')
            else:
                xmlFile = open(self.options.xmlfile, 'rb')

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

            logging.info('listAvailableElements.py file generated.')

            # update the inx files with the infos from the listAvailableElements.py file
            updateInx(content, self.inkscapeDir)

            logging.info('inx files generated.')

            infos = "Please restart Inkscape to update the X-Moto menus."
        else:
            infos = "Nothing new from the Internet. X-Moto menus not updated."

        log.writeMessageToUser(infos)

e = refreshMenu()
e.affect()
