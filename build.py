import config
from optparse import OptionParser
import shutil
import os
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
    
    def checkAppRoots(self):
        #TODO: check scss and template roots

        # check js roots
        jsAppRoot = self.srcPath + 'js/' + self.appName
        if not os.path.exists(jsAppRoot):
            os.makedirs(jsAppRoot)

        initFilePath = jsAppRoot + '/init.js'
        if not os.path.exists(initFilePath):
            with open(initFilePath, 'w') as initFile:
                initFile.write(JAVASCRIPT_BASE_TEMPLATE % self.appName)

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
        
        self.printMsg('Clean complete!')

    def installPythonDeps(self):
        self.printSectionHeader('Installing Python Dependencies')
        subprocess.check_call(['pip', 'install', '-r', self.projRoot + 'requirements.txt'])

    def compileGssFiles(self):
        """ The GSS build step """
        outputDir = self.staticPath + 'css'

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        gss_cmd = ['java',
                '-jar', self.jarPath + 'closure-stylesheets.jar', self.srcPath + 'gss/*.gss',
                '--output-file', self.staticPath + 'css/app.css',
                '--rename']

        if self.debug:
            gss_cmd.extend(['NONE', '--pretty-print'])
        else:
            gss_cmd.append('NONE')

        self.printSectionHeader('Compiling GSS Files')
        commandToRun = ' '.join(gss_cmd)
        self.printMsg(commandToRun)
        subprocess.check_call(commandToRun, shell=True)

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
            cmd = 'cd ' + self.staticPath + 'lib && python closure-library/closure/bin/build/depswriter.py --root="../js" > deps.js'
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
