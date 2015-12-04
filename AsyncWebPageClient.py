#-*-coding: utf-8 -*-
__author__ = "eprivalov"
import threading
import urllib#, urllib2
#import time
from Queue import Queue


class AsyncWebPageClient(object):

    THREADS = 10
    # URL_COLLECTION = ()
    RESULT = []

    def __init__(self, *args, **kwargs):
        """
        Main constructor of the class.
        :param args:
        :param kwargs:
        :return:
        """
        self.Queue = Queue()
        if "threads" in kwargs:
            self.threads = kwargs["threads"]
        else:
            self.threads = self.THREADS

        for _ in xrange(self.threads):
            thread_ = threading.Thread(target=self.get_page_content)
            thread_.setDaemon(True)
            thread_.start()

    def get_page(self, url_collection):
        """
        Creates one dictionary or fills list :param self.RESULT: by the
        information about each url.
        If length of input collection of urls is greater than 1, list
        will be filled of nested dictionaries with style
        {'status_code': <status code>, 'url': <url>, 'content': <content>}
        If length equal 1, will be returned only one dictionary:
        {'status_code': -1, 'err': <error object>, 'url': <url>}
        If collection is empty will be raised IOError and
        message with offering to enter at least one value.
        :param url_collection:
        :return:
        """
        current_queue = Queue()
        for url in url_collection:
            self.Queue.put((url, current_queue))
        collection_length = len(url_collection)
        if collection_length > 1:
            for item in range(collection_length):
                status, url, content = current_queue.get()
                if status == 200:
                    self.RESULT.append(dict(status_code=status, url=url, content=content))
                else:
                    self.RESULT.append(dict(status_code=-1, url=url, err=content))
        elif collection_length == 1:
            status, url, content = current_queue.get()
            return dict(status_code=-1, url=url, err=content)
        else:
            raise IOError, "Colection of urls is empty, please, enter it with at least one item."
        return self.RESULT


    def get_page_content(self):
        """
        Push information of web-pages: status, url and content or code-error(if
        can not connect to the page) to Queue which will used to
        take data of each url and append to list.
        :return:
        """
        while True:
            url, Queue = self.Queue.get()
            try:
                page = urllib.urlopen(url)
                if page.getcode() == 200:
                    Queue.put((200, url, page.read()))
                    page.close()
                else:
                    Queue.put(('-1', url, page.getcode()))
                    page.close()
            except BaseException, e:
                Queue.put(('err', url, e))
                try: page.close()
                except: pass


#url_collection = ('http://statuspage1.nic.ru/',
#                  'http://google.com/'
 #                 )
#url_collection=()
#print "RESULT: ", AsyncWebPageClient(threads=10).get_page(url_collection)

