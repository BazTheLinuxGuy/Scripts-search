#!/usr/bin/env python
r'''get_scripts.py, much like its predecessors, 
    will go through all the files in a given "bin" 
    directory (directories of executable programs, such as /usr/bin)
    and sort out which are scripts: sh, POSIX, Python, Perl, Ruby, Lua, 
    or others. 

    It will use a similar mechnism to do
    this as in "get_scripts_in_usr_bin.py"

    What will be markedly different from the other programs, is the use of 
    a Script and Scripts classes to hold the scripts found in the chosen 
    "bin" directory.

    Command-line invocation:
    get_scripts -i / --inputdir: [executable directory, such as /usr/bin or 
                   /usr/local/sbin]
                -o / --outputdir: [/path/to/directory - for writing output]
                                  NOTE: Must be fully qualified
                -v / --verbose: [increase program verbosity, up to 3 -v's
                                 can be used.]
                -r / --generate-report: [create a report showing statistics of scripts]
                -p [parse the list of scripts into categories:
                   Perl Scripts, Python, sh scripots, Ruby, Lua,
                   whatever...] (NOT YET IMPLEMENTED)
                -  s [sort scripts array by some criterion other than size,
                   such as progname or progtype
'''

import regex
import argparse
import logging
from time import sleep
from collections import namedtuple
import stat
import sys
import os


__author__ = 'Bryan A. Zimmer'
__date_of_this_notation__ = 'September 1, 2020 9:50 AM'
__updated__ = 'September 13, 2020 6:00 PM (Sunday)'
__program_name__ = 'get_scripts.py'


HYPHEN = '-'

global args
global fileinfo

fileinfo=('fileinfo','progname','progtype','size')

# For backward compatibility, a stat_result instance is also accessible
# as a tuple of at least 10 integers giving the most important (and
# portable) members of the stat structure, in the order st_mode
# st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
# st_mtime, st_ctime. More items may be added at the end by some
# implementations. For compatibility with older Python versions,
# (from 'stat' documentation).


fileinfo = namedtuple('fileinfo', 'progname, progtype, size')


def startup_housekeeping():
    r'''move this to startup housekeeping()        
            we need the name of the output directory from the 
            argparse routine then something like this'''
    global args

    if args.outputdir.endswith(os.sep):
        args.outputdir = args.outputdir[0:-1]
    replace = HYPHEN
    sfilename = 'scripts-in'
    inputdir = regex.sub(os.sep, HYPHEN, args.inputdir)
    sfile = sfilename + inputdir + '.txt'
    if args.verbose > 0:
        print('sfile =', sfile)
        sleep(2)
    return sfile


def parse_args():
    global args
    r'''The purpose of args here is to get the input directory/ies
    and the output directory where the results of this program will go.
    There is the matter of naming the output files, but that is better
    done elsewhere. Here, we will stick to the command line args.'''
    program = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(description='Parse command line \
for the program.', prog=program)
    parser.add_argument('-i', '--inputdir',
                        help='Input directory, a "bin" dir.',
                        required=True)
    parser.add_argument('-o', '--outputdir',
                        help='Directory to place results into.',
                        required=True)
    parser.add_argument('-v', '--verbose', action='count',
                        default=0, required=False,
                        help='Increase program verbosity')
    parser.add_argument('-r', '--generate=report',
                        action='store_true', required=False, default=False,
                        help='Statistics on the output we produce.')
#    parser.add_argument('-s','--sortby',
#                        default='size',required=False,
#                        action='store_true',
#                        help='sort output file by size, name, or type')
#    parser.parse_args(['-vvv'])
#    Namespace(verbose=3)

    args = parser.parse_args()
    return args


class Script:
    r''' This class creates a 3-tuple for `scripts'
         that are found in the directory listing returned by 
         os.listdir(inputdir)'''

    pg_type = 'single executable script'

    def __init__(self, progname, progtype, size):
        self.scripts = []
        self.progname = progname
        self.progtype = progtype
        self.size = size
#       self.onescript = (self.progname, self.progtype, self.size)
        self.finfo = fileinfo(self.progname, self.progtype, self.size)

    def process_progtype(self):
        r''' This is the method that refines disparate data
             into a refined "script" a 3-tuple consisting, suitable for 
             adding to our list of scripts. Unfortunately, we had to
             create a three-tuple named `script' to avoid dragging in all
             the other paraphernalia of this Script class. So, if the
             instance is created via script=Script(progname, progtype,
             size), the desired 3-tuple result is script.script.
             Sorry about that.'''
        global args
