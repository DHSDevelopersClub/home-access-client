'''The endpoints server.'''
__author__ = 'Sebastian Boyd', 'Alexander Otavka'
__copyright__ = 'Copyright (C) 2015 DHS Developers Club'

import datetime
import urllib, urllib2, cookielib, sys, re

import endpoints
from protorpc import message_types, remote
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(10)

#from libs.endpoints_proto_datastore.ndb import EndpointsModel
import libs.pytz as pytz

from bs4 import BeautifulSoup

from redirect_handler import redirect
import models
from messages import (ClassroomQueryMessage, ClassroomMessage, ClassroomListMessage,
                      SignupCommandMessage, SignupStateMessage, NextTutorialDateMessage,
                      StudentMessage, StudentListMessage, VerifyStudentMessage,
                      VerifyStudentMessageResponse, GetAuthMessage, State, LoginHAC,
                      LoginHAC, ClassesHAC, AssigmentHAC, ClassHAC, GradeHAC)
from auth_decorators import (requires_student, requires_teacher, requires_root,
                            is_student, is_teacher, is_admin, is_root)

from debug_class_gen import test_gen_classes


WEB_CLIENT_ID = '912907751553-lb6mvsskb62dpre0kje7fbvriracme0m.apps.googleusercontent.com'
ANDROID_CLIENT_ID = ''
IOS_CLIENT_ID = ''
ANDROID_AUDIENCE = ANDROID_CLIENT_ID


def check_signup(classroom, student):
    signedup = False
    for dsid in classroom.signedup_students:
        if student is not None and dsid == student.key.id():
            signedup = True
            break
    return signedup

def search(search, classrooms):
    if search == None: search = ''
    search_list = search.split()
    print len(search_list)
    for c in classrooms:
        c.teacher_object = models.Teacher.get_by_id(c.teacher)
    def match_count(classroom):
        searched_properties = (classroom.room, classroom.teacher_object.name_text,
        classroom.teacher_object.name_prefix)
        match_count = 0
        for string in searched_properties:
            for search in search_list:
                if search.lower() in string.lower():
                    match_count += 1
        return match_count

    # Sort the list of classrooms, then shave off anything with too few search results
    sorted_classrooms = sorted((-match_count(c), c.totalseats - c.takenseats == 0, c.teacher_object.name_text, c) for c in classrooms)
    if search == '':
        shaved_classrooms = [i[3] for i in sorted_classrooms]
    else:
        shaved_classrooms = [i[3] for i in sorted_classrooms if abs(i[0]) > len(search_list) / 2]
    return shaved_classrooms

def signup_simple(student, classroom):
    person = student.key.id()
    classroom.signedup_students.append(person)
    classroom.put()

def unsignup_simple(student, classroom):
    person = student.key.id()
    try:
        classroom.signedup_students.remove(person)
        classroom.put()
    except:
        pass

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def get_next_tutorial():
    local_tz = pytz.timezone('America/Los_Angeles')
    d = datetime.datetime.now().replace(tzinfo=pytz.utc)
    d = d.astimezone(local_tz)
    next_wednesday = next_weekday(d, 2)
    next_friday = next_weekday(d, 4)
    if next_wednesday < next_friday:
        return next_wednesday
    else:
        return next_friday


