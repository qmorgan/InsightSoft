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
import time
# 
import numpy as np
import lxml # html/xml parser
import gc

# Hardcode this base path for now.

if not os.environ.has_key("insight"):
    print "You need to set the environment variable 'insight' to point to the"
    print "directory where you have 'insight' installed"
    sys.exit(1)
basepath = os.environ.get("insight")
cn_user = os.environ.get("CN_USER")
cn_pass = os.environ.get("CN_PASS")



def _CNSummaryLoop(cndf,searchrange=(0,100)):
    '''Loop through and parse the CN summary pages, then add them to a dataframe'''
    index = cndf.CNid.astype('int')
    columns = [u'PROGRAM_EXPENSES',
     u'DONORADVISORY',
     u'CN_ID',
     u'SUMMARY_YEAR',
     u'TOTAL_PRIMARY_REVENUE',
     # u'CHARITYTAGLINE',
     u'MEMBERSHIP_DUES',
     u'ACCOUNTABILITY_AND_TRANSPARENCY_RATING',
     u'FINANCIAL_VALUE',
     u'ADMINISTRATIVE_EXPENSES',
     u'PROGRAM_SERVICE_REVENUE',
     u'CONTRIBUTIONS_GIFTS_AND_GRANTS',
     u'OTHER_REVENUE',
     u'TOTAL_CONTRIBUTIONS',
     u'TOTAL_FUNCTIONAL_EXPENSES',
     u'RELATED_ORGANIZATIONS',
     u'ACCOUNTABILITY_AND_TRANSPARENCY_VALUE',
     u'PAYMENTS_TO_AFFILIATES',
     u'CHARITYCLASS',
     u'GOVERNMENT_GRANTS',
     u'FUNDRAISING_EVENTS',
     u'NET_ASSETS',
     u'FINANCIAL_RATING',
     u'EXCESS_FOR_THE_YEAR',
     u'FUNDRAISING_EXPENSES',
     u'CHARITYNAME',
     u'OVERALL_RATING',
     u'OVERALL_VALUE',
     u'TOTAL_REVENUE',
     u'FEDERATED_CAMPAIGNS']
    
    CNFull = pd.DataFrame(index=index, columns=columns)
    
    CNFullDict = {}
    
    # index2=np.arange(len(index)*4)
    columns2=[u'CN_ID',
        u'YEAR',
        u'PRIMARY_REVENUE',
        u'PROGRAM_EXPENSES']
    
    # FinancesHistWebFull = pd.DataFrame(index=index2,columns=columns2)
    
    columns3=[u'CN_ID',
        u'EMPLOYEE_NAME',
        u'EMPLOYEE_POSITION',
        u'SALARY',
        u'SALARY_PCT_OF_TOTAL',
        u'YEAR']
    
    # CompensationFull = pd.DataFrame(index=index2,columns=columns3)
    
    searchpath = basepath + "/CharityNavigator/raw/summary/"
    indexpagelist = glob.glob(searchpath + '*.html')
    # assert len(indexpagelist) > 0
    orgidlist = []
    orgnamelist = []
    
    cnidlist = []
    cn_finances_history_web_list = []
    
    unable_to_parse_list = []
    
    count=0
    
    # if searchrange:
    #     indexrange = index[searchrange[0]:searchrange[1]]
    # else:
    #     indexrange = index
    
    filerange=indexpagelist[searchrange[0]:searchrange[1]]
    
    fcount=0
    scount=0
    currentcount=0
    oldtime = time.time()
    # Load up the index page, summary3203.html, etc
    # for ind in indexrange:#[searchrange[0]:searchrange[1]]:
    for indexpage in filerange:
        # indexpage=searchpath + "summary" + str(ind) + ".html"
        count+=1 
        if np.mod(count,50) == 0:
            newtime = time.time()
            print "Finished {} out of {}".format(count,len(filerange))
            print "Last iteration took {} seconds".format(newtime-oldtime)
            oldtime=newtime
        cndict,histdf,compdf=_CNSummaryParse(indexpage)
        if cndict:
            current_id = cndict[u'CN_ID']
            # CNFullDict.update({current_id:cndict})
            # oh hell, it was the UPDATE that was killing it!
            ### BAD
            ### CNFull.ix[current_id].update(pd.Series(cndict))
            ### GOOD
            ### CNFull.loc[current_id] = pd.Series(cndict)
            
            CNFull.loc[current_id] = pd.Series(cndict)
            # This was taking longer and longer. Crap way to do this.
            # Finished 25 out of 7518
            # Last iteration took 12.8670480251 seconds
            # Finished 100 out of 7518
            # Last iteration took 18.8660750389 seconds
            # Finished 200 out of 7518
            # Last iteration took 31.1348628998 seconds
            # Finished 300 out of 7518
            # Last iteration took 39.9171040058 seconds

        
            
        else:
            print "NOTHING FOR CN_ID {}".format(indexpage)
        
        gc.collect()
        # if len(histdf) != 0:
        # 
        #     for ind in np.arange(len(histdf)):
        #         FinancesHistWebFull.ix[ind+scount].update(histdf.loc[ind])                  
        #     scount += len(histdf)
        #     
        # if len(compdf) != 0:
        #     # scountstop = scount + len(compdf)
        #     # CompensationFull.ix[scount:scountstop].update(compdf)
        #     # CompensationFull=CompensationFull.append(compdf,ignore_index=True)
        #     for ind in np.arange(len(compdf)):
        #         CompensationFull.ix[ind+fcount].update(compdf.loc[ind])
        #     fcount += len(compdf)
    # CNsummarydf = pd.DataFrame({'CNid':orgidlist})
    return CNFull #, FinancesHistWebFull, CompensationFull
    
