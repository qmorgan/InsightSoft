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
import qErr
# 
import lxml # html/xml parser

# Hardcode this base path for now.

if not os.environ.has_key("insight"):
    print "You need to set the environment variable 'insight' to point to the"
    print "directory where you have 'insight' installed"
    sys.exit(1)
basepath = os.environ.get("insight")
cn_user = os.environ.get("CN_USER")
cn_pass = os.environ.get("CN_PASS")



def _CNSummaryLoop(cndf):
    '''Loop through and parse the CN summary pages'''
    searchpath = basepath + "/CharityNavigator/raw/summary/"
    indexpagelist = glob.glob(searchpath + '*.html')
    assert len(indexpagelist) > 0
    orgidlist = []
    orgnamelist = []
    
    cnidlist = []
    cn_finances_history_web_list = []
    
    # Load up the index page, summary3203.html, etc
    for indexpage in indexpagelist:
        cndict=_CNSummaryParse(indexpage)
    
    
    
    CNsummarydf = pd.DataFrame({'CNid':orgidlist})
    return CNdf
def _CNSummaryParse(indexpage):
    '''Parse CN Summary Pages'''
    cndict={}
    indexpagepath = indexpage
    if os.path.exists(indexpagepath):
        # Grab the Charity Navigator page ID
        try:
            cnid = int(os.path.basename(indexpagepath).split('.')[0].lstrip('summary'))
        except:
            raise ValueError("Filename {} malformed. Should be format 'summary12345.html'")
        # open the html
        html = open(indexpagepath,'r')
        soup = BeautifulSoup(html)
        
        # NOW FOR THE FUN PARSING PART.
    
        # HISTORICAL REVENUE & PROGRAM EXPENSES
        #  from google visualization
        #  put these in a separate table?
        
        # these will be in a <script> tag:
        #   ['Year', 'Primary Revenue', 'Program Expenses'],
        # ['2009',  477240602.0000,   471243724.0000], ['2010',  550469681.0000,   436929989.0000], ['2011',  535384778.0000,   467860232.0000], ['2012',  554416396.0000,   465069220.0000] 
        # 
        # 
        scripts=soup.findAll('script')
        
        for script in scripts:
            strscript=str(script)
            if "'Year', 'Primary Revenue', 'Program Expenses'" in strscript:
                lines=strscript.split("\r\n")
                indexbool = ["['Year', 'Primary Revenue', 'Program Expenses']" in line for line in lines]
                indexreturn = np.where(np.array(indexbool)) # Out[215]: (array([4]),)
                index = indexreturn[0]+1 # the values will be one line after the header
                financialhistorylist = []
                yearlist=[]
                revlist=[]
                explist=[]
                valuelist = lines[index].strip().split(', [')
                for values in valuelist:
                    items=values.strip(']').strip('[').split(',')
                    cleaneditems = [float(item.strip("'").strip()) for item in items]
                    yearlist.append(cleaneditems[0])
                    revlist.append(cleaneditems[1])
                    explist.append(cleaneditems[2])
                    # raise Exception
                    if len(items) == 0:
                        raise ValueError('Empty historical revenue list. Could not parse.')
                    elif len(items) != 3:
                        raise ValueError('Could not parse historical revenue list.')
                    # financialhistorylist.append(cleaneditems)
        
        # transpose it and feed it into pandas
        np.array(financialhistorylist).T
        cn_summary_finances_history_web_df = pd.DataFrame({'cn_id':cnid,
                                            'year':yearlist,
                                            'primary_revenue':revlist,
                                            'program_expenses':explist}) 
                
            # else: 
            #     print 'no'
        
        
        
        #Financial metrics 
        # program_expenses 
        # admin_expenses 
        # fundraising_expenses
        # fundraising_efficiency
        # revenue_growth
        # expenses_growth
        # working_capital_ratio
        
        # # possible icons
        # _gfx_/icons/checked.gif
        # _gfx_/icons/checkboxX.gif
        # _gfx_/icons/CheckboxOptOut.png
        # 
        
        #Accountability Metrics
        # ivb_members
        # diversion_of_assests
        # audited_financials
        # loans_conflicting
        # board_minutes
        # distributed_990
        # whistleblower_policy
        # records_policy
        # ceo_listed
        # board_listed
        
        #website
        
        # donor_privacy_web
        # board_listed_web
        # audited_financials_web
        # form_990_web
        # key_staff_web
        
        # FINANCIAL TABLE - INCOME STATEMENT
        
         # GET YEAR for verifying that it stays constant. 
        
        
        # all of the text names are in links (a href ...)
        # alist=soup.findAll('a')
        # for link in alist:
        #     if 'orgid' in link.get('href'):
        #         orgid = link.get('href').split('=')[-1]
        #         orgname = link.text
        #         orgidlist.append(orgid)
        #         orgnamelist.append(orgname)
    else:
        raise ValueError("Page {} was indexed but doesn't exist??".format(indexpage))
    return cn_summary_finances_history_web_df

def _CNHistoryParse():
    '''Parse CN History Pages'''
    searchpath = basepath + "/CharityNavigator/raw/history/"
    indexpagelist = glob.glob(searchpath + '*.html')
    assert len(indexpagelist) > 0
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
        else:
            raise ValueError("Page {} was indexed but doesn't exist??".format(indexpage))
        
    # CNdf = pd.DataFrame({'CNid':orgidlist})
    # return CNdf


def _CNGetList():
    '''Return dataframe of CharityNavigator indices'''
    searchpath = basepath + "/CharityNavigator/index_pages/"
    indexpagelist = glob.glob(searchpath + '*.html')
    orgidlist = []
    orgnamelist = []
    # Load up the index page, history3203.html, etc
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