@endpoints.api(name='dhstutorial', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID])
class DHSTutorialAPI(remote.Service):
    '''Mediates between client and datastore.'''

    @endpoints.method(message_types.VoidMessage, message_types.VoidMessage,
                      name='gen_debug_classes')
    @requires_root
    def gen_debug_classes(self, request, user_entity):
        test_gen_classes(get_next_tutorial())
        return message_types.VoidMessage()

    @endpoints.method(SignupCommandMessage, SignupStateMessage, name='signup')
    @requires_student
    def signup(self, request, user_entity):
        '''Add or remove a signup for the current user on a specific date.

        If the current user is already signedup for another class on the specified date, their
        signup will be removed from that class so they can only be signed up for one class per date.
        '''
        dsid = request.dsid
        signup = request.signup

        parent_key = ndb.Key('Date', int(request.parent_id))
        classroom = models.Classroom.get_by_id(int(dsid), parent=parent_key)
        if classroom == None:
            return SignupStateMessage(signedup=False,
                                      status=Status.INVALID_ID)

        #Check if signedup
        try:
            dsid = user_entity.key.id()
        except:
            raise endpoints.UnauthorizedException("Not student")
        print dsid
        qry = models.Classroom.query(models.Classroom.signedup_students == dsid).fetch()
        if qry == []:
            signedup = False
            signedup_here = False
        else:
            signedup = True
            signedup_here = check_signup(classroom, user_entity)
        if signedup_here == signup:
            # Already have what you want
            return SignupStateMessage(signedup=signedup_here,
                                      status=Status.ALREADY_DONE)
        elif signedup == False:
            # Not signed up but want to be
            signup_simple(user_entity, classroom)
        elif signedup_here == True:
            # Already signedup here don't want to be
            unsignup_simple(user_entity, classroom)
        elif signedup == True:
            # Signed up in diffrent classroom somthing is wrong
            unsignup_simple(user_entity, qry[0])
            signup_simple(user_entity, classroom)

        return SignupStateMessage(signedup=signup)

    @endpoints.method(ClassroomQueryMessage, ClassroomListMessage, name='list_classes')
    @requires_student
    def list_classes(self, request, user_entity):
        '''List classes on a given date that match the given search.

        A search of either '' or None will return all classes.
        '''
        date = datetime.datetime.strptime(request.date, '%Y-%m-%d')
        qry = models.Date.query(models.Date.date == date)
        try:
            result = qry.fetch(1)[0]
        except IndexError:
            return ClassroomListMessage(classrooms=[])
        date_key = result.key
        qry_result = models.Classroom.query(ancestor=date_key).fetch()
        filtered = search(request.search, qry_result)
        # Move signup class to top
        for classroom in filtered:
            if check_signup(classroom, user_entity):
                filtered.insert(0, filtered.pop(filtered.index(classroom)))

        return ClassroomListMessage(classrooms=[
            ClassroomMessage(
                dsid=str(classroom.key.id()),
                teacher='{} {}'.format(classroom.teacher_object.name_prefix, classroom.teacher_object.name_text),
                profilepic=classroom.teacher_object.profilepic,
                room=classroom.room,
                totalseats=classroom.totalseats,
                takenseats=classroom.takenseats,
                parent_id=str(date_key.id()),
                signedup=check_signup(classroom, user_entity))
            for classroom in filtered])

    @endpoints.method(message_types.VoidMessage, NextTutorialDateMessage, name='next_tutorial')
    def next_tutorial(self, request):
        '''Get the date of the next tutorial after this moment.

        If we are in the middle of a tutorial right now, today's date will be returned.
        '''
        # TODO: Sebastian, make it return today's date if we are in the middle of a tutorial.
        str_date = get_next_tutorial().strftime('%Y-%m-%d')
        return NextTutorialDateMessage(date=str_date)

    @endpoints.method(message_types.VoidMessage, StudentListMessage, name='list_students')
    @requires_teacher
    def list_students(self, request, user_entity):
        date = datetime.datetime.strptime(request.date, '%Y-%m-%d')
        qry = models.Date.query(models.Date.date == date)
        try:
            result = qry.fetch(1)[0]
        except IndexError:
            return StudentListMessage(students=[])
        date_key = result.key
        user_dsid = user_entity.key.id()
        print user_dsid
        qry = models.Classroom.query(models.Classroom.teacher == user_dsid).fetch()

    @endpoints.method(VerifyStudentMessage, VerifyStudentMessageResponse, name='verify_student')
    @requires_teacher
    def verify_student(self, request, user_entity):
        pass

    @endpoints.method(message_types.VoidMessage, GetAuthMessage, name='get_auth')
    def get_auth(self, request):
        current_user = endpoints.get_current_user()
        if is_student(current_user) != None:
            return GetAuthMessage(auth=GetAuthMessage.AuthLevel.STUDENT)
        if is_teacher(current_user) != None:
            return GetAuthMessage(auth=GetAuthMessage.AuthLevel.TEACHER)
        if is_admin(current_user) != None:
            return GetAuthMessage(auth=GetAuthMessage.AuthLevel.ADMIN)
        if is_root(current_user) != None:
            return GetAuthMessage(auth=GetAuthMessage.AuthLevel.ROOT)
        return GetAuthMessage(auth=GetAuthMessage.AuthLevel.NO_USER)


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
            classes_list.append(ClassHAC(assignments=assignment_list, title=class_title, grade_table=grade_list, grade_percent=grade_percent, grade_letter=grade_letter))

        return ClassesHAC(classes=classes_list, status=login_status)

application = endpoints.api_server([DHSTutorialAPI, HomeAccessClientApi])
