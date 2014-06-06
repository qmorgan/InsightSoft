#!/usr/bin/env python
# encoding: utf-8
"""
CharityScrape.py
Author: Adam N Morgan
"""
import os
import qScrape
from BeautifulSoup import BeautifulSoup
import pandas as pd
import glob
import time
import numpy as np
import requests
# 

# Hardcode this base path for now.
basepath = "/Users/amorgan/Documents/Insight/"



def _BBBLoop(idrange=(1,5)):
    # last bbb id is 40196
    # HUGE list of names of non profits. easy to get. few actually have profiles though.
    for bbbid in np.arange(idrange[0],idrange[1]):
        r = _BBBCheck(bbbid)
        time.sleep(0.1)
        with open(basepath + "BBB/index.txt", "a") as myfile:
            myfile.write(r.url.split('/')[-1])
        if "we do not have a current report" in r.content:
            print "No report for bbbid {}".format(bbbid)
        else:
            # download the file if they have a report
             
        

def _BBBCheck(bbbid):
    url = "http://www.bbb.org/charity-reviews/national/{}".format(bbbid)
    r=requests.get(url)
    return r

def _CNScrapeOther(CNdf,baselist=['history','history.detail'],idrange=(6,15),pause=0.5):
    '''This could actually be used to scrape summary as well but it was written
    later. Incorporate the _CNScrapeSummary into this if desired.'''
    
    import qMail
    
    acceptablebases = ['summary','history','history.detail','comments']
    subdf = CNdf.loc[idrange[0]:idrange[1]]
    
    # emailaddr=qMail.gmail_username+'@gmail.com'
    emailaddr="qmorgan@gmail.com"
    payload={'email':emailaddr,'password':'r0b0b00gie'}
    session = requests.session()
    r=session.get('https://www.charitynavigator.org/index.cfm?bay=my.login', params=payload)
    print "Pausing to log in"
    time.sleep(3)
    # loop around bases
    for base in baselist:
        if base not in acceptablebases:
            print "Need to specify base: ['summary','history','comments']"
            continue
        # loop around range
        for dfid, CNitem in subdf.iterrows():
            try:
                orgid=int(CNitem.CNid)
                downloadpath = basepath + 'CharityNavigator/raw/{}/{}{}.html'.format(base,base,orgid)
                if base == 'history.detail': 
                    downloadpath = downloadpath.replace('html','pdf') # this is a pdf file
                urlstr = 'http://www.charitynavigator.org/index.cfm?bay=search.{}&orgid={}'.format(base,orgid)
                r=session.get(urlstr)
                localfile = open(downloadpath,'wb')
                localfile.write(r.content)
                localfile.close()
                print "Wrote id {}: {}".format(dfid,downloadpath)
                timetopause = np.random.rand() + pause # add a randomized sleep time from 0 to 1 sec
                time.sleep(timetopause)
            except:
                errtext='Couldnt scrape dfid:{} (CNid:{})'.format(dfid,orgid)
                qErr.qErr(errtitle="A scraping error has occured!",errtext=errtext)
    # r.content
    r.close()
    
    time.sleep(timetopause)
    # 
    # local_file = open('test.pdf', "w" + 'b')
    # 
    # local_file.write(r.content)


def _CNGetList():
    '''Return dataframe of CharityNavigator indices'''
    searchpath = basepath + "/CharityNavigator/index_pages/"
    indexpagelist = glob.glob(searchpath + '*.html')
    orgidlist = []
    orgnamelist = []
    # Load up the index page, A.html, etc
    for indexpage in indexpagelist:
        indexpagepath = indexpage
        if os.path.exists(indexpagepath):
            html = open(indexpagepath,'r')
            soup = BeautifulSoup(html)
        
            # all of the text names are in links (a href ...)
            alist=soup.findAll('a')
            for link in alist:
                if 'orgid' in link.get('href'):
                    orgid = link.get('href').split('=')[-1]
                    orgname = link.text
                    orgidlist.append(orgid)
                    orgnamelist.append(orgname)
        
    CNdf = pd.DataFrame({'CNname':orgnamelist,'CNid':orgidlist})
    return CNdf

def _CNScrapeSummary(CNdf,idrange=(10,20),pause=0.5):
    subdf = CNdf.loc[idrange[0]:idrange[1]]
    for dfid, CNitem in subdf.iterrows():
        try:
            orgid=int(CNitem.CNid)
        except:
            print "cannot parse CNitem.CNid"
            
        CharityNavigatorMain(base='summary',orgid=orgid,uid='.U4-GN5SwLKc')
        print "Downloaded ID {}: {}".format(dfid,CNitem.CNname.encode('utf-8'))
        
        timetopause = np.random.rand() + pause # add a randomized sleep time from 0 to 1 sec
        time.sleep(timetopause)

def CharityNavigatorMain(base='',orgid=None,uid=None):
    '''
    base: ['summary','history','comments'] 
    orgid: e.g. 7645
    uid: .U4-GN5SwLKc
    
    CharityNavigatorMain('summary',6917,".U4-GN5SwLKc")
    '''
    acceptablebases = ['summary','history','history.detail','comments']
    if base not in acceptablebases:
        print "Need to specify base: ['summary','history','comments']"
        return
    try:
        orgid = int(orgid)
    except:
        print "Need to specify integer orgid: e.g. 7645 "
        return
    if not uid:
        print "Need to specify user id: e.g. '.U4-MkZTqa62'"
        return
    
    downloadpath = basepath + 'CharityNavigator/raw/{}/{}{}.html'.format(base,base,orgid)
    
    urlstring = 'http://www.charitynavigator.org/index.cfm?bay=search.{}&orgid={}#{}'.format(base,orgid,uid)
    
    # Download the file
    qScrape.downloadFile(downloadpath,urlstring)
    
def CharityNavigatorIRS(ein=None,uid=None):
    '''
    Each carity has an EIN, which charity navigator uses to search its IRS pages
    '''
    pass
    
def CharityNavigatorLoop():
    pass
