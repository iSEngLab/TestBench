import re

file_path1 = "codellama"
file_path2 = "chatgpt"
file_path3 = "gpt4"

def read_log_and_handle(file_path):
    
    failure_number = 0
    error_number = 0
    total_number = 0
    error_dict = {}
    test_results = []
    with open('log/java_project_execute_' + file_path + '_new.log', 'r') as file:
        log_content = file.read()
        
    test_to_build_pattern = r"(\[INFO\]  T E S T S.*?\[INFO\] BUILD)"
    matches_blocks = re.findall(test_to_build_pattern, log_content, re.DOTALL)

    for match in matches_blocks:
        pattern = r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)"    
        matches = re.findall(pattern, match)
        if matches:
            match = matches[-1]
            total_number += 1
            if int(match[1]) > 0:
                failure_number += 1
            if int(match[2]) > 0:
                error_number += 1
            test_results.append({
                "Tests run": match[0],
                "Failures": match[1],
                "Errors": match[2],
                "Skipped": match[3]
            })
    
    print(f'{file_path} -- Failure: {failure_number}, Error: {error_number}, Total: {total_number}')
    with open('reTest_' + file_path + '.txt', 'w') as f:
        for result in test_results:
            f.write(f'Tests run: {result["Tests run"]}, Failures: {result["Failures"]}, Errors: {result["Errors"]}, Skipped: {result["Skipped"]}\n')


read_log_and_handle(file_path1)
read_log_and_handle(file_path2)
read_log_and_handle(file_path3)