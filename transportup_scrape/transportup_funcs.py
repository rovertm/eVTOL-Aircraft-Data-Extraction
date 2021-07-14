"""

Functions for scraping the TransportUP site


"""

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



## FOR REQUESTS 

def get_bs4(endpoint):

    """ Returns a bs4 object from a .get().text request at specified endpoint """
    
    # get request -- initialize html response object
    # https://docs.python-requests.org/en/master/user/quickstart/
    html = requests.get(endpoint).text 

    # initiate bs4 object
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    soup = bs4(html, 'html.parser')
    
    return soup




## FOR SCRAPING AIRCRAFT DATA



def get_summary(soup):

    """ returns 'quick summary' from aircraft page """
    
    # ptags
    ptags = acsoup.find_all('p')

    # second index ptag
    summary = ptags[2].text.strip()
    
    return summary



def get_devstage(soup):
    
    """
    
    Overview:
    
    Returns the development stage in a string format given a bs4 soup object
    
    More details:
    
    x-icon picture index to development stage

    0: "preliminary design"
    1: "prototype build"
    2: "flight testing"
    3: "certification"
    4: "commercially operating"

    """
    stages_dict = {0: "preliminary design", 1: "prototype build", \
                  2: "flight testing", 3: "certification", 4: "commercially operating"}

    # x-icons are in 'i' tags
    itags = acsoup.find_all('i')

    dev_stages = []
    
    try:

        for tag in itags:
            if 'data-x-icon' in tag.prettify():
                dev_stages.append(tag)

        for i, stage in enumerate(dev_stages):
            # color attribute required, and 0% features of color attributes indicate false positives
            if 'color' in stage.prettify() and '0%' not in stage.prettify():
                stage_ind = i
                break

        dev_stage = stages_dict[stage_ind]
        
    except:
        dev_stage = None

    return dev_stage



def get_details(soup, details_dict):
    
    """
    Builds a dictionary of all 'strong' elements as keys and element details as value.
    Returns a dictionary 

    Params:

    * soup object

    * dictionary to build or update -- can be empty

    Returns:

    * dictionary of detail keys and their values


    ## Example detail keys

    #         * Powerplant: 

    #         * Range:

    #         * Top Speed:

    #         * Propeller Configuration: 

    #         * Passenger/Payload Capacity:

    #         * Autonomy Level:

    #         * Wingspan/Dimensions:

    #         * Key Suppliers: 


    """
    acsoup = soup

    ptags = acsoup.find_all('p')
    
    try:

        for i, p in enumerate(ptags):
            if p.strong:

                # get detail key
                key = p.strong.text.strip()
                key = key.replace(":", "")

                # get detail value
                val = p.strong.next_sibling

                # add to dict
                details_dict[key] = val
                
    except:
        
        pass
            
    return details_dict


def get_references(soup):
    
    """ gets reference links from aircraft page. Returns a list."""
    
    ## Resources are the last unordered list
    uls = acsoup.find_all('ul')
    refs = uls[-1]
    
    # list items
    lis = refs.find_all('li')
    
    links = []
    
    try:
    
        for li in lis:
            if li.a:
                link = li.a.get('href')
                if 'transportup' not in link: 
                    links.append(link)
                else: pass
            else: pass
            
    except:
        # empty list
        return links
        
        # links list
    return links
    
    

def get_tu_acdata(directory_df, results_df):
    
    """
    
    Overview:
    
    Compares url links from up-to-date directory with url links 
    in current dataframe -- or new dataframe if starting from scratch -- and updates results_df with new data.
    
    Use case:
    
    * Starting a dataframe from scratch --> pass an empty df parameter
    
    * Updating a current dataframe --> pass current dataframe
    
    
    """

    transup_directory = directory_df
    
    update_counter = 0

    ## if the transup aircraft link is not already in the new dataframe, scrape.
    for i, link in enumerate(transup_directory['link']):

        if link not in list(results_df['link']):

            # data for dataframe append
            ac_data = {}

            try:

                # get soup object
                acsoup = get_bs4(link)

                # get category from source dataframe
                ac_data['category'] = transup_directory['category'][i]

                # get category from source dataframe
                ac_data['ac_name'] = transup_directory['ac_name'][i]

                # get link
                ac_data['link'] = link

                # returns summary string
                summary = get_summary(acsoup)
                ac_data['summary'] = summary

                # returns string of dev stage
                dev_stage = get_devstage(acsoup)
                ac_data['dev_stage'] = dev_stage

                # returns list
                references = get_references(acsoup)
                ac_data['references'] = references

                # returns dict OR updated dict
                ac_data = get_details(acsoup, ac_data)

                # print(ac_data)

                results_df = results_df.append(ac_data, ignore_index = True)

                print("Successfully appended a row to dataframe, index: ", i, "link: ", link)
                
                update_counter += 1

            except: 
                print("Error at: ", i, ", link: ", link)

            time.sleep(random.randint(5, 7))
            
            print("")
            print("Summary: ")
            
            if update_counter > 0:
                print("Added ", update_counter, "new aircraft")
            else:
                print("Nothing was updated")




