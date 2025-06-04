import argparse

from codecheck_core import start
from .tools_config import TOOLS_CHECKERS


def main():

    parser = argparse.ArgumentParser(prog="codecheck",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("files", metavar="files", nargs="+",
                    help="paths to test files to check")
    parser.add_argument("-c", "--conf", metavar="config.json",
                        help="path to JSON configuration file", required=True)
    parser.add_argument("-f", "--format", metavar=".clang-format",
                        help="path to clang-format configuration")
    args = parser.parse_args()

    if not args.conf:
        parser.error("path to configuration json file must be provided"
                     "specify it with -c or --conf flags")
    if not args.files:
        parser.error("path to files to check must be provided"
                     "specify it with -t or --test flags")

    config = {
        "config_json": args.conf,
        "files_to_check": args.files,
    }

    # Debugging in IDE
    # config = {
    #     "config_json": '../examples/config_all_debug.json',
    #     "files_to_check": ["../examples/code_example.c"],
    # }

    # Console Testing
    # config = {
    #     "config_json": 'examples/config_all_console.json',
    #     "files_to_check": [
    #         "examples/code_example_1.c", #"examples/code_example_2.c",
    #         #"examples/code_example_3.c", "examples/code_example_4.c"
    #     ],
    # }

    start(TOOLS_CHECKERS, config["config_json"], config["files_to_check"])
    

if __name__ == "__main__":
    main()
