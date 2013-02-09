import os

import pystache

import config

def closure_includes(self):
    closure_include = lambda dep: "<script type='text/javascript' src='%s'></script>" % self.static_url(dep)

    if self.application.debug:
        scripts = [
                'js/closure-library/closure/goog/base.js',
                'js/deps.js',
                ]
    else:
        scripts = ['js/loanlit.js']
    includes_str = '\n'.join([closure_include(script) for script in scripts])

    if self.application.debug:
        includes_str += "<script type='text/javascript'>goog.require('LoanLit.app');</script>"

    return includes_str

def mustache_template(self, namespace, data):
    """
    Takes a namespace and finds it's file.  Takes that file and parses it's
    template.  Then takes that template, loads the partials for it, and
    renderers the template, given the data and the partials.
    """
    partials_path = config.build_paths['partials_path'] + "/"

    paths = namespace.split('.') 
    file_path = '/'.join(paths) + '.mustache'
    partials = dict()
    if self.application.debug == True:
        with open(config.build_paths['mustache_path'] + '/' + file_path) as f:
            read_data = f.read()
        read_data = unicode(read_data)
        for (dirpath, dirname, filenames) in os.walk(partials_path):
            dirpath += '/' if not dirpath.endswith('/') else ''
            new_namespace = dirpath.replace(partials_path, '')
            new_namespace = new_namespace.replace('/', '.')
            for filename in filenames:
                if filename.endswith('.mustache'):
                    with open(dirpath + filename) as f:
                        read_file = f.read()
                    filename = filename.replace(".mustache", "")
                    partials[new_namespace + filename] = read_file


        parsed_template = pystache.parse(read_data)
        renderer = pystache.Renderer(partials=partials)
        return renderer.render(parsed_template, data)
    else:
        return 'no bueno'
