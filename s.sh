#!/bin/sh
echo Beginning of process:
./get_scripts_in_bindirs.py
#
sort -t ";" -n -k 3 scripts-in-bindirs.txt > scripts-in-bindirs-sorted.txt

grep -iE "Perl|Python" scripts-in-bindirs-sorted.txt > perl-and-python-scripts-in-bindirs.txt
grep -iE "ruby|lua" scripts-in-bindirs-sorted.txt > ruby-and-lua-scripts-in-bindirs.txt
echo For your convenience, scripts based on Lua or Ruby are in their \
     own files, check the directory listing of this directory.
echo
echo End of processing.

