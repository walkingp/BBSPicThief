from urllib.request import urlopen
import re,urllib,os,threading,sys,time
import html.parser,logging

#Config class
class Config:
    saveAsPath='pics/'
    minPicSize=10*1024
    timeout=10
    
#Utility
class Utility:
    class NetHelper:
        #get request content
        def GetContent(self,url,encode):
            try:                
                f=urlopen('http://' + Utility.StringHelper().GetHost(url),timeout=Config.timeout)
                code=f.getcode()
                if(code<200 or code >=300):
                    pass
                return f.read().decode(encode)
            except:
                print('>>>Error',url)
                print(sys.exc_info())
        #download web picture
        def DownloadPic(url):
            picName=url.split('/')[-1]
            if url[0:4]=='http':
                localFile=Config.saveAsPath + '%s'%(picName)
                try:
                    urllib.request.urlretrieve(pic,localFile)
                    if os.path.getsize(localFile)<Config.minPicSize:
                        os.remove(localFile)
                except:
                    print('Error:',url)
    class RegularExpHelper:
        #Get regular expression matched result
        def Matches(self,reg,content):
            matches = re.findall(re.compile(reg),content)
            return matches
        #Replace strings using regular expression
        def Replace(self,reg,newValue,content):
            return re.sub(reg,newValue,content)
    class StringHelper:
        #Get Html unescape result
        def Format(self,s):
            return html.parser.HTMLParser().unescape(s)
        def FormatFilePathName(self,s):
            return Utility.RegularExpHelper().Replace(r'[:/\\\*\?\|]','', s)
        def GetHost(self,url):
            return re.findall(r'http://(.+?)/',url)[0]
       
#Interface
class IDownload: 
    def __init__(self):
        pass
    
    def __init__(self,_encode='utf-8',_pageSize=10):
        self.setEncode(_encode)
        self.setPageSize(_pageSize)

    #setter and getter
    def setEncode(self,encode):
        self.encode=encode
    def getEncode(self):
        return self.encode
    def setPageSize(self,pageSize):
        self.pageSize=pageSize
    def getPageSize(self):
        return self.pageSize
    def setUrl(self,url):
        self.url=url
    def getUrl(self):
        return self.url
    def setPagesLinkRegExp(self,pagesLinkRegExp):
        self.pagesLinkRegExp=pagesLinkRegExp
    def getPagesLinkRegExp(self):
        return self.pagesLinkRegExp
    def setImagesRegExp(self,imagesRegExp):
        self.imagesRegExp=imagesRegExp
    def getImagesRegExp(self):
        return self.imagesRegExp
    
    def __GenerateNewUrl(self,url,page):
        return url + str(page)

    def __SplitPage(self,content):
        urlList=Utility.RegularExpHelper().Matches(self.getPagesLinkRegExp(),content)
        return urlList

    def __SavePics(self,url,title):
        global path
        content=Utility.NetHelper().GetContent(url,self.encode)
        picList=Utility.RegularExpHelper().Matches(self.imagesRegExp,content)
        t=[Config.saveAsPath ,Utility.StringHelper().GetHost(url), title]
        path='%s%s/%s/' % tuple(t)
        #create new path if not existed
        if os.path.exists(path)==False:
            os.makedirs(path)
        #download all pictures
        for pic in picList:
            self.__SavePicIntoFile(pic,title)
        #remove empty path                   
        if(len(os.listdir(path))==0):
            os.removedirs(path)
         
    def __SavePicIntoFile(self,picUrl,title):
        picUrl=picUrl.split('?')[0]#Avoid syntax of ?
        picName=picUrl.split('/')[-1]
        if picUrl[0:4]=='http':
            localFile=path + '%s' % (picName)
            try:
                urllib.request.urlretrieve(picUrl,localFile)                
                print('>>Downloaded:',picUrl)
                #Delete pictures whose size is too small
                if os.path.getsize(localFile)<Config.minPicSize:
                    os.remove(localFile)
                    print('>>Deleted:',picUrl)
            except:
                print('>>>>>Error:',picUrl)
                print(sys.exc_info())
                logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'))
                log=logging.getLogger('BBSPicThief')
                log.setLevel(logging.WARN)
                log.warning(picUrl + '|' + localFile + '|' + sys.exc_info())
                
    def Start(self):
        threads=[]
        global mutex,logger
        mutex=threading.Lock()
        for page in range(1,self.pageSize+1):            
            threads.append(threading.Thread(target=self.__DownloadThread,args=(page,)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()                           
    
    def __DownloadThread(self,pageIndex):        
        newUrl=self.__GenerateNewUrl(self.url,pageIndex)        
        content=Utility.NetHelper().GetContent(newUrl,self.encode)
        matches=self.__SplitPage(content)
        for m in matches:
            mutex.acquire()
            self.__SavePics(m[0],Utility.StringHelper().FormatFilePathName(Utility.StringHelper().Format(m[1])))
            mutex.release()
   
class CnblogsDownload(IDownload):
    def __init__(self):
        IDownload.__init__(self)
        IDownload.setUrl(self,'http://www.cnblogs.com/p')
        IDownload.setPagesLinkRegExp(self,r'<h3><a.*?href="(.*?)".*?>(.*?)</a></h3>')
        IDownload.setImagesRegExp(self,r'<img.*src="(.*?)".*/>')
    def Start(self):
        IDownload.Start(self)

#it doesn't work on CSDN cause of permission
class CSDNDownload(IDownload):
    def __init__(self):
        IDownload.__init__(self)
        IDownload.setUrl(self,'http://blog.csdn.net/?page=')
        IDownload.setPagesLinkRegExp(self,r'<a name=".*?" href="(.*?)" target="_blank">(.*?)</a>')
        IDownload.setImagesRegExp(self,r'<img.*src="(.*?)".*?>')
    def Start(self):
        IDownload.Start(self)

if __name__=='__main__':    
    cnblogs=CnblogsDownload()
    cnblogs.Start()
        
                
