#!/bin/sh
# fibonacci series
if [ -z "$VAR" ]
then
    /bin/echo -n "VAR is empty"
else
    N=$VAR
    M=$(($VAR-1))
    a=0 
    b=1  
    i=0
    while [ "$i" -lt "$N" ] 
    do
        /bin/echo -n "$a"
        if [ "$i" -ge "$M" ]
        then
            /bin/echo ""
        else
            /bin/echo -n " "
        fi
        fn=$(( a + b )) 
        a=$b
        b=$fn
        i=$(( i + 1 ))
    done
fi