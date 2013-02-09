# Third Party libs
import tornado.web

# std libs
from optparse import OptionParser

# Our libs
import config
import build
from basehandler import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        context = {'Message': 'Hello World'}
        self.render('index.html', context=context)


def get_handlers():
    return [
            (r"/", MainHandler),
            ]
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-p', '--production', action='store_true', dest='production', default=False)
    (options, args) = parser.parse_args()
    build.main(debug=not options.production)
    settings = config.tornado_settings
    application = tornado.web.Application(get_handlers(), **settings)
    application.debug = config.debug
    server = HTTPServer(application)
    server.listen(
        int(os.environ.get(config.get('application_port'), 8080)),
        address=os.environ.get(config.get('application_ip'), "127.0.0.1")
    )
    server.start(0)
    IOLoop.instance().start()