#        global fileinfo

        line = self.finfo.progtype.rstrip()
        n = line.index(':')
        self.progname = line[0:n]
        x = len(line)
        n += 2  # skip over the colon and following space.

        line = line[n:x]  # i.e., what the 'file' command returns,
        # minus the program name - everything
        # following the ': ' returned by the
        # `file' command.
        self.progtype = line

        if self.finfo.progtype.endswith(','):
            self.findo.progtype = self.finfo.progtype[0:-1]
        self.finfo = fileinfo(self.progname, self.progtype, self.size)
        return self.finfo

### -------- End of class Script -------- ###


class Scripts:
    global args

    pg_type = 'executable scripts'

    def __init__(self):
        self.scripts = []
        self.len = 0

    def add(self, script):
        self.scripts.append(script)

    def length(self):
        self.len = len(self.scripts)
        return self.len

    def writefile(self, sfile):
        # Though this output is not meant for the end user,
        # We need to sort by one of the three fields in the
        # named tuplets,
        # this should be contingent on what the user wants
        #        self.sorted_scripts=[]
        
        self.sfile = sfile
# `sort' or `sorted'?
        self.newlist = self.scripts
        self.newlist = sorted(self.scripts, key=lambda finfo:\
                              finfo.size)
# or:    self.scripts.sort(key=lambda script: key=script.progtype)
# the third option, alphabetical (ascending)
# is there by default
        this = os.getcwd()
        print(f'We are now at {this}')
        sleep(2)
        print('We are writing files at {}.'.format(args.outputdir))
        os.chdir(args.outputdir)
        with open(self.sfile, 'w') as f:
            for onescript in self.newlist:
                s1 = onescript.progname
                s1 = s1.rstrip()
                s2 = onescript.progtype
                s2 = s2.rstrip()
                s3 = str(onescript.size)
                s3 = s3.rstrip()
                s = s1 + ';' + s2 + ';' + s3 + '\n'
                f.write(s)

        print('\n==> ** Processing complete, {} scripts found. **'.\
              format(self.length()),end='\n\n')

        return self.len

### ------- End of Class Scripts ---------- ###


def process_program_list(program_list, scripts):
    global args

    statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                          'st_nlink, st_uid, st_gid, st_size, st_atime,'
                          ' st_mtime, st_ctime')

    program_list.sort(key=str.lower)
    # program_list is now in alphabetical order.

    for program in program_list:
        try:
            program = program.rstrip()
            if args.verbose == 1:
                print('Working on {}'.format(program).ljust(60), end='\r')
            try:
                statinfo = os.stat(program)
            except FileNotFoundError:
                continue
            else:
                size = statinfo.st_size

            command = 'file ' + program
            p = os.popen(command)
            line = p.readline()
            line = line.rstrip()
            progtype = line
            p.close()
            if (('compiled' in progtype) or ('ELF' in progtype)):
                continue
            if (('ASCII' in progtype) or ('script' in progtype) or
                    ('text' in progtype)):
                script = Script(program, progtype, size)
                onescript = script.process_progtype()
                scripts.add(onescript)

        except FileNotFoundError:
            continue

    return scripts.scripts


def main():
    global args

    sfile = startup_housekeeping()  # sfile names the file that will
                                    # be written in the output directory.
    os.chdir(args.inputdir)

    program_list = []
    program_list = os.listdir(args.inputdir)
    numprograms = len(program_list)

    if args.verbose > 0:
        print('\n==> There are {} programs in {}.'.
              format(numprograms, args.inputdir), end='\n\n')
        sleep(2)
    if args.verbose > 0:
        print('\n==> Please be patient. '
              'Processing {} programs takes time.'.
              format(numprograms), end='\n\n')
        sleep(2)
    scripts = Scripts()  # Starts out empty

    script_list=process_program_list(program_list, scripts)
    # the function call populates "scripts" ONLY with
    # "scripts" - Python, Perl, Ruby, php, Bourne Shell, etc.
    # compiled ELF programs are discarded, there are different
    # ways of getting the source code for those.

    if args.verbose > 0:
        print('\n==> There are {} scripts in {}.'.
              format(scripts.length(), args.inputdir), end='\n\n')
        sleep(2)

    scripts.writefile(sfile)
    return scripts.length()


if __name__ == '__main__':
    # call to parse args ##### (or, probably, NOT some configfile)
    global args
    args = parse_args()
    here = os.getcwd()
    rc = main()
    os.chdir(here)
    sys.exit(rc)
