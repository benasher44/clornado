
# std libs
import os
from optparse import OptionParser

# Third Party libs
from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.web

# Our libs
import config
import build
from basehandler import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        context = {'message': 'Hello World'}
        self.render('index.html', context=context)


def get_handlers():
    return [
            (r"/", MainHandler),
            ]
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-p', '--production', action='store_true', dest='production', default=False)
    (options, args) = parser.parse_args()
    #build.main(debug=not options.production)
    settings = config.tornado_settings
    application = tornado.web.Application(get_handlers(), **settings)
    application.debug = not options.production
    server = HTTPServer(application)
    server.listen(
        int(config.application_port),
        address=config.application_ip,
    )
    server.start(1 if not options.production else 0)
    tornado.ioloop.IOLoop.instance().start()
