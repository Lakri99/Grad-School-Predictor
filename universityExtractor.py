import requests
from lxml import html
import sys
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import urllib.request
from requests.exceptions import HTTPError
import pandas as pd
import numpy as np
import time
import random
import studentExtractor as S_ex

def open_url_2_soup(url, session_request = None):
    """
    open webpage and convert to beautiful soup object
    returns: page_soup(soup object)
    params: url(str) - url of the page
    
    """
    proxies = [{
        "http": 'http://14.102.81.195:21776', 
        "https": 'http://14.102.81.195:21776'
    }]
    proxy = random.choice(proxies)
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    if(session_request == None):
        page = requests.get(url, headers = headers,verify = False, allow_redirects = False)
    else:
        page = session_request.get(url, headers = headers,verify = False, allow_redirects = False)
    if(page.status_code == 200):
        page_soup = soup(page.content,'lxml')
        return page_soup
    elif(page.status_code == 302):
        print("error code : ",page.status_code)
        print(url)
        time.sleep(900)
        token,session_req = S_ex.getAuthSession()
        open_url_2_soup(url, session_req)
    else:
        print(page.status_code)
        raise HTTPError()


def getUniversityLookup(url):
    """
    get the list of university and it's basic info from ONE page
    returns : univ_df - dataframe containing name,key and url of universities one page at a time
    params: url - url of the page
    
    """
    univ_name = []
    univ_link = []
    univ_soup = open_url_2_soup(url)
    univ_detail_tag = univ_soup.findAll("div",{"class":"col-sm-9 col-xs-12"})
    for tag in univ_detail_tag:
        a = tag.find("a",href=True)
        univ_name.append(a.text)
        univ_link.append("https://yocket.in"+a['href'])
    #data cleaning 
    univ_df = pd.DataFrame({"name":np.asarray(univ_name),"href": np.asarray(univ_link)})
    print(univ_df['name'].str.split('(',n = 1, expand = True))
    univ_df[['name','keys']] = univ_df['name'].str.split('(',n = 1, expand = True)
    univ_df['keys'] = univ_df['keys'].apply(lambda x: x[:-1])
    return univ_df


def getUniversityList():
    """
    creates a csv file of all university detail
    returns: UniversityList_df - dataframe containg the basic details of top 500 engineering schools
    params: None
    
    """
    UniversityList_df = pd.DataFrame()
    count = 1
    while(count <= 16):
        url = "https://yocket.in/universities?page=" + str(count)
        temp_df = getUniversityLookup(url)
#         print(temp_df)
        UniversityList_df = UniversityList_df.append(temp_df,ignore_index=True)
#         print(UniversityList_df)
        time.sleep(5) 
        count += 1
    UniversityList_df.to_csv('universityList.csv', encoding='utf-8')
    return UniversityList_df

def getUniversityDetail(url):
    """
    get the details of a single university
    params: url(string) - url of the site
    returns : univ_detail(dict) - dictionary containing details of a single university
    
    """
    univ_detail = {}
    page_soup = open_url_2_soup(url)
    univ_tag = page_soup.findAll("div",{"class":"col-sm-3 col-xs-6"})
    univ_detail['name'] = page_soup.findAll("h1")[0].text
    tag_no = 1
    for tag in univ_tag:
        if(tag_no in [1,2,3,4,6,8,9]):
            name,data = extractUnivDetails(tag,tag_no)
            univ_detail[name] = data
        tag_no+= 1
    try:
        univ_detail['admitList'] = univ_detail['student_link']+"2"
        univ_detail['rejectList'] = univ_detail['student_link']+"3"
        univ_detail['appliedList'] = univ_detail['student_link']+"1"
        del univ_detail['student_link']
    except:
        univ_detail['admitList'] = None
        univ_detail['rejectList'] = None
        univ_detail['appliedList'] = None
        del univ_detail['student_link']
    return(univ_detail)


def extractUnivDetails(tag,tag_no):
    """
    returns : univ_dict(dictionary) - dictionary containing university(single) detail
    params: tag(soup element) - the div containing the element
            tag_no(int) - number of div
    """
    univ_dict = {}
    if(tag_no in [1,2,8,9]):
        return(tag.h3.small.text,(tag.br.previous_sibling)[1:])
    elif(tag_no ==3):
        return (tag.h3.findAll("small")[1].text,tag.h3.find("small").previous_sibling)
    elif(tag_no ==4):
        return (tag.h3.findAll("small")[1].text,(tag.h3.find("small").previous_sibling)[2:])
    elif(tag_no == 6):
        try:
            a = tag.findAll("a",href=True)[0]
        except:
            return("student_link",None)
        else:
            return("student_link",("https://yocket.in"+a['href'])[:-1])


def univDetail_to_csv():
    """
    generate csv file containing university details
    params : None
    returns : None
    """
    univ_list = pd.read_csv('universityList.csv')
    univ_list = pd.DataFrame(univ_list)
    universityDetail = pd.DataFrame()
    counter = 51
    while(counter <= 100):
        link = univ_list.iloc[counter]['href']
        dict_temp = getUniversityDetail(link)
        universityDetail = universityDetail.append(dict_temp,ignore_index = True)
        print(counter)
        counter += 1
        time.sleep(10)
#     print(universityDetail)
    universityDetail.to_csv('universityDetailList.csv', encoding='utf-8',header = False,mode = 'a')

