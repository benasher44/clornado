from collections import OrderedDict
import config
import fnmatch
from optparse import OptionParser
import os
import shutil
import scss
import subprocess
import sys

JAVASCRIPT_BASE_TEMPLATE = """goog.provide('%s');
"""

class BuildEngine:
    """
    Builds and compiles GSS, Closure js and application js, and mustache
    templating system.
    """

    def __init__(self, debug=True):
        self.appName = config.app_name.lower()
        self.debug = debug
        self.libPath = config.build_paths['lib_path'] + "/" 
        self.jarPath = config.build_paths['jar_path'] + "/"
        self.projRoot = config.base_path + '/'
        self.srcPath = config.build_paths['src_path'] + "/"
        self.staticPath = config.build_paths['static_path'] + "/"
        self.templatePath = config.build_paths['template_path'] + "/"

    def printSectionHeader(self, secName):
        numDashes = max([len(line) for line in secName.split('\n')])

        print '-' * numDashes
        print secName
        print '-' * numDashes

    def printMsg(self, msg):
        print '- ' + msg

    def ifind(self, match, inFolder):
        matches = []
        for root, dirnames, filenames in os.walk(inFolder):
            for filename in fnmatch.filter(filenames, match):
                yield os.path.join(root, filename)

    
    def checkAppRoots(self):
        #TODO: check template roots

        # check js roots
        jsAppRoot = self.srcPath + 'js/' + self.appName
        if not os.path.exists(jsAppRoot):
            os.makedirs(jsAppRoot)

        initFilePath = jsAppRoot + '/init.js'
        if not os.path.exists(initFilePath):
            with open(initFilePath, 'w') as initFile:
                initFile.write(JAVASCRIPT_BASE_TEMPLATE % self.appName)

        scssSrcRoot = self.srcPath + 'scss'
        if not os.path.exists(scssSrcRoot):
            os.makedirs(scssSrcRoot)

    def cleanBuild(self):
        # intelligently clean
        # whether or not the static/js directory is symlink and the debug flag should match
        needsClean = os.path.islink(self.staticPath + 'js') == self.debug
        if not needsClean:
            return
        
        self.printSectionHeader('Cleaning Directory structure')

        self.printMsg('Deleting compiled js files...')
        if os.path.islink(self.staticPath + 'js'):
            os.unlink(self.staticPath + 'js')
            os.unlink(self.staticPath + 'lib')
        else:
            shutil.rmtree(self.staticPath + 'js', ignore_errors=True)
            shutil.rmtree(self.staticPath + 'lib', ignore_errors=True)

        self.printMsg('Deleting compiled style sheets...')
        shutil.rmtree(self.staticPath + 'css', ignore_errors=True)
        
        self.printMsg('Deleting compiled Scss assets...')
        shutil.rmtree(self.staticPath + 'sassets', ignore_errors=True)
        
        self.printMsg('Clean complete!')

    def installPythonDeps(self):
        self.printSectionHeader('Installing Python Dependencies')
        subprocess.check_call(['pip', 'install', '-r', self.projRoot + 'requirements.txt'])

    def compileScss(self):
        self.printSectionHeader('Compiling Scss Files')
        
        # scss settings
        scss.STATIC_ROOT = self.staticPath
        scss.STATIC_URL = '/static/'
        scss.ASSETS_ROOT = scss.STATIC_ROOT + 'sassets/'
        scss.ASSETS_URL = scss.STATIC_URL + 'sassets/'
        
        # make sure the directories we need are there
        outputDir = self.staticPath + 'css'
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        
        if not os.path.exists(scss.ASSETS_ROOT):
            os.makedirs(scss.ASSETS_ROOT)

        # find some files to compile
        scssFiles = OrderedDict()
        for filepath in self.ifind('*.scss', self.srcPath + 'scss'):
            with open(filepath, 'r') as scssFile:
                self.printMsg(filepath)
                scssFiles[filepath] = scssFile.read()

        # compile
        if len(scssFiles) > 0:
            _scss = scss.Scss(
                    scss_opts={
                        'compress': not self.debug,
                        'debug_info': self.debug,
                        }
                    )

            _scss._scss_files = scssFiles
            scssOutput = _scss.compile()
            with open(self.staticPath + 'css/app.css', 'w') as cssFile:
                cssFile.write(scssOutput)

        self.printMsg('Style build complete!')

    def compileClosure(self):

        if not os.path.exists(self.staticPath):
            os.mkdir(self.staticPath)

        if self.debug:
            os.symlink(os.path.abspath(self.srcPath + 'js'), self.staticPath + 'js')
            os.symlink(os.path.abspath(self.libPath + 'js'), self.staticPath + 'lib')
        else:
            outputDir = self.staticPath + 'js'
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
        
        self.printSectionHeader('Compiling JS Files')
        if self.debug:
            cmd = 'cd ' + self.staticPath + 'lib && python closure-library/closure/bin/build/depswriter.py --root="../js" > ../deps.js'
            self.printMsg(cmd)
            subprocess.check_call(cmd, shell=True)
        else:
            jsPath = os.path.abspath(self.srcPath + 'js')
            libPath = os.path.abspath(self.libPath + 'js')
            cmd = ['python', libPath + '/closure-library/closure/bin/build/closurebuilder.py',
                    '--root=' + libPath,
                    '--root=' + '/'.join([jsPath, self.appName]), 
                    '--compiler_jar=' + self.jarPath + 'closure-compiler.jar', 
                    '--output_mode=compiled',
                    '--namespace=' + self.appName,
                    '--output_file=' + self.staticPath + 'js/compiled.js'
                    ]
            self.printMsg(' '.join(cmd))
            subprocess.check_call(cmd)

        self.printMsg('JavaScript build complete!')

    def compileMustache(self):
        #TODO: Finish this
        pass

    def run(self):
        print 'DEBUG: ' + str(self.debug)

        self.cleanBuild()
        self.checkAppRoots()

        self.installPythonDeps()

        self.compileScss()
        self.compileMustache()
        self.compileClosure()
        
        print "Done!"
        return 0

def main(debug=True):
    return BuildEngine(debug).run()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--prod', action='store_true', dest='prod', default=False)
    (options, args) = parser.parse_args()
    debug = not options.prod
    BuildEngine(debug).run()
