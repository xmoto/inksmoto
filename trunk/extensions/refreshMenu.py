import logging, log
from convertAvailableElements import fromXML
from xmotoExtensionTkinter import XmotoExtensionTkinter
from xmotoExtension import getInkscapeExtensionsDir
from os.path import join, exists
import bz2, md5
import urllib2


class refreshMenu(XmotoExtensionTkinter):
    def __init__(self):
        XmotoExtensionTkinter.__init__(self)
	self.OptionParser.add_option("--tab",       type="string", dest="tab",       help="tab")
        self.OptionParser.add_option("--xmlfile",   type="string", dest="xmlfile",   help="xml file")
        self.OptionParser.add_option("--urlbase",   type="string", dest="urlbase",   help="web site url")
        self.OptionParser.add_option("--connexion", type="string", dest="connexion", help="update method. (web, proxy, local)")
        self.OptionParser.add_option("--host",      type="string", dest="host",      help="proxy hostname")
        self.OptionParser.add_option("--port",      type="string", dest="port",      help="proxy port")
        self.OptionParser.add_option("--user",      type="string", dest="user",      help="proxy user")
        self.OptionParser.add_option("--password",  type="string", dest="password",  help="proxy password")

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
            filename = join(self.inkscapeDir, 'listAvailableElements.xml')
            localXmlFile = open(filename, 'wb')
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

        logging.info("self.options=[%s]" % str(self.options))

        # get the xml file
        self.connexion = self.options.connexion
        logging.info('Connexion method: %s' % self.connexion)
        if self.connexion == 'web':
            self.getXmlFromTheWeb()

        elif self.connexion == 'proxy':
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

        elif self.connexion == 'local':
            if self.options.xmlfile in [None, '', 'None']:
                filename = join(self.inkscapeDir, 'listAvailableElements.py')
                xmlFile = open(filename, 'rb')
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
            filename = join(self.inkscapeDir, 'listAvailableElements.py')
            f = open(filename, 'wb')
            f.write(content)
            f.close()

            logging.info('listAvailableElements.py file generated.')

            missingFiles = self.getMissingImages()
            numFilesDownloaded = 0
            if self.connexion == 'local':
                if len(missingFiles) != 0:
                    logging.info("missing local images: [%s]" % str(missingFiles))
            else:
                numFilesDownloaded = self.downloadMissingImages(missingFiles)

            infos = "X-Moto textures/sprites list updated.\n%d new images downloaded." % numFilesDownloaded
        else:
            infos = "Nothing new from the Internet.\nX-Moto textures/sprites list not updated."

        log.writeMessageToUser(infos)

    def getMissingImages(self):
        # we have to remove listAvailableElements from the already loaded modules
        # to load the newly generated one
        import sys
        if 'listAvailableElements' in sys.modules:
            del sys.modules['listAvailableElements']
        from listAvailableElements import sprites, textures, edgeTextures

        missingImagesFiles = []

        for images in [sprites, textures, edgeTextures]:
            for imageName, properties in images.iteritems():
                if 'file' not in properties:
                    continue
                imageFile = properties['file']
                if not exists(join(self.inkscapeDir, 'xmoto_bitmap', imageFile)):
                    missingImagesFiles.append(imageFile)

        return missingImagesFiles

    def downloadMissingImages(self, missingFiles):
        if len(missingFiles) == 0:
            logging.info("No new images to download")
            return 0

        logging.info("images to download: [%s]" % str(missingFiles))

        fileDownloaded = 0
        for file in missingFiles:
            fileDownloaded += self.downloadOneFile('xmoto_bitmap/' + file, join('xmoto_bitmap', file))

        return fileDownloaded

    def downloadOneFile(self, distantFile, localFile):
        # get distant file
        url = self.options.urlbase
        url += distantFile
        try:
            webContent = self.urlopenread(url)
        except:
            logging.info("Can't download file [%s].\nCheck your connection." % url)
            return 0

        # update local xml file
        filename = join(self.inkscapeDir, localFile)
        try:
            localFileHandle = open(filename, 'wb')
            localFileHandle.write(webContent)
            localFileHandle.close()
        except:
            logging.info("Can't create local file [%s]." % filename)
            return 0

        logging.info("File [%s] downloaded in [%s]" % (url, filename))
        return 1
        

e = refreshMenu()
e.affect()