def _CNSummaryParse(indexpage,find_summary=True,find_employee_comp=False,find_historical=False):
    '''Parse CN Summary Pages'''
    cn_dict={}
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

        donoradvisory = 0
        if "Donor Advisory" in soup.find('title').text:
            # print soup.find('title').text
            # print "  DONOR ADVISORY FOR id {}; skipping".format(cnid)
            donoradvisory = 1
        
        #################################################
        
        # grab the main html:
        mainsoup = soup.find('div',id='maincontent2')
        
        charityname = mainsoup.find('h1','charityname').string
        # u'Kiva'
        # tagline = mainsoup.find('h2','tagline').string
        # u'Loans that change lives'
        classification = mainsoup.find('p','crumbs').string
        # u'International : Development and Relief Services'
        # if tagline != None:
        #     tagline = tagline.replace('\n','')
        infodict = {u'CHARITYNAME':charityname,
                    # u'CHARITYTAGLINE':tagline,
                    u'CHARITYCLASS':classification,
                    u'DONORADVISORY':donoradvisory}
        ratingdict={}
        incomedict={}
        yeardict={}
        cn_summary_finances_history_web_df=[]
        comp_df=[]
        
        if donoradvisory == 0:
            # NOW FOR THE FUN PARSING PART.
    
            #################################################
            # HISTORICAL REVENUE & PROGRAM EXPENSES
            #  from google visualization
            #  put these in a separate table
        
            # these will be in a <script> tag:
            #   ['Year', 'Primary Revenue', 'Program Expenses'],
            # ['2009',  477240602.0000,   471243724.0000], ['2010',  550469681.0000,   436929989.0000], ['2011',  535384778.0000,   467860232.0000], ['2012',  554416396.0000,   465069220.0000] 
            # 
            # 
            if find_historical==True:
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
                cn_summary_finances_history_web_df = pd.DataFrame({'CN_ID':cnid,
                                                    'YEAR':yearlist,
                                                    'PRIMARY_REVENUE':revlist,
                                                    'PROGRAM_EXPENSES':explist}) 


        
            if find_summary==True:
                summarysoup = mainsoup.find('div','summarywrap')
        
                # the metric calculation tables are in 'shadedtable' class
                shadedtables=summarysoup.findAll('div','shadedtable')
        
                overallbool = ['Overall' in s_table.text for s_table in shadedtables]
                financialbool = ['Financial Performance Metrics' in s_table.text for s_table in shadedtables]
                accountabilitybool = ['Transparency Performance Metrics' in s_table.text for s_table in shadedtables]
        
                overallindex = np.where(overallbool)[0][0]
                financialindex = np.where(financialbool)[0][0]
                accountabilityindex = np.where(accountabilitybool)[0][0]
        
                overalltable = shadedtables[overallindex]
                financialtable = shadedtables[financialindex]
                accountabilitytable = shadedtables[accountabilityindex]
        
                summary_year = overalltable.findAll('th','centerme')[-1].text.split('/')[-1]
                yeardict = {u'SUMMARY_YEAR':summary_year}
        
                # 0 overall table
                    # RATINGTYPE        SCORE       RATING
                    # overall           float       int
                    # financial         float       int
                    # accountability    float       int
        
        
                rowlist = overalltable.findAll('tr')
                for row in rowlist:
                    itriplet = row.findAll('td')
                    if len(itriplet) == 3:
                        ikey = (itriplet[0].text)\
                            .replace('&nbsp;','')\
                            .replace(' ','_')\
                            .replace(',','')\
                            .upper()\
                            .replace('(OR_DEFICIT)','')\
                            .replace('&AMP;','AND')
                        ival = (itriplet[1].text)\
                            .replace('&nbsp;','')\
                            .replace('$','')\
                            .replace(',','')
                        irank = (itriplet[2].find('img')['title'])

                        key1 = ikey+'_VALUE'
                        key2 = ikey+'_RATING'
                
                        ratingdict.update({key1:float(ival)})
                        ratingdict.update({key2:irank})
                
        
        
                # 1 Financial Performance Metrics
                    # Program Expenses         82.6% 
                    # Administrative Expenses    12.3%
                    # Fundraising Expenses   5.0%
                    # Fundraising Efficiency    $0.04
                    # Primary Revenue Growth     20.1%
                    # Program Expenses Growth    11.4%
                    # Working Capital Ratio (years) 1.30
            
                #2 Accountability &amp; Transparency Performance Metrics
                    # Independent Voting Board Members  
                    # No Material diversion of assets   
                    # Audited financials prepared by independent accountant 
                    # Does Not Provide Loan(s) to or Receive Loan(s) From related parties   
                    # Documents Board Meeting Minutes   
                    # Provided copy of Form 990 to organizations governing body in advance of filing    
                    # Conflict of Interest Policy   
                    # Whistleblower Policy  
                    # Records Retention and Destruction Policy  
                    # CEO listed with salary    
                    # Process for determining CEO compensation  
                    # Board Listed / Board Members Not Compensated  
                    # Donor Privacy Policy  
                    # Board Members Listed  
                    # Audited Financials    
                    # Form 990  
                    # Key staff listed  
           
                #
                summaries = summarysoup.findAll('div','summaryBox')    
                   # 0: Accountability &amp; Transparency Performance Metrics
                   # 1: Income Statement
                   # 2: Charts
                   # 3: Compensation of Leaders
                   # 4: Mission
                   # 5: Charities Performing Similar Types of Work
        
                #Charity Login??
        
                # FINANCIAL TABLE - INCOME STATEMENT
        
                # could loop over these and grab the innards.. right now just taking the income statement
                incomestatement = summaries[1]
        
                itemlist = incomestatement.findAll('tr')
        
                for item in itemlist:
                    ipair = item.findAll('td')
                    if len(ipair) == 2:
                        ikey = (ipair[0].text)\
                            .replace('&nbsp;','')\
                            .replace(' ','_')\
                            .replace(',','')\
                            .upper()\
                            .replace('(OR_DEFICIT)','')\
                            .replace('&AMP;','AND')
                        ival = (ipair[1].text)\
                            .replace('&nbsp;','')\
                            .replace('$','')\
                            .replace(',','')
                        try:
                            # these should all be integers
                            ival=int(ival)
                        except:
                            continue
                        incomedict.update({ikey:ival})
            
                # EMPLOYEE COMPENSATION 
                if find_employee_comp == True:
                    salarystatement = summaries[3]
            
                    itemlist = salarystatement.findAll('tr')    
                    compensations=[[item.text for item in itemlist[indd].findAll('td')] for indd in range(len(itemlist))]
                    compensations_list = []   
                    for comp in compensations:
                        if len(comp) == 5:
                            compensations_list.append(comp)
            
                    comp_array = np.array(compensations_list).T[0:4]
                    comp_df = pd.DataFrame({u'CN_ID':cnid,u'YEAR':2012,
                        u'SALARY':[(sal.replace('$','').replace(',','')) for sal in comp_array[0]],
                        u'SALARY_PCT_OF_TOTAL':[(sal.replace('%','')) for sal in comp_array[1]],
                        u'EMPLOYEE_NAME':comp_array[2],
                        u'EMPLOYEE_POSITION':comp_array[3]})

                summarysoup.decompose()
            # FINANCIAL METRICS
            # program_expenses 
            # admin_expenses 
            # fundraising_expenses
            # fundraising_efficiency
            # revenue_growth
            # expenses_growth
            # working_capital_ratio
        

            #################################################        
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
        
        
        
        
        
        
             # GET YEAR for verifying that it stays constant. 
        
        
            # all of the text names are in links (a href ...)
            # alist=soup.findAll('a')
            # for link in alist:
            #     if 'orgid' in link.get('href'):
            #         orgid = link.get('href').split('=')[-1]
            #         orgname = link.text
            #         orgidlist.append(orgid)
            #         orgnamelist.append(orgname)
        html.close()
        mainsoup.decompose()
        soup.decompose()
    else:
        raise ValueError("Page {} was indexed but doesn't exist??".format(indexpage))
    
    cn_dict.update(ratingdict)
    cn_dict.update(incomedict)
    cn_dict.update(infodict)
    cn_dict.update(yeardict)
    cn_dict.update({u'CN_ID':cnid})
    # print cn_dict
    return cn_dict ,cn_summary_finances_history_web_df, comp_df


