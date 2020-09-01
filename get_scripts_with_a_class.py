#!/usr/bin/env python 
r''' This really isn't a docstring.
What will this program do? get_scripts_with_a_class.py, much like the others, it will go through all
the files in a given "bin" directory and sort out which are scripts,  a la
Python, Perl, Ruby, Lua, or others. It will use a similar mechnism to do
this as in "get_scripts_in_usr_bin.py"

What will be markedly different from the other programs, is the use of 
a "Scripts" class to hold the scripts found in the chosen "bin" directory.

I have tried before but my Java days tried to entice me into making
a class out of everything, a very ill-advised and inelegant way of 
acheiving the desired result. We don't need a "Food Processor" class 
to take care of the inner guts of the program. 

"Scripts" may well be the only class in the whole program. That may 
neaten up the program somewhat, but once that gets under control, the
truly "next" program will include chosing the directory to be processed 
from the command line, as well as an option to procewss ALL of the bin dirsa, say in the user's path.'''


#  8/14/2020 - next up is to read the files in the directory,
#  Do the stat, from which we get the size (I can't think of
# any files I want to ferret out using os.stat - just to get
# the size, element number 3 in the fileinfo named tuple.
# wehile we're doing that, at the same time we need to be issuing
# os.popen, cobblib Scipts (which I think now think sould be just a fileinfo,
# SCRIPTS. See get_scripts_in_usr_bin.py for details.


import os
import sys
import stat
from collections import namedtuple
import time
import logging
import argparse

DEBUG = 1

global args


# For backward compatibility, a stat_result instance is also accessible
# as a tuple of at least 10 integers giving the most important (and
# portable) members of the stat structure, in the order st_mode
# st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
# st_mtime, st_ctime. More items may be added at the end by some
# implementations. For compatibility with older Python versions,
# (from 'stat' documentation).

statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                      'st_nlink, st_uid, st_gid, t_size, st_atime,'
                      ' st_mtime, st_ctime')
fileinfo = namedtuple('fileinfo', 'progname, filetype, size')



def parse_args():
    global args
    r'''The purpose of args here is to get the input directory/ies
    and the output directory where the results of this program will go.
    There is the matter of naming the output files, but that is better
    done elsewhere. Here, we will stick to the command line args.'''

    parser = argparse.ArgumentParser(description='Parse command line \
for the program.')
    parser.add_argument('-i', '--inputdir',  help='Input directory, a "bin" dir.', required=True)
    parser.add_argument('-o', '--outputdir', help='Directory to place results into.', required=True)
    parser.add_argument('-v', '--verbose', action='count', default=0, required=False)
#    parser.parse_args(['-vvv'])
#    Namespace(verbose=3)

    args = parser.parse_args()
    return args


def startup_housekeeping():
    pass


class Program:
    type = 'single script or compiled program'
 
    def __init__(self, progname, description, size):
        self.progname = progname
        self.description = description 
        self.size = size

    def process_description(self):
        r''' This where the work of pairing down the "description"
             until it is short, succinct, and easy to tell if the program 
             is a script or not.
            (see the named tuple "fileinfo"), same as in all previous
            versions of this proogram, back to "get_scripts_in_usr_bin.py"'''
        global args, files
        global statinfo, fileinfo

        command = 'file ' + self.progname
        p = os.popen(command)
        for line in p:
            line = line.rstrip()
            saveline = line
            n = line.index(':')
            x=len(line)
            two_words = []
            two_words.append(line[0:n])
            if DEBUG:
                print('**DEBUG: {}.'.format(two_words))
            n += 2
            line = line[n:x]
            save_description_line=line
            if (DEBUG > 1):
                print('**DEBUG: save description line is', save_description_line)
            try:
                rindex = line.index(',')
            except ValueError:
                rindex=0
            else:
                nindex = len(line)
                rindex += 1
                line = line[rindex:nindex]
                if (DEBUG > 1):
                    print('**DEBUG: line is', line)
                 #   time.sleep(2)
            finally:
                try:
                    rindex2 = line.index(',')
                    # it's really the second comma that we're looking for
                except ValueError:
                    if (('script' in line) or ('text' in line) or \
                        ('ASCII' in line)):
                        rindex2 = len(line)
                    else:
                        rindex2 = 0
                finally:
                    rindex += rindex2
            self.description = save_description_line[0:rindex]
            lendescription = len(self.description)
            if (('ASCII' in self.description) or ('script' in self.description) or \
                ('text' in self.description)):
                if (DEBUG):
                    print('**DEBUG: new description is', self.description)
                lendescription = len(self.description)
            if self.description.endswith(','):
                lendescription -= 1
                self.description = self.description[0:lendescription]
            if (DEBUG):
                print('**DEBUG: in Script.process_description,\n' \
                      'progname is {}, description is {} and size is {}.'.format(self.progname, self.description, self.size))
        p.close()
        self.finfo = fileinfo(self.progname, self.description, self.size)
        self.prog = self.finfo
        


        
## if this survives the assholes' periodic round of destruction,
## I intend to use only one Scripts class and have it incorporate
## the functionality of class Script. Unless dataclasses have a good
## alternative. Check and see.
##
## The next day (Aug. 31, 2020):
## On the other hand, I think the singular "Script' class is where
## the work should be done such as capturing and pairing down the
## 'description' field.
##
## The aggregate 'Scripts' class can be used to hold all the scripts
## captured so far, until all are captured. They can then be counted,
## displayed (as a whole or subset) and written to files, depending
## the needs of the program.


        
class Scripts:
    type = 'executable scripts'

    def __init__(self):
        self.scripts = []
        # here, we either have to create or read from args
        # what the output file names are going to be

    def add(self, script):
        self.scripts.append(script)
        
    def writescript(self):
        r''' we need the name of the output directory from the argparse routine then something like this'''
        pass

    
def input_loop():
    global files, args
    global statinfo, fileinfo
    files=[]
    if DEBUG>0:
        print('**DEBUG: output directory is {}'.format(args.outputdir))
    files=os.listdir(args.inputdir)
    numfiles=len(files)
    print('There are {} files in {}.'.format(numfiles,args.inputdir))
#    print('Please be patient. Processing {} files takes time.'. \
#          format(numfiles))
    files.sort(key=str.lower)
    if DEBUG > 1:
        print('**DEBUG: Got args?',end=' ')
        print (args.outputdir)
#        time.sleep(2)


    scripts=Scripts()
    for f in files:
        try:
            f = f.rstrip()
            statinfo = os.stat(f)
            size = statinfo.st_size
            if (DEBUG):
                print ('{} is {} bytes long.'.format(f,str(size)))
            prog=Program(f,' ',size)
            prog.process_description()
            if (('ASCII' in prog.description) or ('script' in prog.description) or \
                ('text' in prog.description)):
                scripts.add(prog)

        except FileNotFoundError:
            continue
    return    
                         

def main():
    r''' first get the args from the argoarse routine
       or, if specified, "ALL", meaning every directory in the user's path
    '''
    global args, files
    args = parse_args()
    print ('Just got back "args".')
    if args.inputdir:
        print ('we snagged a commandline argument. Inputdir = {}'.format(args.inputdir))
    if args.outputdir:
        print ('Got the output directory value: {}.'.format(args.outputdir))
    here = os.getcwd()
    os.chdir(args.inputdir)
    files = os.listdir(args.inputdir)
    rc = input_loop()
    return 0
    
if __name__=='__main__':
    # call to parse args and/or configfile
    rc = main()
    sys.exit(rc)

