#!/usr/bin/env python
r'''scripts-search.py, much like its predecessors, 
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
                -s [sort scripts array by program name, program type,\
                    or program size.]

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
__updated__ = 'September 17, 2020 6:00 AM (Thursday)'
__program_name__ = 'get_scripts.py'
## My latest idea is to output the reports as CSV...that way
## they could be incorporated into Excel or other programs.

HYPHEN = '-'

#global args
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
 #   global args

    if args.outputdir.endswith(os.sep):
        args.outputdir = args.outputdir[0:-1]
    replace = HYPHEN
    sfilename = 'scripts-in'
    inputdir = regex.sub(os.sep, HYPHEN, args.inputdir)
    sfile = sfilename + inputdir + '.csv'
    
    if args.verbose > 0:
        print('sfile =', sfile)
        sleep(2)
    return sfile


def parse_args():
#    global args
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
    parser.add_argument('-s','--sortby', action = 'store',
                        default='size',required=False, type=str,
                        choices=['alpha','type','size'],
                        help='sort output file by size, name, or type')
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
        self.finfo = fileinfo(self.progname, self.progtype, self.size)

    def process_progtype(self):
        r''' This is the method that refines disparate data
             into a refined "script" a 3-tuple.'''

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

def straighten_up(datum):

    # NOTE: I'm pretty sure that none of the
    # fields contains more than one comma.
    # If I'm wrong I'm going to have to resort
    # to regex.

    anathema = ','
    replacement = ' -'
    datum = regex.sub(anathema, replacement, datum)
    return datum


    
#    try:
#        x = datum.index(',')
#    except ValueError:
#        return datum
#    else:
#        datum1 = datum[0:x]
#        datum2 = datum[x+1:]
#        datum = datum1 + ' -' + datum2
#        return datum
    

class Scripts:
#    global args

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
        # named tuples,
        
        self.sfile = sfile
# `sort' or `sorted'?
        self.newlist = self.scripts # sorted alphabetically
# the user gets to choose what field to sort on.
        if args.sortby == 'type':
            self.newlist = sorted(self.scripts, key=lambda finfo:\
                                  finfo.progtype)
        elif args.sortby == 'size':
            self.newlist = sorted(self.scripts, key=lambda finfo:\
                                  finfo.size)
        else: # it has to be 'alpha', which it already is sorted to.
            pass
            
# or:    self.scripts.sort(key=lambda script: key=script.progtype)
# the third option, alphabetical (ascending)
# is there by default
        this = os.getcwd()
#        print(f'We are now at {this}')
#        sleep(2)
#        print('We are writing files at {}.'.format(args.outputdir))
        os.chdir(args.outputdir)
        with open(self.sfile, 'w') as f:
            s1='Prog Name'
            s2='Prog Type'
            s3='Size'
            s=s1 + ', ' + s2 + ', ' + s3 + '\n'
            f.write(s)
            for onescript in self.newlist:
                s1 = onescript.progname
                s1 = s1.rstrip()
#                s1 = straighten_up(s1)
                s2 = onescript.progtype
                s2 = s2.rstrip()
                s2 = straighten_up(s2) # change commas to hyphens
                s3 = str(onescript.size)
                s3 = s3.rstrip()
#                s3 = straighten_up(self.s3)
                s = s1 + ',' + s2 + ',' + s3 + '\n'
                f.write(s)

        print('\n==> ** Processing complete, {} scripts found. **'.\
              format(self.length()),end='\n\n')

        return self.len

### ------- End of Class Scripts ---------- ###


def process_program_list(program_list, scripts):
#    global args

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
#    global args

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
        print('==> Please be patient. '
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
#    global args
    args = parse_args()
    here = os.getcwd()
    rc = main()
    os.chdir(here)
    sys.exit(rc)
