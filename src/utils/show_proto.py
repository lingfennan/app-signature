"""
Example run:
python show_proto.py -i ../../data/flexdroid/play_gpl_apps -p APKDatabase | less
"""

import sys, getopt
import proto.apk_analysis_pb2 as evalpb


def read_proto_from_file(proto, filename):
    f = open(filename, "rb")
    proto.ParseFromString(f.read())
    f.close()

def show_proto(inputfile, proto_type, fields=None, filter_func=None):
    proto = getattr(evalpb, proto_type)()
    read_proto_from_file(proto, inputfile)
    if filter_func:
        proto = filter_func(proto)
    print proto
    if fields:
        fields = fields.split(',')
        for f in fields:
            print len(getattr(proto, f))

def main(argv):
    help_msg = ("show_proto.py -i <proto_file> -p <proto_type> -c <count_fields>")
    try:
        opts, args = getopt.getopt(argv, "hi:p:c:")
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)
    count_fields = None
    for opt, arg in opts:
        if opt == "-h":
            print(help_msg)
            sys.exit()
        elif opt in ("-i"):
            infile = arg
        elif opt in ("-p"):
            proto_type = arg
        elif opt in ("-c"):
            count_fields = arg

    show_proto(infile, proto_type, count_fields)


if __name__ == "__main__":
    main(sys.argv[1:])
