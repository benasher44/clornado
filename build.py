import fnmatch
from optparse import OptionParser
import shutil
import glob
import os
import string
import subprocess
import sys

class BuildEngine:

    def __init__(self, debug=False, clean=False):
        self.debug = debug
        self.clean = clean
        relPath = os.path.abspath(os.path.dirname(__file__)) + '/'
        self.libPath = relPath + 'lib/'
        self.jarPath = self.libPath + 'jar/'
        self.srcPath = relPath + 'src/'
        self.staticPath = relPath + 'static/'


    def printSectionHeader(self, secName):
        print '-' * len(secName)
        print secName
        print '-' * len(secName)


    def printMsg(self, msg):
        print '- ' + msg


    def cleanBuild(self):
        self.printSectionHeader('Cleaning Directory structure')

        self.printMsg('Deleting compiled js files...')
        if os.path.islink(self.staticPath + 'js'):
            os.unlink(self.staticPath + 'js')
        else:
            shutil.rmtree(self.staticPath + 'js', ignore_errors=True)

        self.printMsg('Deleting compiled style sheets...')
        shutil.rmtree(self.staticPath + 'css', ignore_errors=True)
        
        self.printMsg('Clean complete!')


    def compileGssFiles(self):
        outputDir = self.staticPath + 'css'

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        gss_cmd = ['java',
                '-jar', self.jarPath + 'closure-stylesheets.jar', self.srcPath + 'gss/*.gss',
                '--output-file', self.staticPath + '../static/css/app.css',
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

    def compileClosure(self, debug):
        if debug:
            os.symlink(os.path.abspath(self.srcPath + 'js'), self.staticPath + 'js')
            os.symlink(os.path.abspath(self.libPath + 'js'), self.staticPath + 'lib')
        else:
            outputDir = self.staticPath + 'js'
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)
        
        self.compileSoy()
        
        self.printSectionHeader('Compiling JS Files')
        if debug:
            cmd = 'cd ' + self.staticPath + 'lib && python closure-library/closure/bin/build/depswriter.py --root_with_prefix="app ../../../../js" > deps.js'
            self.printMsg(cmd)
            subprocess.check_call(cmd, shell=True)
        else:
            jsPath = os.path.abspath(self.srcPath + 'js')
            libPath = os.path.abspath(self.libPath + 'js')
            cmd = ['python', libPath + '/closure-library/closure/bin/build/closurebuilder.py',
                    '--root=' + libPath,
                    '--root=' + jsPath, 
                    '--compiler_jar=' + self.jarPath + 'closure-compiler.jar', 
                    '--output_mode=compiled',
                    '--namespace=LoanLit',
                    '--output_file=' + self.staticPath + 'js/app.js'
                    ]
            self.printMsg(' '.join(cmd))
            subprocess.check_call(cmd)

        self.printMsg('JavaScript build complete!')


    def run(self):
        print 'DEBUG: ' + str(self.debug)

        if self.clean:
            self.cleanBuild()

        self.compileGssFiles()
        self.compileClosure(debug)
        
        print "Done!"
        return 0

def main(debug=False, clean=False):
    return BuildEngine(debug, False).run()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False)
    parser.add_option('-c', '--clean', action='store_true', dest='clean', default=False)
    (options, args) = parser.parse_args()
    BuildEngine(options.debug, options.clean).run()
