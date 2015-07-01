from google.appengine.api import users
import webapp2


class RootHandler(webapp2.RequestHandler):
    #Better one for when everything is completed:
    '''
    def get(self):
        current_user = users.get_current_user()
        if current_user is None:
            self.redirect('/welcome')
        else:
            self.redirect('/app')
    '''
    # Temp for while we still oly have grades page:
    def get(self):
        self.redirect('/app/grades')
redirect =  webapp2.WSGIApplication([("/", RootHandler)])
