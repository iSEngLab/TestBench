import javalang
import re
import logging
import os
import json
from tqdm import tqdm

# logging.basicConfig(filename='log/java_project_repair.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
source_path = '/home/joseph/TestCaseGeneration/source_file_parser'


def add_package(generate_content, package_name):
    """
    Repair test case error(compile error).
    error: package org.junit.jupiter.api does not exist
    """
    repair_code = "package " + package_name + ";\n\n"
    repair_code += generate_content

    return  repair_code

def add_import(generate_content, import_info):
    """
    Repair test case error(compile error).
    error: syntax error
    """
    package_match = re.search(r'^package\s+[\w\.]+;', generate_content, re.MULTILINE)

    if package_match:
        # If package declaration is present, add imports after it
        package_end = package_match.end()
        return generate_content[:package_end] + '\n\n' + import_info + '\n' + generate_content[package_end:]
    else:
        # If no package declaration, add imports at the beginning
        return import_info + '\n' + generate_content

def add_class_framework(generate_content, package_name, class_name):
    """
    Repair test case error(syntax error).
    """
    repair_code = "package " + package_name + ";\n\n"
    repair_code += "import org.junit.jupiter.api.*;\n"
    repair_code += "import static org.junit.jupiter.api.Assertions.*;\n\n"
    repair_code += "public class " + class_name + "Test {\n"

    indented_generate_content = generate_content.replace("\n", "\n    ")

    repair_code += "    " + indented_generate_content + "\n"
    repair_code += "}"

    return  repair_code

def add_Test_annotation_and_class_framework(generate_content, package_name, class_name):
    """
    Repair test case error(syntax error).
    """
    repair_code = "@Test\n"
    repair_code += generate_content + "\n"
    repair_code = add_class_framework(repair_code, package_name, class_name)

    return  repair_code

def add_method_framework_and_class_framework(generate_content, package_name, class_name, method_name):
    """
    Repair test case error(syntax error).
    """
    repair_code = "@Test\n"
    repair_code += "public void " + method_name + "Test() {\n"

    indented_generate_content = generate_content.replace("\n", "\n    ")

    repair_code += "    " + indented_generate_content + "\n"
    repair_code += "}\n"
    repair_code = add_class_framework(repair_code, package_name, class_name)

    return  repair_code

def judge_error(generate_content):
    """
    Judge error(syntax error) in test case.
    """
    try:
        tree = javalang.parse.parse(generate_content)
    except:
        return True
    return False

def import_info_return(project_name, method_name):
    dir = source_path + '/' + project_name + '_out.json'
    with open(dir, 'r') as f:
        data = json.load(f)
    for item in data:
        if item['method_name'] == method_name:
            full = item['full_context']
            break
    import_pattern = r'^\s*import\s+[\w\.]+;'
    import_info = re.findall(import_pattern, full, re.MULTILINE)
    return import_info


def repair_error(generate_content, package_name, class_name, method_name, project_name):
    """
    Detect and repair error in test case.
    """
    repair_code = generate_content
    if judge_error(repair_code):
        match_class = re.search(r'public class', generate_content)
        if not match_class:
            match_annotation = re.search(r'@Test', generate_content)
            if match_annotation:
                repair_code = add_class_framework(generate_content, package_name, class_name)
            else:
                match_method = re.search(r'public void', generate_content)
                if match_method:
                    repair_code = add_Test_annotation_and_class_framework(generate_content, package_name, class_name)
                else:
                    repair_code = add_method_framework_and_class_framework(generate_content, package_name, class_name, method_name)
        else:
            match_import = re.search(r'import org.junit.jupiter.api.*', generate_content)
            if not match_import:
                repair_code = add_import(repair_code, "import org.junit.jupiter.api.*")
            match_import = re.search(r'import static org.junit.jupiter.api.Assertions.*', generate_content)
            if not match_import:
                repair_code = add_import(repair_code, "import static org.junit.jupiter.api.Assertions.*")
        repair_code = re.sub(r'^#+\s+.*$', '', repair_code, flags=re.MULTILINE)

    match_package = re.search(r'package', repair_code)
    if not match_package:
        repair_code = add_package(repair_code, package_name)
    import_info = import_info_return(project_name, method_name)
    # repair_code = add_import(repair_code, "import java.util.*")
    # repair_code = add_import(repair_code, "import java.io.*")
    # repair_code = add_import(repair_code, "import java.lang.*")
    for item in import_info:
        repair_code = add_import(repair_code, item)

    return repair_code
    # if judge_error(repair_code):
    #     logging.info("\nthe content still with syntax error after repair:\n")
    #     logging.info("original content: -------------------\n" + generate_content)
    #     logging.info("\nrepaired content: -------------------\n" + repair_code)
    #     try:
    #         tree = javalang.parse.parse(repair_code)
    #     except Exception as e:
    #         logging.error(e)
    #     return False
    # return True

        


if __name__ == '__main__':


    current_directory = 'generate_result/gpt4_generate_result'

    total = 0
    error_total = 0
    repair_total = 0
    for root, dirs, files in tqdm(os.walk(current_directory)):
        for file in files:
            if file == 'result.json':
                file_path = os.path.join(root, file)
                with open (file_path, 'r') as f:
                    json_content = f.read()
                    json_content = json.loads(json_content)
                package_name = json_content['package']
                method_name = json_content['method_name']
                class_name = json_content['class_name']
                generate_tests = json_content['generate_test']
                for generate_test in generate_tests:
                    total += 1
                    if judge_error(generate_test):
                        error_total += 1
                        flag = repair_error(generate_test, package_name, class_name, method_name)
                        if flag:
                            repair_total += 1

    print("total: ", total)
    print("error_total: ", error_total)
    print("repair_total: ", repair_total)

