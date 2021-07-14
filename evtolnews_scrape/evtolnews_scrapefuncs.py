# General packages
import requests
import json
import time
import datetime
import random
import os
import sys

# data / numerical handling
import pandas as pd
import numpy as np

# data visualization
import seaborn as sb
import matplotlib as mp

# Scraping libraries
from bs4 import BeautifulSoup as bs4


"""

The functions below are used to assist in scraping the eVTOL aircraft directory landing page found here: https://evtol.news/aircraft


"""


def get_bs4(endpoint):

    """ Returns a bs4 object from a .get().text request at specified endpoint """
    
    # get request -- initialize html response object
    # https://docs.python-requests.org/en/master/user/quickstart/
    html = requests.get(endpoint).text 

    # initiate bs4 object
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    soup = bs4(html, 'html.parser')
    
    return soup

def get_accategories(soup):
    
    """
    Gets aircraft category labels from <strong> elements within <p> tags 
    
    Returns list of categories
    
    """
    # ptags are parent of <strong> labels and <ol> and <li> items
    p_tags = soup.find_all(name = 'p')

    # <strong> labels include aircraft category names
    strong_labels = [strong.find_all('strong') for strong in p_tags]

    # loop to grab and strip <strong> labels
    ac_labels = []
    for label in strong_labels:
        for l in label:
            ac_labels.append(l.text.strip())

    # labels are index [1:] -- see below

    # ['Welcome',
    #  'Vectored Thrust',
    #  'Hover Bikes/Personal Flying Devices',
    #  'Lift + Cruise',
    #  'Wingless (Multicopter)',
    #  'Electric Rotorcraft']

    return ac_labels[1:]

def get_acdirectory():
    
    """ 
    returns a dataframe of current aircraft directory
    at https://evtol.news/aircraft endpoint 
        
    """
    
    # aircraft directory url
    endpoint = "https://evtol.news/aircraft"
    # beautiful soup object for parsing
    soup = get_bs4(endpoint)
    
    # current list of aircraft categories -- as of July 2021
    categories = get_accategories(soup)

    # to build dictionary of aircraft href links as keys and categories as values
    ac_dict = get_aclinks(soup, categories)
    
    # build dataframe from aircraft dictionary
    df = pd.DataFrame.from_dict(data = ac_dict, orient = 'index' )

    # clean up
    df.reset_index(inplace=True)
    df.rename(inplace = True, columns = { 0:'category', 'index': 'links' } )
    
    return df


def get_aclinks(soup, categories):
    
    """
    
    builds aircraft dictionary with href links as identifier keys and aircraft
    categories as values
    
    returns a dictionary
    
    """
    
    # grab ordered lists to extract li list items that contain href links
    # each ordered list index aligns with categories index, i.e. each ol corresponds to a category
    olists = soup.find_all(name = 'ol')
    
    ac_dict = {}
    for ind, ol in enumerate(olists):
        for li in ol.find_all('li'):    
            try:
                # list of links per category
                ac_link = li.find('a').get('href')
            except:
                ac_link = 'error at index: {}'.format(ind)
            # add the aircraft link if not in dictionary -- prevents dupes
            if ac_link not in ac_dict:
                # assign aircraft link as key, and aircraft category as value
                ac_dict[ac_link] = categories[ind]

    return ac_dict




"""

Functions for scraping individual aircraft links from evtol.news

e.g. 

https://evtol.news/a3-by-airbus/

"""


## AIRCRAFT NAME AND STATUS DATA



def get_acname(soup):
    
    """ returns full aircraft name, OEM + model, from h1 tag """
    try:
        # aircraft name and status are in the h1 tag
        h1 = soup.find_all('h1')
        h1s = [tag for tag in h1]
        h1_text = ''

        # builds string of aircraft name
        ac_name = h1_text.join(h1s[0])
    except:
        ac_name = 'N/A'

    return ac_name

def get_acstatus(soup):

    """ assigns status as 'defunct' or 'active' pending if 'defunct' in h1 tag name """
    try:
        if 'defunct' in get_acname(soup):
            status = 'defunct'
        else:
            status = 'active'
    except:
        status = 'N/A'

    return status