def _CNEINLoop(searchrange=(0,100)):
    # index = cndf.CNid.astype('int')
    columns = [u'CN_ID',
            u'EIN']
    
    searchpath = basepath + "/CharityNavigator/raw/history/"
    indexpagelist = glob.glob(searchpath + '*.html')
    # assert len(indexpagelist) > 0
    orgidlist = []
    orgnamelist = []
    
    cnidlist = []
    cn_finances_history_web_list = []
    
    unable_to_parse_list = []
    
    count=0
    
    CNEINDF = pd.DataFrame(index=range(len(indexpagelist)), columns=columns)
    
    
    filerange=indexpagelist[searchrange[0]:searchrange[1]] 
    
    fcount=0
    scount=0
    currentcount=0
    oldtime = time.time()
    
    for indexpage in filerange:
        # indexpage=searchpath + "summary" + str(ind) + ".html"
        current_id=count
        count+=1 
        if np.mod(count,50) == 0:
            newtime = time.time()
            print "Finished {} out of {}".format(count,len(filerange))
            print "Last iteration took {} seconds".format(newtime-oldtime)
            oldtime=newtime
        EIN=_CNHistoryParse(indexpage,only_get_EIN=True)
        if EIN:
            # current_id = cndict[u'CN_ID']
            # EIN = 'index.cfm?bay=search.irs&ein=364395095'
            einstr = EIN.split('=')[-1]
            einint=int(einstr)
            cnidint=int(os.path.basename(indexpage).split('.')[0].replace('history',''))
            CNEINDF.loc[current_id] = pd.Series({'CN_ID':cnidint,'EIN':einint})
            
        else:
            print "NOTHING FOR CN_ID {}".format(indexpage)
        
        gc.collect()
    return CNEINDF
    
    
