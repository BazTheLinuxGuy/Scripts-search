#!/usr/bin/env python3

import os
import sys
import stat
from collections import namedtuple
DEBUG = 0

# For backward compatibility, a stat_result instance is also accessible
# as a tuple of at least 10 integers giving the most important (and
# portable) members of the stat structure, in the order st_mode,
# st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime,
# st_mtime, st_ctime. More items may be added at the end by some
# implementations. For compatibility with older Python versions,
# accessing stat_result as a tuple always returns integers.
# (from 'stat' documentation).


def write_scripts_to_disk():
    ''' write scripts to disk (scripts from /usr/bin) '''

    global scripts
    
    logdir = '/home/baz/source/python/scripts-search/version-2'
    sfile = logdir + os.sep + 'scripts-in-usr-bin.txt'
    if (DEBUG > 1):
        print('sfile is', sfile)
    try:        
        with open(sfile, 'w') as f:
            for script in scripts:
                if (DEBUG > 1):
                    print(script)
                s1 = script.progname
                s1 = s1.rstrip()
                s2 = script.filetype
                s2 = s2.rstrip()
                s3 = str(script.size)
                s3 = s3.rstrip()
                s = s1 + ';' + s2 + ';' + s3 + '\n'
                f.write(s)
    except Exception:
        rv=0
        print('Unfortunately, you triggered an exception.')
    else:
        rv = len(scripts)
    finally:
        print('That does it for',sfile)
        return rv


def get_filetype(cmd=None):
    r'''This subroutine grabs informations out of each line of the command
    'file /usr/bin/<program>', so we can parse out the parts we need,
    which are the type of the file (either ELF-64-bit compiled program, or
    some kind of ASCII-based script, shell script, Perl program or 
    Python program), and the size of the program or script.'''

    global scripts

    p = os.popen(cmd)
    for line in p:
        line = line.rstrip()
        save_line = line
        n = line.index(':')
        x = len(line)
        words = []
        words.append(line[0:n])
        if (DEBUG > 1):
            print(words)
        n += 2
        line = line[n:x]
        save_filetype_line = line
        if (DEBUG > 1):
            print('save filetype line is', save_filetype_line)
        try:
            rindex = line.index(',')
        except ValueError:
            rindex = 0
        else:
            nindex = len(line)
            rindex += 1
            line = line[rindex:nindex]
            if (DEBUG > 1):
                print('line is', line)
        finally:
            try:
                rindex2 = line.index(',')       # it's really the second
            except ValueError:                  # comma we are looking for
                if (('scripts' in line) or ('text' in line)):
                    rindex2 = len(line)
                else:
                    rindex2 = 0
            finally:
                rindex += rindex2
        filetype = save_filetype_line[0:rindex]
        len_ft = len(filetype)
        if (('script' in filetype) or ('text' in filetype)):
            if (DEBUG):
                print('new filetype is', filetype)
        if filetype.endswith(','):
            len_ft -= 1
            filetype = filetype[0:len_ft]
        if (DEBUG > 1):
            print("in get_filetype, filetype is ",filetype)
    p.close()


# next file/line

    return filetype

# end of function


def main(program_name):
    r'''This is the main routine, which takes the aggregation of
        scripts and preps them for more processing down the road.'''

    global scripts
    scripts = []
    here = os.getcwd()
    statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                          'st_nlink,st_uid, st_gid, t_size, st_atime,'
                          ' st_mtime, st_ctime')
    fileinfo = namedtuple('fileinfo', 'progname, filetype, size')
    os.chdir('/usr/bin')
    files = os.listdir('/usr/bin')
    HowManyFiles = len(files)
    print('Please be patient. Processing {} files takes time.'. \
          format(HowManyFiles))
    files.sort(key=str.lower)
    scripts = []
    for thisfile in files:
        thisfile = thisfile.rstrip()
        print('working on', thisfile.ljust(45), end='\r')
        statinfo = os.stat(thisfile)
        mode = statinfo.st_mode
        if mode == stat.S_IFLNK:
            continue
#           breakpoint()
        else:
            size = statinfo.st_size
            cmd = 'file ' + thisfile
            filetype = get_filetype(cmd)
            finfo = fileinfo(thisfile, filetype, size)
            if (('script' in finfo.filetype) or
                ('text' in finfo.filetype)):
                scripts.append(finfo)
                if (DEBUG > 1):
                    print('\nCurrent length of scripts={}' \
                          .format(len(scripts)))
# next line
    if (DEBUG > 2):
        len_scripts = len(scripts)
        print('printing scripts from 117 on...')
        print(scripts[117:len_scripts])

    nfiles_in_scripts = write_scripts_to_disk()
    os.chdir(here)
    return ((nfiles_in_scripts, HowManyFiles))
# end of main()

if __name__ == '__main__':
    global scripts
    scripts=[]
    program_name = os.path.basename(sys.argv[0])
    print('Executing', program_name)

    nfiles_in_scripts, HowManyFiles = main(program_name)

    print ('\nThis program, "{}" reports {} scripts among the\n' \
           '{} programs in /usr/bin.'. \
            format(program_name,nfiles_in_scripts,HowManyFiles))
    sys.exit(nfiles_in_scripts)
                    
# end of program.