## AIRCRAFT CORE DATA -- from 'p' tags
## including: AIRCRAFT MODEL, OEM, WEBSITE, PHYSICAL ADDRESS, ABOUT, RESOURCES, SPECS

def get_coredata(soup):
    
    """ 
    searches ptags for core aircraft data indicated by a <strong> tag 
    
    
    returns tuple (core data index, bs4.result object) if valid, else: 'error'
    
    """
    
    acptags = soup.find_all('p')
    
    # searches the first three <p> tags for core aircraft data -- indicated by <strong> within <p> tag
    for i, tag in enumerate(acptags[:2]):
        if tag.find('strong'):
            # we found the right p tag for core aircraft data -- save it for further parsing
            core_index = i
            core_data = acptags[core_index]
            
            # break loop, return index and data
            return core_index, core_data

        else: pass

    # error if didn't find anything
    return 'error'


def get_acmodel(core_data):
    
    """ gets the aircraft model from core data """
    
    if core_data != 'error':
        
        try:
    
            # renames paramater
            data = core_data[1]

            if data.find('strong'):
                acmodel = data.strong.text.strip()

                # break and return acmodel
                return acmodel
            else:
                return 'N/A'
                
        except:
            return 'N/A'
    else:
        return 'N/A'


def get_acoem(core_data):

    """ gets the ac oem from core data children """
    
    if core_data != 'error':

        data = core_data[1]

        try:

            for i, child in enumerate(data.children):

                # find the aircraft model name in parse tree for reference
                if child.name == 'strong':

                    # get the next sibling element -- the OEM name
                    if child.next_sibling.name != 'br':

                        try:
                            oem = child.next_sibling.text.strip()
                        except:
                            oem = child.next_sibling.strip()
                    # get the next x2 sibling element -- after jumping a line break
                    else:
                        try:
                            oem = child.next_sibling.next_sibling.text.strip()
                        except:
                            oem = child.next_sibling.next_sibling.strip()

                    # further stripping
                    oem = oem.replace("\xa0","")
                    oem = oem.replace("\r\n", "")

                    return oem

        except:

            return 'N/A'
            
    else:
        return 'N/A'

def get_acextlink(core_data):

    """ gets the aircraft model's website link if exists """
    
    if core_data != 'error':
        
        
    
        try:
            core_data = core_data[1]
            
            if core_data.a.get('href'):
                weblink = core_data.a.get('href')
        except:
            weblink = 'N/A'
            
    else:
        weblink = 'N/A'

    return weblink

def get_acaddress(core_data):
    
    """ returns address for aircraft oem if it exists. """
    
    if core_data != 'error':

        try:
            core_data = core_data[1]
            children = list(core_data.children)
            for i, child in enumerate(children):
                for t in child:
                    # major assumption -- if there is a comma or 'USA' in text then it's an address
                    # success of this assumption gives >90% accuracy given observed site structure, some errors are imminent
                    if ',' in t or 'USA' in t:
                        address = child.strip()
                        return address
        except:
            return 'N/A'
            
    else:
        return 'N/A'
        

def get_acabout(core_data, soup):
    
    """ 
    Returns the "about" text from aircraft landing page.
    
    The about ptag data is at a +1 index from the aircraft core data.
    
    Param:
    
    get_coredata() function response
    
    bs4 soup object for aircraft site link
    
    Returns:
    
    text for about data
    
    """
    
    if core_data != 'error':
    
        # find all ptags from soup object
        acptags = soup.find_all('p')

        try:
            core_data_index = core_data[0]
            # The about data index is +1 after core data ptag index
            about_index = core_data_index + 1
            # Get text response
            acabout = acptags[about_index].text.strip()
        except:
            acabout = 'N/A'
            
    else:
        acabout = 'N/A'

    return acabout

