import xml.etree.cElementTree as ET  # working with xml
import json
from os import system
import os
import subprocess
from shutil import which, copy, rmtree

test_executable_name = 'test'

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
    # deleted_tools = []
    for key, tool in data['tools'].items():
        if not 'bin' in tool:
            continue
        if (which(tool['bin']) is None):
            print("Tool " + tool['bin'] + " not installed, skipping..")
            # deleted_tools.append(key)
            tool['enabled'] == False
            tool['outcome'] = 'skip'
        if (tool['enabled'] == False):
            tool['outcome'] = 'skip'
    # for tool in deleted_tools:
    #     data['tools'].pop(tool)


def run_tools():
    print("Running tools..")
    if test_build():
        test_cppcheck()
        test_clang_format()
        test_autotests()
        test_valgrind()
        test_copydetect()
    else:
        print('Code not builded, check failed')
    
    with open('output.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def test_build():
    print("Running build check...")

    compile_command = ''
    flags = []
    if data['tools']['build']['language'] == 'C++':
        compile_command = 'g++'
        flags.append('-c')
    elif data['tools']['build']['language'] == 'C++':
        compile_command = 'gcc'
        flags.append('-c')
    else:
        print('Language {} not supported, check failed'.format(data['tools']['build']['language']))
        exit()

    global compiled_files
    compiled_files = []
    for file in files:
        compiled_files.append(file.split('.')[0] + '.o')

    result = subprocess.run([compile_command] + flags + files, capture_output=True)

    output = open("output_build.txt", "w")
    data['tools']['build']['check']['full_output'] = 'output_build.txt'
    output.write(str(result.stderr))
    output.close()

    data['tools']['build']['outcome'] = 'pass'
    if result.returncode == 0:
        data['tools']['build']['check']['outcome'] = 'pass'
        print("Build checked")
        return True
    else:
        data['tools']['build']['check']['outcome'] = 'fail'
        print("Build checked")
        return False

def test_valgrind():
    if not 'valgrind' in data['tools'] or data['tools']['valgrind']['enabled'] == False:
        return
    print('Running valgrind check...')
    enabled_types = []
    for c in data['tools']['valgrind']['checks']:
        enabled_types.append(c['check'])

    # if not builded early on autotest stage
    if not data['tools']['autotests']:
        compile_command = data['tools']['valgrind']['compiler']
        compile_command += ' '
        for file in files:
            compile_command += file
            compile_command += ' '
        compile_command += '-o '
        compile_command += test_executable_name
        system(compile_command)

    system('valgrind --xml=yes --xml-file=valgrind.xml ./{} > /dev/null'.format(test_executable_name))    
    system('valgrind ./{} > /dev/null 2> output_valgrind.txt'.format(test_executable_name))    

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

    for val in data['tools']['valgrind']['checks']:
        if val['check'] == 'errors':
            val['outcome'] = 'pass' if val['limit'] >= errors_count else 'fail'
        if val['check'] == 'leaks':
            val['outcome'] = 'pass' if val['limit'] >= leaks_count else 'fail'

    data['tools']['valgrind']['full_output'] = 'output_valgrind.xml'
    data['tools']['valgrind']['outcome'] = 'pass'
    os.remove(test_executable_name)
    os.remove('valgrind.xml')
    print('Valgrind checked')

def test_cppcheck():
    if not 'cppcheck' in data['tools'] or data['tools']['cppcheck']['enabled'] == False:
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
    command += ' --xml --output-file=output_cppcheck.xml'
    system(command)

    errors_count = {}
    for event, elem in ET.iterparse('output_cppcheck.xml'):  # incremental parsing
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
        c['outcome'] = 'pass' if c['limit'] >= c['result'] else 'fail'

    data['tools']['cppcheck']['full_output'] = 'output_cppcheck.xml'
    data['tools']['cppcheck']['outcome'] = 'pass'
    print("Cppcheck checked")

def test_clang_format():
    if not 'clang-format' in data['tools'] or data['tools']['clang-format']['enabled'] == False:
        return
    # clang-format до версии 14 не поддерживает указание конкретного файла формата,
    # поэтому нужно размещать файл с форматом с названием .clang-format на одном уровне с исходниками
    print("Running clang-format...")
    copy('/stable/.clang-format', '.')
    command = 'clang-format '
    for file in files:
        command += file
        command += ' '
    command += '--style=file --output-replacements-xml > output_format.xml'
    system(command)

    replacements = 0
    for event, elem in ET.iterparse('output_format.xml'):
        if elem.tag == 'replacement':
            replacements += 1
            elem.clear()
    
    data['tools']['clang-format']['check']['result'] = replacements
    data['tools']['clang-format']['check']['outcome'] = 'pass' if data['tools']['clang-format']['check']['limit'] >= replacements else 'fail'
    data['tools']['clang-format']['full_output'] = 'output_format.xml'
    data['tools']['clang-format']['outcome'] = 'pass'
    print('Clang-format checked')

def test_autotests():
    if not 'autotests' in data['tools'] or data['tools']['autotests']['enabled'] == False:
        return

    print("Running autotests...")

    # command = ''
    # if data['tools']['autotests']['language'] == 'C':
    #     command = 'gcc -c '
    # else if data['tools']['autotests']['language'] == 'C++':
    #     coomand = 'g++ -c '

    compile_test = 'g++ ' + data['tools']['autotests']['test_path'] + ' '
    for file in files:
        compile_test += file.split('.')[0] + '.o'
        compile_test += ' '
    compile_test += ' -o '
    compile_test += test_executable_name

    compile_test += ' -I /stable'

    run_test = './test --reporter junit -o tests_result.xml'
    system(compile_test)
    system(run_test)
    system("./test > output_tests.txt")

    errors = 0
    failures = 0
    for event, elem in ET.iterparse('tests_result.xml'):
        if elem.tag == 'testsuite':
            errors += int(elem.get('errors'))
            failures += int(elem.get('failures'))
            elem.clear()

    for file in files:
        os.remove(file.split('.')[0] + '.o')

    os.remove('tests_result.xml')

    if not data['tools']['valgrind']:
        os.remove(test_executable_name)

    if errors > 0 or failures > data['tools']['autotests']['check']['limit']:
        data['tools']['autotests']['check']['outcome'] = 'fail'
    else:
        data['tools']['autotests']['check']['outcome'] = 'pass'

    data['tools']['autotests']['check']['errors'] = errors
    data['tools']['autotests']['check']['failures'] = failures
    data['tools']['autotests']['full_output'] = "output_tests.txt"
    data['tools']['autotests']['outcome'] = "pass"
    print('Autotests checked')

def test_copydetect():
    if not 'copydetect' in data['tools'] or data['tools']['copydetect']['enabled'] == False:
        return

    print("Running copydetect...")
    if os.path.exists('test_directory'):
        rmtree('test_directory')

    os.mkdir('test_directory')
    for file in files:
        copy(file, 'test_directory')

    command = 'copydetect -t test_directory -r {} -a -d 0 --out-file \'output_copydetect\''.format(data['tools']['copydetect']['check']['reference_directory'])
    system(command)
    rmtree('test_directory')
    data['tools']['copydetect']['full_output'] = "output_copydetect.html"
    data['tools']['copydetect']['outcome'] = 'pass'

    print('Copydetect checked')