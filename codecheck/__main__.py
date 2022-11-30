import argparse
import check

def main():
    parser = argparse.ArgumentParser(prog="codecheck",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-e", "--example", action="store_true",
                        help="example run without command line arguments")
    parser.add_argument("-c", "--conf", metavar="config.json",
                        help="path to JSON configuration file")
    parser.add_argument("-t", "--test", metavar="main.c", nargs="+",
                        help="paths to test files to check")
    parser.add_argument("-f", "--format", metavar=".clang-format",
                        help="path to clang-format configuration")
    args = parser.parse_args()

    if args.example:
        print("Running example case:")
        config = {
            "json_path" : '../examples/config.json',
            "check_files" : ["../examples/code_example.c"],
            "clang_format" : '../guidelines/strict.clang-format'
        }
        check.parse_configuration(config)
        return

    if not args.conf:
        parser.error("path to configuration json file must be provided"
                     "specify it with -c or --conf flags")    
    if not args.test:
        parser.error("path to test files to check must be provided"
                     "specify it with -t or --test flags")

    config = {
        'json_path' : args.conf,
        'check_files' : args.test,
        'clang_format' : args.format
    }
    check.parse_configuration(config)
    

if __name__ == "__main__":
    main()