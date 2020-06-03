# SED
SED implementation with Python 3

#1.Supports n, i, e parameters
#2 Supports nth replacement, p, g, w flags
#3 Checks for correct quotes on command
#4 Supports echo, bash, file input format
#5 Supports chained commands

Tested Commands:

sed "s/ks/kg/g" b.txt # File not found 
sed -e 's/kali/roni/2' example.txt #2
sed 's/kali/roni/2' example.txt # 3
sed -e 's/\bben\b/jordan/g' example.txt #4 example replacing only the exact match for "ben" with "jordan"
sed -e 's/\bben\b/jordan/p' example.txt #5 replacing first occurences of ben, prints match again
sed -e 's/ben/jordan/p' example.txt #6 replacing first matches in a row for ben including not exact
sed -e 's/ben/jordan/g' example.txt #7 replacing all occurrences of ben with jordan, not exact
sed -e 's/ben/jordan/pg' example.txt # 8 replacing all occurrences of ben with jordan,not exact, print matche again
sed -e 's/\bb e n\b/jordan/g' example.txt #9 doesn't replace anything
sed -e 's/\bb e n\b/jordan/g" example.txt #10 bad quotes error
sed sed "s/kings/kings/g" example.txt #11 incorrect format
sed -e 's/\bben\b/jordan/' example.txt # 12 replace first ben in row, no parameter
echo "A,B,C" | sed "s/,/','/g" #13
echo "A,B,C" | sed "s/,/','/" #14
echo "A,B,C" | sed "s/,/','/pg" #15
echo "A,B,C" | sed -e "s/,/','/pg" #16
sed "s/,/','/g" <<< "A,B,C" #17
sed -i "s/,/','/g" <<< "A,B,C" #18 No input file
sed "s/,/','/p" <<< "A,B,C" # 19
sed -e 's/ben/jordan/2' example2.txt #20
sed -e 's/\sben\s/jordan/g' example2.txt #21
sed -n 's/\bben\b/jordan/g' example.txt#22
echo "unix" | sed -n 's/unix/linux/p' #23 prints linux
echo "unix" | sed -n 's/unix/linux/' #24 prints nothing
echo "unix" | sed -n 's/unix/linux/w' #25 File not found - can't open file
sed -e 's/a/A/' -e 's/b/B/' example.txt #26 chain commands
echo "unixab" | sed -e 's/a/A/' -e 's/b/B/' #27 unixAb
sed -e 's/a/A/' -e 's/b/B/' example.txt #28 chain commands with file
sed -e 's/a/A/' -e 's/b/B/gp' example.txt # 29
sed -e 's/ben/jordan/g' -e 's/jordan/n/gp' example.txt # 30
sed -e 's/a/A\\/' -e 's/b/B/' example.txt # 31
sed -e 's/a/A\\/' -e 's/b/B/' -e 's/r/G/' example.txt #32 3 chained commands
sed -e 's/a/A\\/\\/' -e 's/b/B/' example.txt #33 Incorrect foramt error
sed -n 's/ben/jordan/pg' example.txt #34 tests n parameter with p, prints changes
sed -n 's/ben/jordan/g' example.txt #35 doesn't print without p flag
sed -i 's/ben/j/' example2.txt #36 writes changes to file