def get_acresources(soup):
    
    
    """ returns the href links from the 'Resources' label on aircraft page """
    
    # find all ptags from soup object
    acptags = soup.find_all('p')
    
    ## STEP 1 -- Find the "Resources" ptag index

    for i, ptag in enumerate(acptags):
        for tag in ptag:
            if "Resources:" in tag:
                res_ind = i
                break
            else: None

    ## STEP 2 -- Get the list item hrefs from resources ptag
    
    try:
        if res_ind:

            # label correct resource index of ptags
            resources = acptags[res_ind]

            # Storage for resource links
            hrefs = []

            # loop the siblings, i.e. tags after "Resources" ptag, to find unordered list
            for res in resources.next_siblings:
                # find the ul list
                if res.name == 'ul':
                    # fin all list items in unordered list
                    for item in res.find_all('li'):
                        # if the list item has an a tag, get the href link
                        for element in item:
                            if element.name == 'a':
                                hrefs.append(element.get('href'))
    except:
        hrefs = []
        
    return hrefs

def get_acspecs(soup):
    
    """ returns list of specification items if specification exists on site """
    
    # find all ptags from soup object
    acptags = soup.find_all('p')
    
    ## STEP 1 -- Find the "Specifications" ptag index

    for i, ptag in enumerate(acptags):
        for tag in ptag:
            if "Specifications:" in tag:
                specs_ind = i
                break
            else: None
                

    ## STEP 2 -- Get the list item hrefs from specifications ptag if exists
    
    # Storage for resource links
    spec_list = []
    
    try:
        # if "Specifications" list was found, countinue the scrape
        if specs_ind:

            specs = acptags[specs_ind]

            # loop the siblings, i.e. tags after "Specifications:" ptag, to find unordered list
            for spec in specs.next_siblings:
                # find the ul list
                if spec.name == 'ul':
                    # loop all list items in unordered list
                    for item in spec.find_all('li'):
                        # if the list item has an a tag, get the href link
                        for element in item:
                            # further stripping                        
                            try:
                                element = element.text.strip()
                                element = element.replace("\xa0"," ")
                                element = element.replace("\r\n", " ")

                                spec_list.append(element)
                            except:
                                spec_list.append(element.strip())
                                
    except:
        spec_list = []

    return spec_list


def scrape_appendnew(start_ind, stop_ind, inputs_df, results_df):
    
    """
    Overview: 
    This function adds new aircraft data to an existing dataframe 
    if the aircraft link doesn't already exist.

    Detail:
    Function loops through an inputs_df dataframe of weblinks and scrapes data
    from the link if it doesn't exist in results_df dataframe.
    
    This function calls all functions related to scraping data from an aircraft
    link and therefore scrapes ALL data then appends to dataframe.

    Params: 
    start_ind: index of link to start at
    
    stop_ind: index of link to stop at
    
    inputs_df: dataframe of links to check and scrape for, * Must include columns
    named 'links' + 'category'
    
    results_df: dataframe to append new link and scraped data to

    Returns:
    Appended results_df -- if conditions are met.
    
    """
    
    # ordered lists from original df
    links = inputs_df['links']
    categories = inputs_df['category']
    
    # start time
    start_time = time.time()
    print("start time: ", time.ctime(start_time))

    
    # loop through , add the data to new results_df with append
    for ind, link in enumerate(links[start_ind : stop_ind]):
        # if the link is not yet in new dataframe, continue
        if link not in list(results_df['link']):
            # dict to append to new results_df dataframe
            ac_data = {}

            # try / except for scraping data
            # Only updates ac_data if requests.get() was successful
            try:
                # get soup object
                acsoup = get_bs4(link)

                try:
                    
                    # add first key
                    ac_data['link'] = link
#                     print('got the link!')
#                     get aircraft category
                    # accounts for looping in a slices, to align proper index with categories
                    ac_data['category'] = categories[start_ind + ind]
#                     print('got the category!')
                    # get aircraft name
                    ac_data['name'] = get_acname(acsoup)
#                     print('got the name!')
                    # get status
                    ac_data['status'] = get_acstatus(acsoup)
#                     print('got the status!')

                    # get specs
                    ac_data['specs'] = get_acspecs(acsoup)
#                     print('got the specs!')
                    # get resources
                    ac_data['resources'] = get_acresources(acsoup)
#                     print('got the resources!')

                    # CORE DATA

                    # get core data paramaters for following data point functions
                    core_data = get_coredata(acsoup)
#                     print('got the core data!')

                    # get additional data points
                    ac_data['oem'] = get_acoem(core_data)
#                     print('got the oem!')
                    ac_data['model'] = get_acmodel(core_data)
