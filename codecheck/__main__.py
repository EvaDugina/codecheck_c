import argparse

from codecheck import checkcode


def main():

    # parser = argparse.ArgumentParser(prog="codecheck",
    #     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser.add_argument("files", metavar="files", nargs="+",
    #                 help="paths to test files to check")
    # parser.add_argument("-c", "--conf", metavar="config.json",
    #                     help="path to JSON configuration file", required=True)
    # parser.add_argument("-f", "--format", metavar=".clang-format",
    #                     help="path to clang-format configuration")
    # args = parser.parse_args()
    #
    # if not args.conf:
    #     parser.error("path to configuration json file must be provided"
    #                  "specify it with -c or --conf flags")
    # if not args.files:
    #     parser.error("path to files to check must be provided"
    #                  "specify it with -t or --test flags")
    #
    # config = {
    #     "config_json": args.conf,
    #     "files_to_check": args.files,
    # }

    # Uncomment code below and comment code above to test without cl args
    config = {
        "config_json": '../examples/config_build.json',
        "files_to_check": ["../examples/code_example.c"],
    }

    checkcode.start(config["config_json"], config["files_to_check"])
    

if __name__ == "__main__":
    main()
