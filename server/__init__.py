'''The endpoints server.'''
__author__ = 'Sebastian Boyd', 'Alexander Otavka'
__copyright__ = 'Copyright (C) 2015 DHS Developers Club'

import datetime
import urllib, urllib2, cookielib, sys, re

import endpoints
from protorpc import message_types, remote
from google.appengine.api import urlfetch

#from libs.endpoints_proto_datastore.ndb import EndpointsModel

from bs4 import BeautifulSoup

import models
from messages import (LoginHAC, ClassesHAC, AssigmentHAC, ClassHAC, GradeHAC)


WEB_CLIENT_ID = '981058069504-rjcfv5tc2msk8qvmu42uedqetforee0t.apps.googleusercontent.com'
ANDROID_CLIENT_ID = ''
IOS_CLIENT_ID = ''
ANDROID_AUDIENCE = ANDROID_CLIENT_ID

@endpoints.api(name='homeaccessclient', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID])
class HomeAccessClientApi(remote.Service):
    @endpoints.method(LoginHAC, ClassesHAC, name='login')
    def login(self, request):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        username = request.username
        password = request.password
        database = '10'
        login_data = urllib.urlencode({'Database' : database, 'LogOnDetails.UserName' : username, 'LogOnDetails.Password' : password})
        opener.open('https://home.tamdistrict.org/HomeAccess/Account/LogOn', login_data, 15)
        if [cookie for cookie in cj if cookie.name == ".AuthCookie"] == []:
            login_status = ClassesHAC.LoginStatus.LOGIN_ERROR
        else:
            login_status = ClassesHAC.LoginStatus.OK
        resp = opener.open('https://home.tamdistrict.org/HomeAccess/Content/Student/Assignments.aspx', None, 15)
        html = resp.read()
        html = html.decode('utf8', 'ignore')
        soup = BeautifulSoup(html)
        charts = soup.find_all('table')
        classes_list = []
        for classroom_soup in soup.find_all("div", { "class" : "AssignmentClass"}):
            class_title = classroom_soup.find_all("div", class_="sg-header sg-header-square")[0].find_all("a")[0].string.strip()
            assignment_list = []
            try:
                for tr in classroom_soup.find("table", class_="sg-asp-table").find_all("tr", class_="sg-asp-table-data-row"):
                    td = tr.find_all("td")
                    due = td[0].string
                    assigned = td[1].string
                    assigment_title = td[2].find_all("a")[0].string.strip()
                    assignment_category = td[3].string.strip()
                    score_my = td[4].string.strip()
                    score_total = td[5].string.strip()
                    assignment = AssigmentHAC(title=assigment_title, category=assignment_category,
                                                    date_assigned=assigned, date_due=due,
                                                    score=score_my, max_score=score_total)
                    assignment_list.append(assignment)
            except:
                continue
            grade_list = []
            for tr in classroom_soup.find("div", class_="sg-view-quick sg-clearfix").find("table", class_="sg-asp-table").find_all("tr", class_="sg-asp-table-data-row"):
                td = tr.find_all("td")
                length = len(td)
                grade_items_docs = ["grade_category", "points", "max_points", "percent", "weight", "weighted_points"]
                grade_items = []
                for t in td:
                    grade_items.append(t.string.strip())
                while len(grade_items) < 6:
                    grade_items.append('')
                grade = GradeHAC(category=grade_items[0], weight=grade_items[4], score=grade_items[1],
                                max_score=grade_items[2], percent=grade_items[3],
                                weighted_points=grade_items[5])
                grade_list.append(grade)
            grade_str = classroom_soup.find("span", id=re.compile("plnMain_rptAssigmnetsByCourse_lblOverallAverage_\d")).string
            p = re.compile(r'\(([^\)]+)\)')
            grade_percent = re.sub(r'\([^)]*\)', '', grade_str).strip()
            try:
                grade_letter = p.search(grade_str).group(1)
            except:
                grade_letter = ''
            print("done")
            classes_list.append(ClassHAC(assignments=assignment_list, title=class_title, grade_table=grade_list, grade_percent=grade_percent, grade_letter=grade_letter))

        return ClassesHAC(classes=classes_list, status=login_status)

application = endpoints.api_server([HomeAccessClientApi])
