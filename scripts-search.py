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
    get_scripts -i / --inputdir: [executable directory,
                                   such as /usr/bin or /usr/local/sbin]

                -o / --outputdir: [/path/to/directory - for writing output]
                                  NOTE: Must be fully qualified
                -v / --verbose: [increase program verbosity, up to 3 -v's
                                 can be used.]
                -r / --generate-report: [create a report showing \
                                         statistics of scripts]
                -p [parse the list of scripts into categories:
                   Perl Scripts, Python, sh scripts, Ruby, Lua,
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
__updated__ = 'November 9, 2020 11:05 AM (Monday)'
__program_name__ = 'scripts-search.py'

global fileinfo

DEBUG=0

# For backward compatibility, a stat_result instance is also accessible
# as a tuple of at least 10 integers giving the most important (and
# portable) members of the stat structure, in the order st_mode
# st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
# st_mtime, st_ctime. More items may be added at the end by some
# implementations. For compatibility with older Python versions,
# (from 'stat' documentation).


fileinfo = namedtuple('fileinfo', 'progname, progtype, size')


def parse_args():
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
    parser.add_argument('-r', '--report',
                        action='store_true', required=False, default=False,
                        help='Statistics on the output we produce.')
    parser.add_argument('-s', '--sortby', action='store',
                        default='size', required=False, type=str,
                        choices=['name', 'type', 'size'],
                        help='sort output file by size, name, or type')
#    parser.parse_args(['-vvv'])
#    Namespace(verbose=3)

    args = parser.parse_args()
    return args


def startup_housekeeping():
    r'''move this to startup housekeeping()
            we need the name of the output directory from the
            argparse routine then something like this'''

    if args.outputdir.endswith(os.sep):
        args.outputdir = args.outputdir[0:-1]
    replace = '-'
    sfilename = 'scripts-in'
    inputdir = regex.sub(os.sep, '-', args.inputdir)
    sfile = sfilename + inputdir + '.csv'

    if args.verbose > 0:
        print('The output file(s) will be written to:')
        print(args.outputdir + os.sep + sfile, end='\n\n')
#        sleep(2)
    return sfile


class Script:
    r''' This class creates a 3-tuple for `scripts'
         that are found in the directory listing returned by
         os.listdir(inputdir)'''

    pg_type = 'single executable script'

    def __init__(self, progname, progtype, size):
#        self.scripts = []
        self.progname = progname
        self.progtype = progtype
        self.size = size
        self.finfo = fileinfo(self.progname,
                              self.progtype, self.size)

    def process_progtype(self):
        r''' This is the method that refines disparate data
             into a refined "script" a named 4-tuple.'''

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
            self.finfo.progtype = self.finfo.progtype[0:-1]
        self.finfo = fileinfo(self.progname, self.progtype, self.size)
        return self.finfo

### -------- End of class Script -------- ###


def straighten_up(datum):

    anathema = ','
    replacement = ' -'
    datum = regex.sub(anathema, replacement, datum)
    return datum


class Scripts:

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
        self.sfile = sfile
#       `sort' or `sorted'?
        self.newlist = self.scripts  # sorted alphabetically
#       the user gets to choose what field to sort on.
        if args.sortby == 'type':
            self.newlist = sorted(self.scripts, key=lambda finfo:
                                  finfo.progtype)
        elif args.sortby == 'size':
            self.newlist = sorted(self.scripts, key=lambda finfo:
                                  finfo.size)
        else:  # it has to be 'alpha', which it already is sorted to.
            pass

        os.chdir(args.outputdir)
        with open(self.sfile, 'w') as f:
            s1 = 'Program Name'
            s2 = 'Program Type'
            s3 = 'Size in Bytes'
            s = s1 + ',' + s2 + ',' + s3 + '\n'
            f.write(s)
            for onescript in self.newlist:
                s1 = onescript.progname
                s1 = s1.rstrip()
                s1 = straighten_up(s1)
                s2 = onescript.progtype
                s2 = s2.rstrip()
                s2 = straighten_up(s2)  # change commas to hyphens
                s3 = str(onescript.size)
                s3 = s3.rstrip()
                s3 = straighten_up(s3)
                s = s1 + ',' + s2 + ',' + s3 + '\n'
                f.write(s)

        print('\n==> ** Processing complete, {} scripts found. **'.
              format(self.length()), end='\n\n')

        return self.len

### ------- End of Class Scripts ---------- ###


def process_programs(programs, scripts):

    statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                          'st_nlink, st_uid, st_gid, st_size, st_atime,'
                          ' st_mtime, st_ctime')

    programs.sort(key=str.lower)
    # programs is now in alphabetical order.

    for program in programs:
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
                if (DEBUG):
                    print(f'size of {program} is {size}')
            command = 'file ' + program
            p = os.popen(command)
            line = p.readline()
            line = line.rstrip()
            progtype = line
            p.close()

