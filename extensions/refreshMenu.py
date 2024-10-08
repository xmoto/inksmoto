#!/usr/bin/python
"""
Copyright (C) 2006,2009 Emmanuel Gorse, e.gorse@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from inksmoto import log
import logging
from inksmoto.xmotoExtension import XmExt
from inksmoto.convertAvailableElements import fromXML
from inksmoto.xmotoTools import getHomeDir
from inksmoto.xmotoTools import getExistingImageFullPath, createDirsOfFile
from os.path import join, basename, isdir
import bz2, md5
import urllib.request, urllib.error, urllib.parse
import glob, os

class RefreshMenu(XmExt):
    def __init__(self):
        XmExt.__init__(self)
        self.OptionParser.add_option("--tab", type="string",
                                     dest="tab", help="tab")
        self.OptionParser.add_option("--xmlfile", type="string",
                                     dest="xmlfile", help="xml file")
        self.OptionParser.add_option("--urlbase", type="string",
                                     dest="urlbase", help="web site url")
        self.OptionParser.add_option("--connexion", type="string",
                                     dest="connexion",
                                     help="update method. (web, proxy, local)")
        self.OptionParser.add_option("--host", type="string",
                                     dest="host", help="proxy hostname")
        self.OptionParser.add_option("--port", type="string",
                                     dest="port", help="proxy port")
        self.OptionParser.add_option("--user", type="string",
                                     dest="user", help="proxy user")
        self.OptionParser.add_option("--password", type="string",
                                     dest="password", help="proxy password")

    def urlopenread(self, url):
        """ urlopen with try/except
        """
        try:
            content = urllib.request.urlopen(url).read()
        except urllib.error.HTTPError as exc:
            log.outMsg("HTTP request failed with error code %d (%s)."
                       % (exc.code, exc.msg))
            raise Exception("Error accessing to the url: %s" % url)
        except urllib.error.URLError as exc:
            log.outMsg("URL error. Cause: %s." % exc.reason)
            raise Exception("Error accessing to the url: %s" % url)
        return content

    def getXmlFromTheWeb(self):
        localXmlFilename = join(getHomeDir(), 'inksmoto', 'listAvailableElements.xml')
        # get local md5 sum
        try:
            localXmlFile = open(localXmlFilename, 'rb')
            self.localXmlContent = localXmlFile.read()
            localMd5content = md5.new(self.localXmlContent).hexdigest()
            localXmlFile.close()
            logging.info('Local xml file found and md5 sum calculated.')
        except IOError as xxx_todo_changeme:
            (errno, strerror) = xxx_todo_changeme.args
            logging.info('No local xml file found.\n%d-%s' % (errno, strerror))
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
            localXmlFile = open(localXmlFilename, 'wb')
            localXmlFile.write(webContent)
            localXmlFile.close()

            logging.info('local xml file generated.')

            self.localXmlContent = webContent
            self.update = True
        else:
            logging.info('MD5 sums are the same. No updates done.')

    def effectHook(self):
        self.update = False

        # TODO::create the window showing what's going on

        #logging.info("self.options=[%s]" % str(self.options))

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
                proxyDic = {"http":
                                "http://%(user)s:%(password)s@%(host)s:%(port)s"
                            % proxy_info}
                logging.info('proxydic: %s' % str(proxyDic))
            else:
                proxyDic = {"http": "http://%(host)s:%(port)s" % proxy_info}
                logging.info('proxydic: %s' % str(proxyDic))

            try:
                proxy_support = urllib.request.ProxyHandler(proxyDic)
            except urllib.error.URLError as exc:
                log.outMsg("Error while creating proxy handler.. Cause: %s."
                           % exc.reason)
                raise Exception("FATAL ERROR::can't create proxy handler")

            try:
                opener = urllib.request.build_opener(proxy_support)
            except Exception as e:
                log.outMsg('Error while creating proxy opener.\n%s' % e)
                raise Exception("FATAL ERROR::can't create proxy opener")

            try:
                urllib.request.install_opener(opener)
            except Exception as e:
                log.outMsg('Error while installing proxy opener.\n%s' % e)
                raise Exception("FATAL ERROR::can't install proxy opener")
	    
            self.getXmlFromTheWeb()

        elif self.connexion == 'local':
            if self.options.xmlfile in [None, '', 'None']:
                filename = join(getHomeDir(), 'inksmoto', 'listAvailableElements.xml')
                xmlFile = open(filename, 'rb')
            else:
                xmlFile = open(self.options.xmlfile, 'rb')

            self.localXmlContent = xmlFile.read()
            xmlFile.close()

            self.update = True
        else:
            raise Exception('Bad connexion method: %s' % (str(self.connexion)))

        if self.update == True:
            # update the listAvailableElements.py file with the infos
            # from the xml
            try:
                content = fromXML(self.localXmlContent)
            except Exception as e:
                log.outMsg("Error parsing the xml file.\n%s" % str(e))
                return False

            # update the listAvailableElements.py file
            filename = join(getHomeDir(), 'inksmoto', 'listAvailableElements.py')
            f = open(filename, 'wb')
            f.write(content)
            f.close()

            logging.info('listAvailableElements.py file generated.')

            infos = "X-Moto textures/sprites list updated."
        else:
            infos = "Nothing new from the Internet.\n\
X-Moto textures/sprites list not updated."

        # always download missing images
        missingFiles = self.getMissingImages()
        numFilesDownloaded = 0
        if self.connexion == 'local':
            if len(missingFiles) != 0:
                logging.info("missing local images: [%s]" % str(missingFiles))
        else:
            numFilesDownloaded = self.downloadMissingImages(missingFiles)
            infos += "\n%d new images downloaded." % numFilesDownloaded

        log.outMsg(infos)

        return False

    def getMissingImages(self):
        """ we have to remove listAvailableElements from the already
            loaded modules to load the newly generated one """
        from inksmoto.availableElements import AvailableElements
        AvailableElements().load()
        
        SPRITES = AvailableElements()['SPRITES']
        TEXTURES = AvailableElements()['TEXTURES']
        EDGETEXTURES = AvailableElements()['EDGETEXTURES']

        missingImagesFiles = []

        for images in [SPRITES, TEXTURES, EDGETEXTURES]:
            for properties in list(images.values()):
                if 'file' not in properties:
                    continue
                imageFile = properties['file']
                if getExistingImageFullPath(imageFile) is None:
                    missingImagesFiles.append(imageFile)

        return missingImagesFiles

    def downloadMissingImages(self, missingFiles):
        if len(missingFiles) == 0:
            logging.info("No new images to download")
            return 0

        logging.info("images to download: [%s]" % str(missingFiles))

        fileDownloaded = 0
        for _file in missingFiles:
            fileDownloaded += self.downloadOneFile('xmoto_bitmap/' + _file,
                                                   join('xmoto_bitmap', _file))

        return fileDownloaded

    def downloadOneFile(self, distantFile, localFile):
        # get distant file
        url = self.options.urlbase
        url += distantFile
        try:
            webContent = self.urlopenread(url)
        except Exception as e:
            logging.info("Can't download file [%s].\nCheck your connection.\n%s"
                         % (url, e))
            return 0

        filename = join(getHomeDir(), 'inksmoto', localFile)
        # get dirname and create it if it doesnt exists
        createDirsOfFile(filename)
            
        try:
            localFileHandle = open(filename, 'wb')
            localFileHandle.write(webContent)
            localFileHandle.close()
        except Exception as e:
            logging.info("Can't create local file [%s].\n%s" % (filename, e))
            return 0

        logging.info("File [%s] downloaded in [%s]" % (url, filename))
        return 1

def run():
    ext = RefreshMenu()
    ext.affect()
    return ext

if __name__ == "__main__":
    run()