#                     print('got the model!')
                    ac_data['aircraft_website'] = get_acextlink(core_data)
#                     print('got the website!')
                    ac_data['address'] = get_acaddress(core_data)
#                     print('got website!')
                    ac_data['about'] = get_acabout(core_data, acsoup)
#                     print('got the about!')
                    ## APPEND THE DATAFRAME
#                     print('got ALL DATA, now trying to append')
                    
                    # append the ac_data to existing dataframe
                    results_df = results_df.append(ac_data, ignore_index = True)

                except:

                    print('append error at: ', link, 'index: ', ind)

            except:
                print('requests() error at: ', link, 'index: ', ind)

            # add timer until next scrape request
            time.sleep(random.randint(7, 10))

            # additional sleep timer criteria
            # sleep 90 seconds every 25 hits
#             if ind % 20 == 0:
#                 # show last item in dataframe
#                 display(results_df.tail(1))
#                 time.sleep(90)

        else: None

    # program run time summary
    end_time = time.time()
    print("end time: ", time.ctime(end_time))
    print("")
    total_time = end_time - start_time
    print("total runtime: ",total_time)
    
    return results_df



## UPDATING DATAFRAMES
    
    
    
    
def check_updates(current, df_tocheck):
    
    """ takes in current aircraft directory df and compares to a results df """
    
    if len(current) > len(df_tocheck):
        diff = len(current) - len(df_tocheck)    
        response = "NOT up to date. {} new aircraft exist".format(diff)
        return response
    
    else: return "Your df is up to date. No update needed."
    
    
    
def check_na(updated_df):
    """ checks dataframe for NA values and returns a dictionary with columns and their NA counts sorted by counts """
    
    na_cols = list(updated_df.columns)

    # find number of NA values for each column if they exist
    # build dictionary
    na_response = {col: updated_df['{}'.format(col)].isna().value_counts()[1] for col in na_cols \
                   if len(updated_df['{}'.format(col)].isna().value_counts())>1}
    
    if len(na_response) != 0:
        
        # sort dict by greatest NAs count 
        new_nas = dict(sorted(na_response.items(), key = lambda item: item[1]))
        return new_nas
    else: return "No NA values in the dataframe"
    
    
    
    
def check_mostna(na_dict):
    """ takes a dict of NA cols and counts, returns a list of tuples with column(s) with most (max) NA counts """

    maxs = []
    for col, count in nas.items():
        if count == max(nas.values()):
            maxs.append((col, count))
    return maxs    
    
    

    

def update_na(cols_list, aircraft_link, df):

    """ 
    
    Updates dataframe row by aircraft link key for specified list of na values.
    
    Params:
    
    cols_list --> list of cols to update. Example: ['oem', 'model']
    ** suggested use: one column at a time for easy error isolation.
    
    aircraft_link --> index: str(link) to an aircraft site
    
    df --> dataframe to update
    
    NOTE** .set_index() of df to 'link' before use!
    
    Returns: 
    
    Updated df
    
    
    """
    
    # verify that index is set to the 'link' column
    if df.index.name != 'link':
        df.set_index('link', inplace = True )
    else: None
    
    # get soup object
    acsoup = get_bs4(aircraft_link)

    # to populate with cols:new_vals
    nadict = {}
    
    # Build FUNCTION DICT --> func_dict = {'model': get_acmodel(), 'website': get_acextlink()...}
    core_data = get_coredata(acsoup)
    
    # mapping col keys to associated function values
    func_dict = {'specs': [get_acspecs(acsoup)], 'resources': [get_acresources(acsoup)], 'oem': get_acoem(core_data), \
                
                'model': get_acmodel(core_data), 'aircraft_website': get_acextlink(core_data), 'address': get_acaddress(core_data), \
                
                'about': get_acabout(core_data, acsoup)}
    
    # run functions for new col data, store in dict
    nadict = {col: func_dict[col] for col in cols_list}

#     for val in nadict.values():
#         print(val)
#         print('and the length of the value is ', len(val))
    
    
    # create single-row pd.df to update dataframe
    naupdate = pd.DataFrame(nadict, index = [aircraft_link])

    # update dataframe row
    df.update(naupdate)
    