wget https://android-arsenal.com/free
cat free | grep -o '<a href=[^>]*>[^<]*</a>' | grep \"/details > free_2
cat android_arsenal_list | while read line; do OUTFILE=$(echo $line | grep -oE "[^/]+$"); curl $line > android_arsenal_sdk_dst/$OUTFILE; done

