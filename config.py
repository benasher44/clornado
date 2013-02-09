import os.path

debug = True
tornado_settings = {
    'cookie_secret': 'clornado', #TODO: Solve the issue of unique cookies and security
    'gzip': True,
    'login_url': '/login', #TODO: Investigate static_handler_class
    'static_path': os.path.join(base_path, 'static'),
    'template_path': os.path.join(base_path, 'templates'),
    'ui_methods': include,
    'ui_modules': uimodules,
    'xsrf_cookies': True,

}

# Uncomment this to change your application port
# application_port = 8080
# application_ip = '127.0.0.1'
