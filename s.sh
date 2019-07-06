pushd /home/baz/source/python/scripts-search?version-2 >& /dev/null
./get_scripts_in_usr_bin.py
#
sort -t ";" -n -k 3 scripts-in-usr-bin.txt > scripts-in-usr-bin-sorted.txt
#
grep -iE  "Perl|Python" scripts-in-usr-bin-sorted.txt > perl-and-python-scripts-in-usr-bin.txt
popd >& /dev/null

