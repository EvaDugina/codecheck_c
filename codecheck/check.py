import xml.etree.cElementTree as ET  # working with xml
import json
from os import system
import os
from shutil import which

def write_result(tool, error_type, result):
    for check in data['tools'][tool]['checks']:
        if check['check'] == error_type:
            check['result'] = result
            return
    print("--- write_result failed")

def parse_configuration(configuration):
    f = open(configuration["json_path"])
    global data
    data = json.load(f)
    global files
    files = configuration['check_files']
    check_tools()
    run_tools()
    
def check_tools():
    deleted_tools = []
    for key, tool in data['tools'].items():
        if (which(tool['bin']) is None):
            print("Tool " + tool['bin'] + " not installed, skipping..")
            deleted_tools.append(key)
    for tool in deleted_tools:
        data['tools'].pop(tool)


def run_tools():
    print("Running tools..")
    test_cppcheck()
    test_valgrind()
    test_clang_format()
    with open('output.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def test_valgrind():
    if not data['tools']['valgrind']:
        return
    print('Running valgrind check...')
    enabled_types = []
    for c in data['tools']['valgrind']['checks']:
        enabled_types.append(c['check'])
    compile_command = data['tools']['valgrind']['compiler']
    compile_command += ' '
    for file in files:
        compile_command += file
        compile_command += ' '
    system(compile_command)
    system('valgrind --xml=yes --xml-file=valgrind.xml ./a.out')

    leaks_count = 0
    errors_count = 0
    for event, elem in ET.iterparse('valgrind.xml'):  # incremental parsing
        if elem.tag == 'kind':
            if elem.text.startswith('Leak_'):
                leaks_count += 1
            else:
                errors_count += 1
            elem.clear()

    write_result('valgrind', 'leaks', leaks_count)
    write_result('valgrind', 'errors', errors_count)
    os.remove('a.out')
    os.remove('valgrind.xml')
    print('Valgrind checked')

def test_cppcheck():
    if not data['tools']['cppcheck']:
        return
    print('Running cppcheck...')
    enabled_types = []
    for c in data['tools']['cppcheck']['checks']:
        if c['check'] != 'error':
            enabled_types.append(c['check'])
    command = 'cppcheck '
    for file in files:
        command += file
        command += ' '
    command += '--enable='
    command += ','.join(enabled_types)
    command += ' --xml --output-file=cppcheck.xml'
    system(command)

    errors_count = {}
    for event, elem in ET.iterparse('cppcheck.xml'):  # incremental parsing
        if elem.tag == 'error':
            severity = elem.get('severity')
            if errors_count.get(severity) is None:
                errors_count[severity] = 1
            else:
                errors_count[severity] += 1
            elem.clear()
    
    for c in data['tools']['cppcheck']['checks']:
        if c['check'] in errors_count:
            c['result'] = errors_count[c['check']]
        else:
            c['result'] = 0

    os.remove('cppcheck.xml')
    print("Cppcheck checked")

def test_clang_format():
    if not data['tools']['clang-format']:
        return
    # clang-format до версии 14 не поддерживает указание конкретного файла формата,
    # поэтому нужно размещать файл с форматом с названием .clang-format на одном уровне с исходниками
    print("Running clang-format...")
    command = 'clang-format '
    for file in files:
        command += file
        command += ' '
    command += '--style=file --output-replacements-xml > format.xml'
    system(command)

    replacements = 0
    for event, elem in ET.iterparse('format.xml'):
        if elem.tag == 'replacement':
            replacements += 1
            elem.clear()
    
    data['tools']['clang-format']['check']['result'] = replacements
    os.remove('format.xml')
    print('Clang-format checked')

    
