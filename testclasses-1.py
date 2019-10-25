#!/usr/bin/env python3
''' This program-let explopreres classes as they might ne use in
    the program. "get-scripts-in-bin-dirs.py'''

import sys, os
import stat
import argparse
from collections import namedtuple
from collections import deque

statinfo = namedtuple('statinfo', 'st_mode, st_ino, st_dev, '
                      'st_nlink,st_uid, st_gid, t_size, st_atime,'
                      ' st_mtime, st_ctime')

fileinput=named_tuple('fileinfo','progname, filetype, size')




def create_classes():

    class Script:

        def __init__(program, info, size):
            self.program = program
            self.info = info
            self.size = size
            Script = (self.program,self.info = info, self.size=size)
        

def main():
    create_classes()



    return rc


if __name__=='__main__':
    int rc
    rc=main()
    sys.exit(rc)