def _CNHistoryParse(indexpage,only_get_EIN=True):
    '''Parse CN History Pages'''

    # Load up the index page, A.html, etc
    indexpagepath = indexpage
    if os.path.exists(indexpagepath):
        html = open(indexpagepath,'r')
        soup = BeautifulSoup(html)
        # all of the text names are in links (a href ...)
        if only_get_EIN: # ONLY GET THE EIN AND THEN EXIT
            alist=soup.findAll('a')
            for link in alist:
                try:
                    if 'search.irs' in link.get('href'):
                        orgname = link.get('href')
                        html.close()
                        soup.decompose()
                        return orgname
                except:
                    pass
                
        html.close()
        soup.decompose()
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
            html.close()
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

def _ParseGSDescription(html):
    assert html.split('.')[-1].lower()=='html'
    # print "opening", html
    openedfile=open(html)
    readfile = openedfile.read()
    mission="Not found."
    if "<h3>Mission</h3></div><p>" in readfile:
        mission=readfile.split('<h3>Mission</h3></div><p>')[-1].split('</p></div>')[0]
    mission=mission.replace("'","&#39;")
    return mission
    

def _ParseGSNTEE(html):
    # In [126]: soup = BeautifulSoup(file('/Users/amorgan/Desktop/99-0288410.html'))
    # 
    # In [127]: soup.findAll('ul')[0].text.split(')')
    # Out[127]: [u'F32 (Community Mental Health Center', u'']
    pass

