!/usr/bin/env python
import regex
import argparse
import logging
import time
from collections import namedtuple
import stat
import sys
import os
r''' This really isn't a docstring.
What will this program do? get_scripts_with_a_class.py, 
much like the others, will go through all the files in 
a given "bin" directory and sort out which are scripts,
a la sh, POSIX, Python, Perl, Ruby, Lua, or others. 

It will use a similar mechnism to do
this as in "get_scripts_in_usr_bin.py"

What will be markedly different from the other programs, is the use of 
a Script and Scripts classes to hold the scripts found in the chosen "bin" directory.
'''


__author__ = 'Bryan A. Zimmer'
__date_of_this_notation__ = 'September 1, 2020 9:50 AM'


# Command-line invocation:
# get_scripts -i [executable directory, such as /usr/bin or /usr/local/sbin]
##               -o /your/home/directory/path/to/scratch/file
# -vvv
# -r [create a report showing statistics of scripts]
# -p [parse the list of scripts into categories:
# Perl Scripts, Python, sh scripots, Ruby, Lue, whatever...]
# -s [sort main list by some criterion other than size, (a)lphabetical, s(c)ripts, type
##
##


#  8/14/2020 - next up is to read the files in the directory,
#  Do the stat, from which we get the size (I can't think of
# any files I want to ferret out using os.stat - just to get
# the size, element number 3 in the named tuple "fileinfo".
# while we're doing that, at the same time we need to be issuing
# os.popen, Scripts (which I think now think sould be just a fileinfo,
# SCRIPTS. See get_scripts_in_usr_bin.py for previous details.


DEBUG = 0

global args


# For backward compatibility, a stat_result instance is also accessible
# as a tuple of at least 10 integers giving the most important (and
# portable) members of the stat structure, in the order st_mode
# st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
# st_mtime, st_ctime. More items may be added at the end by some
# implementations. For compatibility with older Python versions,
# (from 'stat' documentation).

statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                      'st_nlink, st_uid, st_gid, st_size, st_atime,'
                      ' st_mtime, st_ctime')
fileinfo = namedtuple('fileinfo', 'progname, filetype, size')


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
    r''' This class creates a "fileinfo" named-tuple for
         only scripts that are found in the directory listing returned by 
         os.listdir(inputdir)'''

    type = 'single executable script'

    def __init__(self, progname, filetype, size):
        self.progname = progname
        self.filetype = filetype
        self.size = size

    def process_filetype(self):
        r''' This where the work of pairing down the "filetype"
             until it is short, succinct, and easy to tell if the program 
             is a script or not.
            (see the named tuple "fileinfo"), same as in all previous
            versions of this proogram, back to "get_scripts_in_usr_bin.py"'''
        global args
        global fileinfo

        line = self.filetype.rstrip()
        saveline = line
        n = line.index(':')
        x = len(line)
        n += 2  # skip over the colon and following space.
        line = line[n:x]  # i.e., what the 'file' command returns, minus
                          # the program name - everything following the ': '
        save_filetype_line = line
        try:
            rindex = line.index(',')
        except ValueError:
            rindex = 0
        else:
            nindex = len(line)
#            rindex += 1
            line = line[rindex:nindex]
        finally:
            try:
                rindex2 = line.index(',')
                # it's really the second comma that we're looking for
            except ValueError:
                if (('script' in line) or ('text' in line) or
                    ('ASCII' in line)):
                    rindex2 = len(line)
                else:
                    rindex2 = 0
            finally:
                rindex += rindex2
        self.filetype = save_filetype_line[0:rindex]
        lenfiletype = len(self.filetype)
        if self.filetype.endswith(','):
            lenfiletype -= 1
        self.filetype = self.filetype[0:lenfiletype]
        if (DEBUG):
            bigstring=f'progname={self.progname}, \
                      filetype={self.filetype}, \
                      size={self.size}.'
            print(bigstring.ljust(45),end='\r')
        self.script = fileinfo(self.progname, self.filetype, self.size)



class Scripts:
    global args

    type = 'executable scripts'

    def __init__(self):
        self.scripts = []
        self.len = 0
        # here, we either have to create or read from args
        # what the output file names are going to be

    def add(self, script):
        self.scripts.append(script)

    def length(self):
        return len(self.scripts)
 
        
    def writefile(self):
        r''' we need the name of the output directory from the 
             argparse routine then something like this'''
        logdir = args.outputdir
        pattern = '/'
        replace = '-'
        sfilename = 'scripts-in'
        directory = args.inputdir
        directory = regex.sub(pattern, replace, directory)
        replace='_'
        logdir = regex.sub(pattern, replace, logdir)
        if DEBUG:
            print('\n==> input directory =', directory, end='\n\n')
            time.sleep(1)
        sfile = logdir + '_'+ 'scripts-in-' + directory + '.txt'

# this should be contingent on what the user wants
        sorted_scripts=[]
        sorted_scripts=sorted(self.scripts, key=lambda script: script.size)

        if DEBUG:
            print('---> ** sfile is', sfile, end='\n\n')
            time.sleep(1)
        with open(sfile, 'w') as f:
            for script in self.scripts:
                s1 = script.progname
                s1 = s1.rstrip()
                s2 = script.filetype
                s2 = s2.rstrip()
                s3 = str(script.size)
                s3 = s3.rstrip()
                s = s1 + ';' + s2 + ';' + s3 + '\n'
                f.write(s)
        if DEBUG:
            print('\n*** That does it for', sfile, end='\n\n')
        return len(self.scripts)


def main():
    global args
    global statinfo, fileinfo

    os.chdir(args.inputdir)

    files = []
    files = os.listdir(args.inputdir)
    numfiles = len(files)
    if DEBUG:
        print('\n==> There are {} files in {}.'.format(
            numfiles, args.inputdir), end='\n\n')
        time.sleep(1)
    print('Please be patient. Processing {} files takes time.'.
          format(numfiles))
    files.sort(key=str.lower)
    scripts = Scripts()
    for filename in files:
        try:
            filename = filename.rstrip()
            try:
                statinfo = os.stat(filename)
            except FileNotFoundError:
                continue
            else:
                size = statinfo.st_size
            command = 'file ' + filename
            p = os.popen(command)
            for line in p:
                line = line.rstrip()
                filetype = line
            p.close()    
            if (('ASCII' in filetype) or ('script' in filetype) or
                    ('text' in filetype )):
                script = Script(filename, filetype, size)
                script.process_filetype()
                scripts.add(script)
           
        except FileNotFoundError:
            continue
    if DEBUG:
        print('\n** There are {} scripts in {}.'.\
              format(scripts.length(), args.inputdir), end='\n\n')

    scripts.writefile()
    return scripts.length()


if __name__ == '__main__':
    # call to parse args (or, possibly, configfile)
    global args

    args= parse_args()
    here = os.getcwd()
    rc = main()
    os.chdir(here)
    sys.exit(rc)
