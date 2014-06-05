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

# 

def _CNSession():
    import qMail
    emailaddr=qMail.gmail_username+'@gmail.com'
    payload={'email':emailaddr,'password':qMail.gmail_password}
    session = requests.session()
    r=session.get('https://www.charitynavigator.org/index.cfm?bay=my.login', params=payload)
    # r=session.get('http://www.charitynavigator.org/index.cfm?bay=search.history&orgid=7958#.U5AJ35Tqa60')
    # r.content
    r.close()
    # 
    # local_file = open('test.pdf', "w" + 'b')
    # 
    # local_file.write(r.content)

# Hardcode this base path for now.
basepath = "/Users/amorgan/Documents/Insight/"

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
