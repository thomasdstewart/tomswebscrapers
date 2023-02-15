#!/bin/bash

echo  -en "Sky Garden dates: \n" > ~/check_skygarden.txt
curl -s "https://skygarden.bookingbug.com/api/v1/37002/events?start_date=$(date +%Y-%m-%d)&end_date=$(date -d "today + 1 year" "+%Y-%m-%d")&summary=true" -H 'App-Id: f6b16c23' -H 'App-Key: f0bc4f65f4fbfe7b4b3b7264b655f5eb' | jq .events[] | xargs | sed 's/ /\n/g' >> ~/check_skygarden.txt

n=$(diff -u ~/check_skygarden.txt.orig ~/check_skygarden.txt | wc -l)

if [ $n -gt 0 ]; then
        cat ~/check_skygarden.txt | mutt -s "Sky Garden Availability" thomas@stewarts.org.uk
        cp ~/check_skygarden.txt ~/check_skygarden.txt.orig
fi
