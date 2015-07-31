'''The endpoints server.'''
__author__ = 'Sebastian Boyd', 'Alexander Otavka'
__copyright__ = 'Copyright (C) 2015 DHS Developers Club'

import datetime
import urllib, urllib2, cookielib, sys, re
import hashlib, hmac

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

def verify_email(api_key, token, timestamp, signature):
    return signature == hmac.new(
                             key=api_key,
                             msg='{}{}'.format(timestamp, token),
                             digestmod=hashlib.sha256).hexdigest()

def get_grades(username, password):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
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
    response = {'classes': classes_list, "status": login_status}
    return response

def search_classrooms(query, classrooms):
    if query == None: query = ''
    if query == '': return False
    query_list = query.split()
    def match_count(classroom):
        queryed_properties = (classroom.title)
        match_count = 0
        for string in queryed_properties:
            for query in query_list:
                if query.lower() in string.lower():
                    match_count += 1
        return match_count

    # Sort the list of classrooms, then take best result
    sorted_classrooms = sorted((-match_count(c), c) for c in classrooms)
    if len(sorted_classrooms) == 0:
        return False
    else:
        classroom = sorted_classrooms[0]
    return classroom

def send_mail(sender, to, subject, text, html=None, campaign=None):
        api_key = 'REDACTED'
        url = 'https://api.mailgun.net/v3/sebastianboyd.com'
        deadline = 5
        payload = {}
        payload['from'] = sender
        payload['to'] = to
        payload['subject'] = subject
        payload['text'] = text
        if html:
            payload['html'] = html
        if campaign:
            payload['o:campaign'] = campaign
        encoded_payload = urllib.urlencode(payload)
        base64string = base64.encodestring('api:' + api_key).replace('\n', '')
        headers = {}
        headers['Authorization'] = "Basic %s" % base64string
        result = urlfetch.fetch(url, deadline=deadline, payload=encoded_payload, method=urlfetch.POST, headers=headers)
        return result

@endpoints.api(name='homeaccessclient', version='v1')
class HomeAccessClientApi(remote.Service):
    @endpoints.method(LoginHAC, ClassesHAC, name='login',
                      allowed_client_ids=[WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID])
    def login(self, request):
        response = get_grades(request.username, request.password)
        return ClassesHAC(classes=response["classes"], status=response["login_status"])

    # Text Message refers to text based communication; sms, email
    @endpoints.method(TextMessage, ClassesHAC, name='incomingtextrequest')
    def incomingtextrequest(self, request):
        mailgun_api_key = ''
        wit_token = 'WQPZ2RUGURGQSQKZNVLDPTGBISP7QZ35'
        if varify_email(api_key, request.token, request.imestamp, request.signature):
            return # Add failure code
        wit_request = urllib2.Request("https://api.wit.ai/message?v=20150731&q=" + request.stripped-text,
                                  headers={"Authorization": "Bearer " + wit_token})
        contents = json.loads(urllib2.urlopen(wit_request).read())
        query = contents["outcomes"][0]["entities"]["search_query"][0]["value"]
        grades = get_grades(username, password)
        if grades["status"] == ClassesHAC.LoginStatus.OK:
            classroom = search_classrooms(query, grades["classes"])
            if classroom:
                send_mail("<Grades> grades@txt.sebastianboyd.com", , )
application = endpoints.api_server([HomeAccessClientApi])