def _ParseGSTables(html):
    assert html.split('.')[-1].lower()=='html' # quick & dumb type checking
    # openedfile=open(html)
    # readfile = openedfile.read()
    
    # all years appear to be in the HTML! Just hidden! So much data.
    
    # skiprows since the first one contains dates, and then pandas tries to read all rows as dates
    try: 
        liabilities = pd.read_html(html,match="Total Liabilities:",skiprows=[0])
        # grab the latest year; should be the first instance of the table
        liabilities = liabilities[0].set_index(0)
    except ValueError:
        liabilities = None
    try:
        assets = pd.read_html(html,match="Total Assets:",skiprows=[0])
        assets = assets[0].set_index(0)
    except ValueError:
        assets = None
    try:
        revenue = pd.read_html(html,match="Total Revenue:")
        revenue = revenue[0].set_index(0)
    except ValueError:
        revenue = None
    try:
        #                                1
        # 0
        # Program Services     $12,142,393
        # Administration          $255,736
        # Fundraising                   $0
        # Total Expenditures:  $12,398,129
        expenses = pd.read_html(html,match="Administration")
        expenses = expenses[0].set_index(0)
        # convert to an integer
        expenses[1]=expenses[1].str.replace('$','').str.replace(',','').str.replace(')','').str.replace('(','-')

    except ValueError:
        expenses = None
    try:
        netgain = pd.read_html(html,match="Gain/Loss")
        netgain = netgain[0].set_index(0)
    except ValueError:
        netgain = None
    
    return expenses
    
    
def _insertIntoGS(cursor,ein,description):

    pass
    # don't forget to commit!
    # conn.commit()

def _GSPopulateTable(filelist=[],drop=False):
    import pymysql
    import os
    if not os.environ.has_key("MYSQL_PASS"):
        print "You need to set the environment variable  to"
        print "point to your mysql password"
        return
    else:
        passwd = os.environ.get("MYSQL_PASS")
    
    conn = pymysql.connect(host='localhost',user='root',passwd=passwd, db='cnavigator')
    cursor = conn.cursor()
    
   
    if drop:
        cursor.execute("DROP TABLE IF EXISTS missions")
        #make schema
        sql_cmd="""
        CREATE TABLE missions (
            description_ID              INT AUTO_INCREMENT,
            EIN                          BIGINT  UNIQUE,
            description                 VARCHAR(32767)   ,  
            PRIMARY KEY(description_ID)
            )
        """
        print "Creating table"
        cursor.execute(sql_cmd)
        conn.commit()
        conn.close()
        return
    

             
    niter = len(filelist)/100
    
    n=0 
    
    while n < niter:
        insertcmd="""INSERT IGNORE INTO missions (EIN,description)
            VALUES"""
            
        filelist2=filelist[n*100:(n+1)*100]
        print "doing", n*100, ' to ', (n+1)*100
        for filename in filelist2:
            # print filename
            mission = _ParseGSDescription(filename)
            ein = int(filename.split('/')[-1].replace('-','').replace('.html',''))
        
            insertcmd+=""" ({ein},'{description}'),
            """.format(ein=ein,description=mission)
        
        # cursor = _insertIntoGS(cursor,ein,mission)
        insertcmd=insertcmd.rstrip().rstrip(',')
        # insertcmd+="ON DUPLICATE KEY UPDATE description='{description}'"
        print "executing"
        cursor.execute(insertcmd)
        conn.commit()
        n += 1
        print "Finished {}/{}".format(n*100,len(filelist))
    

    print "done"
    
    # do populations
    

    
    conn.close()