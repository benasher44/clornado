import base64
import os.path
import uuid

import template_methods
#import uimodules

base_path = os.path.abspath(os.path.dirname(__file__))
app_name = 'helloworld'

if not os.path.exists(os.path.join(base_path, 'secret.py')):
    with open('secret.py', 'w') as secret_file:
        secret_file.write('secret = "%s"\n' % base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))

import secret

tornado_settings = {
    'cookie_secret': secret.secret,
    'gzip': True,
    'login_url': '/login', #TODO: Investigate static_handler_class
    'static_path': os.path.join(base_path, 'static'),
    'template_path': os.path.join(base_path, 'templates'),
    'ui_methods': template_methods,
    #'ui_modules': uimodules,
    'xsrf_cookies': True,

}

build_paths = {
    'static_path': tornado_settings['static_path'],
    'template_path': tornado_settings['template_path'],
    'mustache_path': os.path.join(tornado_settings['template_path'], 'mustache'),
    'partials_path': os.path.join(tornado_settings['template_path'], 'mustache/partials'),
    'lib_path': os.path.join(base_path, 'lib'),
    'src_path': os.path.join(base_path, 'src'),
    'jar_path': os.path.join(base_path, 'lib/jar'),
}

application_port = 8080
application_ip = '127.0.0.1'