## FOR UPDATING DATAFRAMES




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
    
    


## FOR DATA CLEANING




def drop_nullcols(df, nullperc):

    """ 
    Drops columns of a dataframe based on a percentage parameter for (# null rows / total rows). 
    
    Returns list of dropped columns. 
    
    """

    null_cols = []
    for df_col in list(cdf.columns):
        if len(cdf[cdf[df_col].isna()]) / len(cdf) >= nullperc:
            null_cols.append(df_col)

    cdf.drop(columns = null_cols, inplace = True)
    
    print("These are the dropped columns...")
    
    return null_cols
            
    
    

def assign_actype(x):
    
    """ 
    df.apply(lambda x: ac_typer(x)) support function.
    
    Provides logic and return value for Aircraft Type value grouping.
    
    """
    
    # ac_types = ['Winged VTOL', 'Wingless VTOL', 'STOL', 'Other']

    # type conversion
    x = str(x)

    # Winged VTOL
    if 'winged' in x.lower() and 'vtol' in x.lower():
        x = 'Winged VTOL'
    elif 'wingless' in x.lower() and 'vtol' in x.lower():
        x = 'Wingless VTOL'
    elif 'stol' in x.lower():
        x = 'STOL'
    else:
        x = None
        
    return x


def handle_null_devstage(df):
    
    """
    
    Changes null values in dev_stage to 'prototype build' if they are in the 'market' category
    
    Rationale: 
    Market category is less watched, less publicized. So likely to be a project in early stages.
    
    """
    
    cdf = df
    
    # get indices for null dev_stage and 'category' == market
    updi = np.where((cdf['dev_stage'].isna() == True) & (cdf['category'] == 'market'))
    ind_upd = list(updi[0])

    for i in ind_upd:
        cdf['dev_stage'][i] = 'prototype build'


def assign_prodstage(x):
    
    """
    Takes a series object from df['dev_stage'] and returns the appropriate value for df['prod_stage'] 
    based on conversion logic set below. Update as needed.
    
    Prototype: prototype production

    LRP: low rate production

    FRP: full rate production
    
    
    """
    
    dev_stages = ['prototype build', 
                    'flight testing', 
                    'preliminary design', 
                    'certification', 
                    'commercially operating']
    
    # assignment values for dev_stage to prod_stage key
    newdvals = [1, 1, 0, 2, 3]
    dev_stage_numdict = {key: val for key, val in zip(dev_stages, newdvals)}

    prod_stages = ['prototype production', 'lrp', 'frp']
    # assign key:val for dev_stage to prod_stage conversion
    prod_stage_dict = {0: 'pre production', 1: 'prototype production', 2: 'lrp', 3: 'frp'}

    if x in dev_stage_numdict:
        return prod_stage_dict[dev_stage_numdict[x]]
    
    
    
def assign_pplant(x):
    
    """ 
    df.apply(lambda x: x) support function
    
    Provides logic and return value for power plant category value grouping.
    
    """
    
    plant_cats = ['electric', 'hybrid electric', 'undisclosed']

    # type conversion
    x = str(x)

    # Winged VTOL
    if 'hybrid' in x.lower():
        # hybrid electric index 1
        x = plant_cats[1]
    elif 'hybrid' not in x.lower() and 'electric' in x.lower():
        # all electric index 0
        x = plant_cats[0]
    else:
        # undisclosed
        x = plant_cats[2]
        
    return x


def assign_autonlevel(x):
    
    """ 
    df.apply(lambda x: x) support function
    
    Provides logic and return value for autonomy level category value grouping.
    
    """
    
    auto_cats = ['semi autonomous', 'autonomous', 'piloted semi autonomous', 'piloted', 'undisclosed']

    # type conversion
    x = str(x)

    if 'semi' in x.lower() and 'pilot' not in x.lower():
        x = auto_cats[0]

    elif 'autonomous' in x.lower() and 'semi' not in x.lower():    
        x = auto_cats[1]
        
    elif 'pilot' in x.lower() and 'semi' in x.lower():    
        x = auto_cats[2]

    elif x.lower() == 'piloted':
        x = auto_cats[3]
        
    else:
        # undisclosed
        x = auto_cats[4]
        
    return x