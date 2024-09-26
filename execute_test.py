import json
import javalang
import os
import subprocess
import re
import logging
from tqdm import tqdm
from extract_raw_file import update_json_file
# from parse_clover import get_coverage
from parse_jacoco import get_coverage
import generate_content_repair

basic_path = "./generate_result/codellama_generate_result/"
append_path = "./test_result/temp/"
relative_project_path = "/home/joseph/java_project/"
coverage_path = "/home/joseph/TestCaseGeneration/coverage_result/"
# --------------------------------------------------------------
current_path = os.getcwd()
logging.basicConfig(filename='log/java_project_execute.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def path_handle(path):
    project_list = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            for sub_item in os.listdir(os.path.join(path, item)):
                if os.path.isdir(os.path.join(path, item, sub_item)):
                    project_list.append(os.path.join(path, item, sub_item))
    return project_list

def json_reader(path): 
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def syntax_judge(code, clean=False):
    try:
        tree = javalang.parse.parse(code)
        index = 0
        while('public' not in tree.types[index].modifiers):
            index += 1
        try:
            class_name = tree.types[index].name
        except:
            class_name = tree.types[0].name
        return class_name
    except Exception as e:
        if clean:
            return None
        logging.error("Syntax Error")
        logging.error(e)
        return None

def write_file(path, class_name, code):
    delete_file(path, class_name)
    # print(path + "/" + class_name + ".java")
    with open(os.path.join(path, class_name + ".java"), 'w') as f:
        f.write(code)

def delete_file(path, class_name):  
    if os.path.exists(os.path.join(path, class_name + ".java")):
        os.remove(os.path.join(path, class_name + ".java"))
        return True
    return False

def clean_path(path_list):
    print("strat cleaning...")
    count = 0
    for second_path in tqdm(path_list):
        for item in os.listdir(second_path):
            data = json_reader(os.path.join(second_path, item, "result.json"))
            relative_path = os.path.join(relative_project_path, data['relative_path'])
            test_path = relative_path.replace("main", "test").rsplit("/", 1)[0]
            for each_result in data['generate_test']:
                class_name = syntax_judge(each_result, True)
                if class_name is not None:
                    ret = delete_file(test_path, class_name)
                    if ret:
                        count += 1
    print("Finish! clean " + str(count) + " files")


def write_coverage_result(path, data):
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, "coverage_new.json")
    file_exists = os.path.exists(file_path)
    if file_exists:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []
    existing_data.append(data)
    with open(file_path, 'w', encoding='utf-8') as file:   
        json.dump(existing_data, file, indent=4)

