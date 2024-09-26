import re

error_block_pattern = re.compile(
    r'\[ERROR\] COMPILATION ERROR : \n\[INFO\] -------------------------------------------------------------(.*?)\[INFO\] \d+ error(s?)',
    re.DOTALL
)

error_message_pattern = re.compile(
    r'^\[ERROR\] (?P<file>.+\.java):\[(?P<line>\d+),(?P<column>\d+)\] (?P<message>.+)$',
    re.MULTILINE
)


specific_error_patterns = [
    (re.compile(r'.* has private access in .*'), 'has private access in'),
    (re.compile(r'package .+ does not exist'), 'package does not exist'),
    (re.compile(r'cannot assign a value to final variable .+'), 'cannot assign a value to final variable'),
    (re.compile(r'.+ is not public in .+; cannot be accessed from outside package'), 'is not public in; cannot be accessed from outside package'),
    (re.compile(r'incompatible types: .+ cannot be converted to .+'), 'incompatible types cannot be converted'),
    (re.compile(r'constructor .+ in class .+ cannot be applied to given types;'), 'constructor cannot be applied to given types'),
    (re.compile(r'cannot find symbol'), 'cannot find symbol'),
    (re.compile(r'wrong number of type arguments; required \d+'), 'wrong number of type arguments'),
    (re.compile(r'local variables referenced from a lambda expression must be final or effectively final'), 'variables in lambda must be final or effectively final'),
    (re.compile(r'no suitable method found for .+\(.*\)'), 'no suitable method found'),
    (re.compile(r'.+ is not abstract and does not override abstract method .+ in .+'), 'class is not abstract and does not override abstract method'),
    (re.compile(r'unreported exception .+; must be caught or declared to be thrown'), 'unreported exception must be caught or declared to be thrown'),
    (re.compile(r'method does not override or implement a method from a supertype'), 'method does not override or implement a method from a supertype'),
    (re.compile(r'class .+ is public, should be declared in a file named .+\.java'), 'class is public, should be declared in a file with the same name'),
    (re.compile(r'reference to .+ is ambiguous'), 'reference is ambiguous'),
    (re.compile(r'missing return statement'), 'missing return statement'),
    (re.compile(r'exception .+ is never thrown in body of corresponding try statement'), 'exception is never thrown in body of corresponding try statement'),
    (re.compile(r'static import only from classes and interfaces'), 'static import only from classes and interfaces'),
    (re.compile(r'cannot inherit from final .+'), 'cannot inherit from final class'),
    (re.compile(r'incompatible types: possible lossy conversion from .+ to .+'), 'incompatible types: possible lossy conversion'),
    (re.compile(r'lambda expressions are not supported in -source \d+'), 'lambda expressions not supported in source version'),
    (re.compile(r'method references are not supported in -source \d+'), 'method references not supported in source version'),
    (re.compile(r'non-static variable .+ cannot be referenced from a static context'), 'non-static variable cannot be referenced from a static context'),
    (re.compile(r'.+ is abstract; cannot be instantiated'), 'abstract class cannot be instantiated')
]

file_path1 = "codellama"
file_path2 = "chatgpt"
file_path3 = "gpt4"

def read_log_and_handle(file_path):
    
    error_dict = {}
    with open('log/java_project_execute_' + file_path + '_new.log', 'r') as file:
        log_content = file.read()
        error_blocks = error_block_pattern.findall(log_content)
        for block in error_blocks:
            error_messages = error_message_pattern.finditer(block[0])
            append_list = []
            for match in error_messages:
                original_error_message = match.group('message')
                generalized_error_message = original_error_message
                for pattern, general_message in specific_error_patterns:
                    if pattern.match(original_error_message):
                        generalized_error_message = general_message
                        break
                if generalized_error_message not in append_list:
                    append_list.append(generalized_error_message)
                    if generalized_error_message in error_dict:
                        error_dict[generalized_error_message] += 1
                    else:
                        error_dict[generalized_error_message] = 1

    error_dict = dict(sorted(error_dict.items(), key=lambda item: item[1], reverse=True))

    # for error, count in error_dict.items():
    #     print(f'Error: {error}, Count: {count}')

    with open('record_' + file_path + '.txt', 'w') as f:
        for error, count in error_dict.items():
            f.write(f'Error: {error}, Count: {count}\n')

read_log_and_handle(file_path1)
read_log_and_handle(file_path2)
read_log_and_handle(file_path3)
