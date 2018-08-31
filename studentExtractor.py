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
import universityExtractor as U_ex

def getAuthSession():
    """
    generate session with login credentials
    params: None
    returns: token(string) - the csrf token value
             session_requests(session object): session with login posted
    """
    USERNAME = "studytonightrb@gmail.com"
    PASSWORD = "priyabashyam"
    LOGIN_URL = "https://yocket.in/account/login"
    session_requests = requests.session()
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
    result = session_requests.get(LOGIN_URL, verify = False, headers = headers)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrfToken']/@value")))[0]
    payload = {
        "email": USERNAME,
         "password": PASSWORD,
         "_csrfToken": authenticity_token
    }

    # Perform login
    login_req = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
    return (authenticity_token,session_requests)


def getStdList(page_soup,admit_status):
    """
    calculates the details of user for a single page
    params : admit_status(string) - admit/reject string
             page_soup(soup object) - soup of each page of student list of a university
    returns: dataframe containing user detail from a single page
    """
    name_tag = page_soup.findAll("input" , {"id" : "users-view-search-universities"})[0]
    name = name_tag['value']
    grading = page_soup.findAll("div",{"class" : "col-sm-6"})[1:]
#     print(grading[0])
    student_df = pd.DataFrame()
    for tag in grading:
#         print(tag)
        std_data = {}
        std_data['college'] = name
        std_data['admit/reject'] = admit_status
        a = tag.findAll("a",href = True)[0]
#         print(a)
        std_data['Name'] = a.text #Tag for name of student
#         std_data['studentLink'] - a['href']
        std_data['CourseName'] = tag.find("small").text #Tag for course
        student_data_tag = tag.findAll("div",{"class":"col-sm-3 col-xs-6"})
        for data_tag in student_data_tag:
            heading = data_tag.find("strong").text
            data = data_tag.findNext("br").next_sibling
            if (heading == "GRE"):
                std_data['GRE'] = data.string

            elif(heading == "TOEFL" or heading == "IELTS" or heading == "ENG TEST"):
                std_data['ENG_TEST'] = data.string

            elif(heading == "UNDERGRAD"):
                std_data['CGPA']= data.string

            elif(heading == "WORK EX"):
                std_data['WorkExp'] = data.string
#         print(std_data)
        student_df = student_df.append(std_data, ignore_index=True)
#     print(student_df)
    return student_df


def getStudentDetailList(url,session_request = None, admit = None):
    """
    gets the entire student list for a single university
    params: url(string) - student list url of the university
            session_request(session obejct) - session with login posted
            admit(string) - admit/reject status
    return: student_detail(dataframe) - containg all the student list for a single university
    """
    page_counter = 1
    student_detail = pd.DataFrame()
    url = url + "?page="
    target_url = url + str(page_counter)
    while(page_counter <= 50):
        
        try:
            page_soup = U_ex.open_url_2_soup(target_url,session_request)
        except HTTPError:
            print(target_url)
            print("exception raised")
            page_counter = 1
            break
            
        else:
            print(target_url)
            target_url = url + str(page_counter)
            std_detail_page = getStdList(page_soup,admit)
            student_detail = pd.concat([student_detail,std_detail_page])
            time.sleep(10)
            page_counter += 1
        
    return student_detail


def generateStudentList(start_index):
    """
    generate applied and rejected student detail list for all universities
    params: start_index(int) - start of range to scrape
    returns: None
    """
    token, session_request = getAuthSession()
#     session_request = None
#     print(token)
    student_detail_df = pd.DataFrame(pd.read_csv("universityDetailList.csv", header=1))
    header = False
    for index,row in student_detail_df.iterrows():
        if(index in range(start_index,301)):
            print(index)
        #   if(index == start_index):
            student_admit = getStudentDetailList(row['admitList'], session_request, 'admit')
#             print(student_admit)
            student_admit.to_csv('studentList1.csv', mode = 'a', encoding='utf-8',header = header)
            header = False
            student_reject = getStudentDetailList(row['rejectList'], session_request, 'reject')
            student_reject.to_csv('studentList1.csv', mode='a', encoding = 'utf-8', header = header)
#             time.sleep(120)