def result_evaluate(generate_code, file_path, class_name, method_name, package_name, project_name, context):
    result_list = []
    for j in range(len(generate_code)):
        logging.info("\nclass_name: " + class_name + " method_name: " + method_name + " index: " + str(j + 1))
        logging.info("\npath: " + file_path)
        logging.info("\ncode: " + generate_code[j])

        # logging.info("\nUsing code repair rules...")
        repair_code = generate_content_repair.repair_error(generate_code[j], package_name, class_name, method_name, project_name)
        # repair_code = generate_code[j]

        logging.info("\nrepair_code: " + repair_code)

        syntax_ret = syntax_judge(repair_code)
        if not syntax_ret:
            result_list.append('Syntax Error')
            continue
        
        # Write the code to the file for compilation check
        # -Drat.skip=true is added to skip License checks
        # -Dsurefire.failIfNoSpecifiedTests=false is to skip classes with no tests
        # For new projects, the required parameters may vary, so frequent modifications might be needed.
        write_file(file_path, syntax_ret, repair_code)
        logging.info("####################  mvn clean test-compile  ####################")
        sp = subprocess.Popen(
            "mvn clean test-compile -Drat.skip=true -Dsurefire.failIfNoSpecifiedTests=false -Dcheckstyle.skip",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,shell=True)
        stdout, stderr = sp.communicate(timeout=60)
        output_str = stdout.decode('utf-8')
        logging.info(output_str)
        pattern = r'BUILD (SUCCESS|FAILURE)'  
        match = re.search(pattern, output_str)  
        if match:
            build_status = match.group(1) 
            if build_status != "SUCCESS":
                result_list.append('Compile Error')
                delete_file(file_path, syntax_ret)
                continue

        # Perform test check
        # -DskipPitest=True is to skip Pitest check (Pitest is bound to the test phase in this project)
        # -Drat.skip=true is a parameter added to skip License checks
        # -Dsurefire.failIfNoSpecifiedTests=false is to skip classes with no tests
        # For new projects, the required parameters may vary, so frequent modifications might be needed.
        logging.info("####################  mvn test -Dtest=" + syntax_ret + "####################")
        try:
            sp = subprocess.Popen(
                "mvn clean test -DskipPitest=True -Drat.skip=true -Dsurefire.failIfNoSpecifiedTests=false -Dcheckstyle.skip -Dtest=" + syntax_ret,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, shell=True)
            stdout, stderr = sp.communicate(timeout=120)
        except:
            logging.info("Test Timeout")
            result_list.append('Test Error')
            delete_file(file_path, syntax_ret)
            continue
        output_str = stdout.decode('utf-8')
        logging.info(output_str)
        pattern = r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)'
        match = re.search(pattern, output_str)
        if match:
            test_status = match.group(2)
            if test_status != "0":
                result_list.append('Test Error')
                delete_file(file_path, syntax_ret)
                continue
        pattern = r'BUILD (SUCCESS|FAILURE)'  
        match = re.search(pattern, output_str)  
        if match:
            build_status = match.group(1)  
            if build_status != "SUCCESS":
                result_list.append('Test Error')
                delete_file(file_path, syntax_ret)
                continue
        
        result_list.append('Accept')

        logging.info("####################  Coverage Calculate: " + syntax_ret + " ####################")
        this_path = os.getcwd()
        package_metric, class_metric, method_metric = get_coverage(this_path, package_name, syntax_ret, method_name)
        logging.info("project_name: " + project_name)
        logging.info("file_path: " + file_path)
        logging.info("package_name: " + package_name)
        logging.info("class_name: " + class_name)
        logging.info("method_name: " + method_name)
        logging.info("project_metric: " + str(package_metric))
        logging.info("package_metric: " + str(class_metric))
        logging.info("method_metric: " + str(method_metric))

        logging.info("####################  Mutation Test: " + syntax_ret + " ####################")
        targetClasses = package_name + "." + class_name
        targetTests = package_name + "." + syntax_ret
        logging.info("mvn command: mvn clean test-compile org.pitest:pitest-maven:mutationCoverage -Drat.skip=true -Dcheckstyle.skip -DtargetClasses=\"" + targetClasses + "\" -DtargetTests=\"" + targetTests + "\"")
        logging.info("targetClasses: " + targetClasses)
        logging.info("targetTests: " + targetTests)
        try:
            sp = subprocess.Popen(
                'mvn clean test-compile org.pitest:pitest-maven:mutationCoverage -Drat.skip=true -Dcheckstyle.skip -DtargetClasses="' + targetClasses + '" -DtargetTests="' + targetTests + '"',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, shell=True)
            stdout, stderr = sp.communicate(timeout=120)
            output_str = stdout.decode('utf-8')
            logging.info(output_str)
            pattern = r"Generated \d+ mutations Killed \d+ \((\d{1,3})%\)"
            matches = re.findall(pattern, output_str)
            if matches:
                percentages = [int(m) for m in matches]
                average_percentage = sum(percentages) / len(percentages)
            else:
                average_percentage = -1
        except Exception as e:
            logging.info("Mutation Test Timeout")
            logging.info(e)
            average_percentage = -1
            
        coverage_data = {
            "context": context,
            "project_name": project_name,
            "file_path": file_path,
            "package_name": package_name,
            "class_name": class_name,
            "method_name": method_name,
            "test_code": repair_code,
            "package_metric": package_metric,
            "class_metric": class_metric,
            "method_metric": method_metric,
            "pitest": average_percentage
        }
        write_coverage_result(coverage_path, coverage_data)

        delete_file(file_path, syntax_ret)

    return result_list

if __name__ == "__main__":

    path_list = path_handle(basic_path)

    clean_path(path_list)

    if not os.path.exists(append_path):
        os.makedirs(append_path)

    for second_path in tqdm(path_list):
        # os.chdir(current_path)
        each_result = {}
        project_name = "unknown"
        for item in os.listdir(second_path):
            os.chdir(current_path)
            data = json_reader(os.path.join(second_path, item, "result.json"))
            package = data['package']
            project_name = data['project_name']
            class_name = data['class_name']
            method_name = data['method_name']
            relative_path = os.path.join(relative_project_path, data['relative_path'])
            each_result['project_name'] = data['project_name']
            each_result['code'] = data['source_code']
            each_result['package'] = data['package']
            each_result['class_name'] = data['class_name']
            each_result['method_name'] = data['method_name']
            os.chdir(os.path.join(relative_project_path, data['execute_path']))
            test_path = relative_path.replace("main", "test").rsplit("/", 1)[0]
            if not os.path.exists(test_path):
                os.makedirs(test_path)
            execute_result = result_evaluate(data['generate_test'], test_path, class_name, method_name, package, project_name, item)
            each_result[item] = execute_result

        os.chdir(current_path)
        update_json_file(os.path.join(append_path, project_name + '_result.json'), each_result)
        # update_json_file("total_result.json", each_result)
    
    print("Finish!")

        

