#            command = 'whatis ' + program  # + ' > /dev/null'
#            p = os.popen(command)
#            line = p.readline()
#            line = line.rstrip()
#            whatis = line
#            p.close()
#
#            try:
#                x = whatis.index('- ')
#            except ValueError:
#                pass
#            else:
#                x += 2
#                whatis = whatis[x:]

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

def report_module(scripts): #taken from the main "Scripts" class.
    categories = {}
    i=0
    type0 = ''    
    scrp=scripts[0]
    scripts = sorted(scripts, key=lambda finfo:
                     finfo.progtype)

#    scripts are now sorted by type.
#    script = finfo = (progname, progtype, size)
#    type0 = scripts.scripts["x"].progtype
#    categories[type0] = (count)

# OK, here we are going to take a chance and pare down the "progtype"
# to only what
# precedes the first comma. This is supposed to make things
# easier to categorize.


    newscripts = []
    for i,scrp in enumerate(scripts):
        print('{}'.format(scrp.progname), end=' ')
        type1 = scrp.progtype
        try:
            n = type1.index(',')
        except ValueError:
            n = len(type1)
        new_progtype = type1[0:n]
        if 'symbolic' in new_progtype:
            continue
        print(f'new_progtype: {new_progtype}', end=' ')
        print('Size:', scrp.size)
#        scr.progtype = new_progtype # this failed, 'can't set attribute', so:
        progname = scrp.progname
        progtype = new_progtype
        size = scrp.size
        finfo = fileinfo(progname, progtype, size)
        newscripts.append(finfo)
#        print('\n' + '-' * 76)
        
#    sleep(5)    
    symlinks=[]

# I wanted to use a dictionary, but the nature of this thing
# is that an item has THREE, not two, items!
      
#    newscripts.sort(key=lambda finfo: finfo.size)
    

    for scrp in newscripts:
        if scrp.progtype != type0:
            type0 = scrp.progtype
            if not 'symbolic' in type0:
                categories[type0] = 1
            else:
                symlinks.append(scrp)
        else:
            categories[type0] += 1


    for k,v in categories.items():
        print('{}'.format(k))
        if 'symbolic link' in k:
            continue
        else:
            print(f'{k}:'.ljust(50),'Number:',str(v).ljust(20))

# OK, here's the report
    os.system('clear')

    print('Program type'.ljust(50), 'Number of programs'.ljust(15))
    lines1 = '_' * 30
    lines2 = '_' * 15
    print(lines1.ljust(55), lines2.ljust(15))
    for k,v in categories.items():
        print(k.ljust(55), str(v).ljust(15))
    print('\n\n\n\n\n')    
    sleep(10)

            
    return
    
def main():

    sfile = startup_housekeeping()  # sfile names the file that will
    # be written in the output directory.
    os.chdir(args.inputdir)

    programs = []
    programs = os.listdir(args.inputdir)
    numprograms = len(programs)

    if args.verbose > 0:
        print('\n==> There are {} programs in {}.'.
              format(numprograms, args.inputdir))
#        sleep(2)
#    if args.verbose > 0:
        print('==> Please be patient. '
              'Processing {} programs takes time.'.
              format(numprograms))
#        sleep(2)
    scripts = Scripts()  # Starts out empty

    script_list = process_programs(programs, scripts)

    # the function call populates "scripts" ONLY with
    # "scripts" - Python, Perl, Ruby, php, Bourne Shell, etc.
    # compiled ELF programs are discarded, there are different
    # ways of getting the source code for those.

    if args.verbose > 0:
        print('\n==> There are {} scripts in {}.'.
              format(scripts.length(), args.inputdir), end='\n\n')
#        sleep(2)

    scripts.writefile(sfile)
    if args.report:
        report_module(scripts.scripts)
    return scripts.length()


if __name__ == '__main__':
    args = parse_args()
    here = os.getcwd()
    rc = main()
    cmd = 'pushd ' + here + '>& /dev/null'
    os.system(cmd)

    sys.exit(rc)

