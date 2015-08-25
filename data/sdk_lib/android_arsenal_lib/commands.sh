# These commands need to be run manually for now.

# download the page
wget https://android-arsenal.com/free
# get the app links
cat free | grep -o '<a href=[^>]*>[^<]*</a>' | grep \"/details > free_2
# download each app link
cat android_arsenal_list | while read line; do OUTFILE=$(echo $line | grep -oE "[^/]+$"); curl $line > android_arsenal_sdk_dst/$OUTFILE; done
# find GPL licenses
grep '[^L]GPL' *

# the two other pages
wget https://android-arsenal.com/demo
wget https://android-arsenal.com/paid

