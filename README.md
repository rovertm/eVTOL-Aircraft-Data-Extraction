# eVTOL Aircraft Data Extraction and Analysis

Web scraping tools for eVTOL aircraft data extraction maintaining a dataframe

## Table of Contents

1. [About](#about)
2. [Use Cases](#use_cases)
3. [Installation](#installation)
5. [File Descriptions](#files)
7. [Licensing, Authors, and Acknowledgements](#licensing)
8. [View the notebooks](#notebooks)

## About <a name="about"></a>

This repository contains tools for scraping eVTOL aircraft data from two websites:

1. https://evtol.news/
2. https://transportup.com/

Each set of scraper functions, contained in individual packages, follows an identical process architecture show below.

![scraper_flow](evtol_scrape_flowchart.jpeg)


## Use Cases <a name="use_cases"></a>

Source data for:

* Market research
* Competitive intelligence

## Installation <a name="installation"></a>

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) 
* Standard libraries across Python 3* Anaconda distribution.


## File Descriptions <a name="files"></a>

* Jupyter Notebook for analysis: 

    * evtolnews_scrape.ipynb
    * transportup_scrape.ipynb

* Python files for custom functions

    * transportup_funcs.py
    * evtolnews_scrapefuncs.py

* .csv files for read and writing to directory and results dataframes

    * tu_directory_{date}.csv --> dataframe of aircraft links (to scrape)
    * tu_results_df_{date}.csv --> dataframe of scraped and cleaned aircraft data
    
    * evtolnews_directory_{date}.csv --> dataframe of aircraft links (to scrape)
    * evtolnews_results_df_{date}.csv --> dataframe of scraped and cleaned aircraft data


## Licensing, Authors, Acknowledgements<a name="licensing"></a>

All code is open for any and all usage.

## View the notebooks <a name="notebooks"></a>

View the evtol.news scraper at Jupyter's NBviewer site, [click here.](https://nbviewer.jupyter.org/github/rovertm/evtol_scraper/blob/main/evtolnews_scrape/evtolnews_scrape.ipynb)

View the TransportUP scraper at Jupyter's NBviewer site, [click here.](https://nbviewer.jupyter.org/github/rovertm/evtol_scraper/blob/main/transportup_scrape/transportup_scrape.ipynb)


