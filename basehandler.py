import simplejson

from tornado.web import RequestHandler

class BaseHandler(RequestHandler):
    """
    A base class for request handlers.
    """
    def json(self, dictionary):
        """ Writes a json response, and sets the json header. """
        self.set_header("Content-Type", "application/json")
        return self.write(simplejson.dumps(dictionary))
