import os
import sys
import requests
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class mzitu():
    def __init__(self, driver):
        self.driver = driver
        # get User-Agent info from chrome://version/
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
        self.urlHome = "http://www.mzitu.com/"
        self.modules = ["zipai", "jiepai"]
        self.dirHome = os.getcwd()

    def __makeDir(self, path):
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)

    def __saveImage(self, imgHref, imgName):
        try:
            img = requests.get(imgHref, headers=self.headers)
            f = open(imgName, 'wb')
            f.write(img.content)
            f.close()
        except:
            print("saved image failed %s" %(imgHref))

    def __saveImages(self, imgHrefList):
        def saveThread(imgHrefList, fileList):
            for imgHref in imgHrefList:
                imgName = imgHref[imgHref.rfind('/')+1:] # *.jpg
                if imgName not in fileList:
                    self.__saveImage(imgHref, imgName)

        threadList = []
        fileList = os.listdir('.')
        hrefThreadSize = int(len(imgHrefList)/4)
        thread1 = threading.Thread(target=saveThread, args=(imgHrefList[0*hrefThreadSize:1*hrefThreadSize], fileList))
        thread2 = threading.Thread(target=saveThread, args=(imgHrefList[1*hrefThreadSize:2*hrefThreadSize], fileList))
        thread3 = threading.Thread(target=saveThread, args=(imgHrefList[2*hrefThreadSize:3*hrefThreadSize], fileList))
        thread4 = threading.Thread(target=saveThread, args=(imgHrefList[3*hrefThreadSize:], fileList))
        threadList.append(thread1)
        threadList.append(thread2)
        threadList.append(thread3)
        threadList.append(thread4)

        for thread in threadList:
            thread.start()

        for thread in threadList:
            thread.join()

    def downloadImages(self, pages):
        os.chdir(self.dirHome)

        savedDirRoot = "images"
        self.__makeDir(savedDirRoot)
        os.chdir(savedDirRoot)

        for module in self.modules:
            self.__makeDir(module)
            os.chdir(module)

            imgHrefList = []
            countBefore = len(os.listdir('.'))

            urlModule = self.urlHome + module
            self.driver.get(urlModule)
            pageLatestElem = self.driver.find_element_by_xpath("//div[@class='pagenavi-cm']/span[@aria-current='page']")
            pageLatest = int(pageLatestElem.text) # 453
            for page in range(pages):
                urlPage = urlModule + '/comment-page-' + str(pageLatest - page) + '/#comments'
                self.driver.get(urlPage)
                imgElemList = self.driver.find_elements_by_xpath("//div[@class='comment-body']/p/img")
                for imgElem in imgElemList:
                    imgHref = imgElem.get_attribute('data-original')
                    imgHrefList.append(imgHref)
            self.__saveImages(imgHrefList)

            countAfter = len(os.listdir('.'))
            print("saved %d images in dir:%s" %(countAfter-countBefore, module))
            os.chdir("..")


# python main.py 2
if __name__ == '__main__':

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('log-level=3')
    driverPath = r'C:\softPackage\chromedriver_win32\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driverPath, options=options)

    pages = int(sys.argv[1])
    mzitu = mzitu.mzitu(driver)
    mzitu.downloadImages(pages)

    driver.quit()
