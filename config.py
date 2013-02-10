import os.path

import template_methods
#import uimodules

base_path = os.path.abspath(os.path.dirname(__file__))
app_name = 'helloworld'

tornado_settings = {
    'cookie_secret': 'clornado', #TODO: Solve the issue of unique cookies and security
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
