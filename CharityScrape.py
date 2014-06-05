#!/usr/bin/env python
# encoding: utf-8
"""
CharityScrape.py
Author: Adam N Morgan
"""
import os
import qScrape
from BeautifulSoup import BeautifulSoup

# Hardcode this base path for now.
basepath = "/Users/amorgan/Documents/Insight/"

def _CNGetList(letter='A'):
    searchpath = basepath + "/CharityNavigator/index_pages/"
    # Load up the index page, A.html, etc
    indexpagepath = searchpath + letter.upper() + '.html'
    if os.path.exists(indexpagepath):
        html = open(indexpagepath,'r')
        soup = BeautifulSoup(html)
        pass
    

def CharityNavigatorMain(base='',orgid=None,uid=None):
    '''
    base: ['summary','history','comments'] 
    orgid: e.g. 7645
    uid: .U4-GN5SwLKc
    
    '''
    acceptablebases = ['summary','history','comments']
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