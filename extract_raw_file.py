#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
this script is used to extract information from source project.
information includes: Full Context, Simple Context, method content, method docstring and etc.

the input is a txt file, each block contains the relative path of the java file and start/end line number of the method.
the output is a json file, each block contains the information of the method.
"""

import javalang
import os
import json

source_file_path = "source_file_total.txt"
# ------------- need to modify based on env --------------------
relative_project_path = "/home/joseph/java_project/"
output_file_path = "source_file_parser/"


def extract_blocks(file_path):
    """
    extract blocks from a txt file.
    Return a list of block, each block contains 
    the relative path of the java file and start/end line number of the method.
    """

    blocks = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        num_lines = len(lines)
        i = 0
        while i + 4 <= num_lines:
            path = lines[i].strip()  # get the relative path of the java file
            start_line = lines[i + 1].strip()  # get the start line number
            end_line = lines[i + 2].strip()  # get the end line number
            execute_path = lines[i + 3].strip()  # get the execute path
            if path and start_line and end_line:
                try:
                    start_line = int(start_line)
                    end_line = int(end_line)
                    if end_line > start_line:
                        block = {'path': path, 'start_line': start_line, 'end_line': end_line, 'execute_path': execute_path}
                        blocks.append(block)
                    else:
                        print(f"Invalid block at line {i + 3}: end_line must be greater than start_line. Skipping block.")
                except ValueError:
                    print(f"Invalid block at line {i + 3}: start_line and end_line must be integers. Skipping block.")
            else:
                print(f"Invalid block at line {i + 3}: Missing information. Skipping block.")
            i += 5
    return blocks

def extract_lines_from_file(file_path, start_line, end_line):
    """
    Extract lines from a file based on the start and end line numbers.
    Returns the content between the start and end lines.
    """

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            content = ''.join(lines[start_line-1:end_line])
            return content
    except FileNotFoundError:
        print("File path error or file does not exist!")
        return None
    except IndexError:
        print("Start line or end line is out of file range!")
        return None
    
def read_file(file_path):
    """
    Read a file and return the content.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print("File path error or file does not exist!")
        return None
    
def extract_path(file_path):
    """
    Extract the project name and file name from a file path.
    """
    path = file_path.split('/')
    return path[0], path[-1]
    
def remove_comments_and_fix_indentation(code, comment):
    """
    Removes comments from the code and fixes the indentation.

    Args:
        code (str): The code to remove comments and fix indentation.
        comment (str): The comment string to be removed.

    Returns:
        str: The code without comments and with fixed indentation.
    """
    # Remove comments
    code_without_comments = code
    if comment != None:
        code_without_comments = code.replace(comment, '')
    # Fix indentation
    lines = code_without_comments.split('\n')
    if lines:
        indent = len(lines[0]) - len(lines[0].lstrip())
        fixed_lines = [line[indent:] for line in lines]
        fixed_code = '\n'.join(fixed_lines)
        return fixed_code
    else:
        return code_without_comments
    
def parse_source_code(code, path):
    """
    Parse the source code and return the methods and docstrings.
    """
    method_name = ""
    arguments = []
    try:
        tokens = javalang.tokenizer.tokenize(code)
        parser = javalang.parser.Parser(tokens)
        tree = parser.parse_member_declaration()
        docstring = tree.documentation
        method_name = tree.name
        arguments = [parse_formal_parameter(i) for i in tree.parameters]
        method = remove_comments_and_fix_indentation(code, docstring)
        return method, docstring, method_name, arguments
    except javalang.parser.JavaSyntaxError:
        print("-----Java syntax error! please check the code-----")
        print("path: ", path)
        return None, None, None, None
    
def parse_file(content, path):
    """
    parse a file and return the simple context and full context.
    """
    if path == "javacv/src/main/java/org/bytedeco/javacv/FFmpegFrameGrabber.java:490-515":
        a = 1
    simple_context = ""
    package_name = ""
    class_name = ""
    try:
        tree = javalang.parse.parse(content)
        if tree.package:
            simple_context += "package " + tree.package.name + ";\n\n"
            package_name = tree.package.name
        if len(tree.imports) > 0:
            for i in tree.imports:
                simple_context += "import " + ("static " if i.static else "") + i.path + ";\n\n"
        if len(tree.types) > 0:
            for node in tree.types:
                if isinstance(node, javalang.tree.ClassDeclaration) and not class_name:
                    class_name = node.name
                node_signature = parse_node(node)
                simple_context += node_signature + "\n"
        return simple_context, content, package_name, class_name
    except Exception as e:
        print("-----Java syntax error! please check the file-----")
        print("path: ", path)
        print(e)
        return None, None, None, None

