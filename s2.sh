
#!/bin/sh
echo Beginning of process:
./get_scripts_in_usr_bin.py
#
sort -t ";" -n -k 3 scripts-in-usr-bin.txt > scripts-in-bindirs-sorted.txt

grep -iE "Perl|Python" scripts-in-usr-bin-sorted.txt > perl-and-python-scripts-in-usr-bin.txt
grep -iE "ruby|lua" scripts-in-bindirs-sorted.txt > ruby-and-lua-scripts-in-bindirs.txt
echo
echo For your convenience, scripts based on Perl and Python or Lua and\
	 Ruby are in their own files, check the directory listing of\
	 this directory.
echo
echo End of processing.
