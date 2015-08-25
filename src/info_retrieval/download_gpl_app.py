import subprocess
import re

# Download GPL app from android arsenal.
def wget_and_store(url, outfile):
    p1 = subprocess.Popen(['wget', '-O', outfile, url], stdout=subprocess.PIPE)
    output, error = p1.communicate()
    return error

def download_from_android_arsenal(inlist, outdir):
    for link in inlist:
        print link
        p1 = subprocess.Popen(["curl", link], stdout=subprocess.PIPE)
        output, error = p1.communicate()
        # Get the group https.*zip
        pattern = r'(?:<a class="actionLink" title="Download sources" href=")(https.*zip)">'
        p = re.compile(pattern)
        m = p.search(output)
        if m:
            url = m.groups()[0]
            outfile = outdir + '-'.join(link.split('/')[-2:]) + '-master.zip'
            print url
            wget_and_store(url, outfile)

# Download GPL app from F-droid.

# Download Google Play app.

IN_FILE = '../../data/sdk_lib/android_arsenal_lib/gpl_list'
OUT_DIR = '../../data/sdk_lib/android_arsenal_lib/projects/'
inlist = filter(bool, open(IN_FILE, 'r').read().split('\n'))
download_from_android_arsenal(inlist, OUT_DIR)