def parse_node(node, indent=0):
    """
    Parse a node and return the signature.
    """
    if isinstance(node, javalang.tree.FieldDeclaration):
        declaration = " " * indent
        if node.modifiers:
            declaration += " ".join(node.modifiers) + " "
        declaration += parse_reference_type(node.type) + " "
        declarator_names = [i.name for i in node.declarators]
        declaration += ", ".join(declarator_names)
        return declaration + ";\n"
    
    if isinstance(node, javalang.tree.MethodDeclaration):
        declaration = " " * indent
        if node.modifiers:
            declaration += " ".join(node.modifiers) + " "
        declaration += parse_reference_type(node.return_type) + " "
        declaration += node.name + "("
        declaration += ", ".join([parse_formal_parameter(i) for i in node.parameters]) + ")"
        if node.throws:
            declaration += "throws " + ", ".join(node.throws)
        return declaration + ";\n"
    
    if isinstance(node, javalang.tree.ConstructorDeclaration):
        declaration = " " * indent
        if node.modifiers:
            declaration += " ".join(node.modifiers) + " "
        declaration += node.name + "("
        declaration += ", ".join([parse_formal_parameter(i) for i in node.parameters]) + ")"
        return declaration + ";\n"
    
    if isinstance(node, javalang.tree.EnumDeclaration):
        declaration = " " * indent
        if node.modifiers:
            declaration += " ".join(node.modifiers) + " "
        declaration += "enum " + node.name + "{"
        declaration += ", ".join(i.name for i in node.body.constants) + "}"
        return declaration + "\n"
    
    if isinstance(node, javalang.tree.ClassDeclaration):
        declaration = " " * indent
        if node.modifiers:
            declaration += " ".join(node.modifiers) + " "
        declaration += "class " + node.name
        if node.extends:
            declaration += " extends " + parse_reference_type(node.extends)
        if node.implements:
            declaration += " implements " + ", ".join([parse_reference_type(i) for i in node.implements])
        declaration += " {\n"
        if node.body:
            for i in node.body:
                declaration += parse_node(i, indent=indent+4)
        declaration += " " * indent + "}\n"
        return declaration
    return ""

def parse_reference_type(node):
    """
    A fucking helpful method to parse the fucking reference type.
    """
    declaration = ""
    if isinstance(node, javalang.tree.ReferenceType):
        args = node.arguments
        if args is None:
            # arg_name = args.name
            return node.name
        else:
            arg_name = [parse_reference_type(i.type) for i in args]
        declaration += node.name + ("<" + ", ".join(arg_name) + ">" if args else "")
    else:
        declaration += parse_basic_type(node)
    return declaration

def parse_formal_parameter(node):
    """
    A fucking helpful method to parse the fucking formal parameter type.
    """
    if isinstance(node, javalang.tree.FormalParameter):
        return parse_reference_type(node.type) + " " + node.name

def parse_basic_type(node):
    """
    A fucking helpful method to parse the fucking basic type.
    """
    declaration = ""
    if isinstance(node, javalang.tree.BasicType):
        declaration += node.name
        for i in node.dimensions:
            declaration += "[]"
    return declaration

def update_json_file(file_path, data):
    """
    Update the JSON file with new data.
    """
    file_exists = os.path.isfile(file_path)
    if file_exists:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if item not in existing_data:
            existing_data.append(item)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4)
    return existing_data
        
if __name__ == "__main__":
    current_path = os.getcwd()
    blocks = extract_blocks(source_file_path)
    for each in blocks:
        os.chdir(relative_project_path)
        relative_path = each['path']
        execute_path = each['execute_path']
        project_name, file_name = extract_path(relative_path)
        code = extract_lines_from_file(relative_path, each['start_line'], each['end_line'])
        file = read_file(relative_path)
        simple_context, full_context, package_name, class_name = parse_file(file, relative_path + ":" + str(each['start_line']) + "-" + str(each['end_line']))
        source_code, docstring, method_name, arguments = parse_source_code(code, relative_path + ":" + str(each['start_line']) + "-" + str(each['end_line']))
        # TODO: add java execute path
        data = {
            "project_name": project_name,
            "file_name": file_name,
            "relative_path": relative_path,
            "execute_path": execute_path,
            "package": package_name,
            "docstring": docstring,
            "source_code": source_code,
            "class_name": class_name,
            "method_name": method_name,
            "argument_name": arguments,
            "full_context": full_context,
            "simple_context": simple_context
        }
        os.chdir(current_path)
        if not os.path.exists(output_file_path):
            os.makedirs(output_file_path)
        update_json_file(output_file_path + data['project_name'] + "_out.json", data)
