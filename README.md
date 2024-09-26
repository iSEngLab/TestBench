# TestBench

TestBench is a class level benchmark to evaluate the performance of LLMs on test case generation task. TestBench includes 108 Java programs sourced from several popular open-source projects and provides three types of context descriptions: Self-Contained Context, Full Context and Simple Context. Additionally, it build a comprehensive evaluation framework from five perspectives to evaluate the accuracy of generated test cases. 

## Usage

The directory structure of this project is as follows:
```
.
├─ content_repair.py
├─ execute_test.py
├─ execute_test.sh
├─ extract_raw_file.py
├─ generate_test_chatgpt.py
├─ generate_test_codellama.py
├─ generate_test_gpt4.py
├─ parser_log_compile.py
├─ parser_log_test_error.py
├─ parse_jacoco.py
├─ parse_result.py
├─ prompts.py
├─ README.md
│
├─ coverage_result
├─ generate_result
├─ source_file_parser
└─ test_result
```
The `source_file_parser` saves the source code and other information in the following format.

```
{
    "project_name": "***"
    "file_name": "***.java",
    "relative_path": "method path based on project path",
    "execute_path": "pom.xml path based on project path",
    "package": "package statement here",
    "docstring": "***",
    "source_code": "source code here",
    "class_name": "class name",
    "method_name": "method name",
    "argument_name": [a list here],
    "full_context": "full context here",
    "simple_context": "simple context here"
}
```

`generate_result` saves the original output of CodeLLama, GPT-3.5 and GPT-4 on TestBench.

`test_result` and `coverage_result` respectively save the test results and coverage calculation results of LLMs on TestBench.

To evaluate other LLMs on TestBench, you should first download the specific Java project, available at https://drive.google.com/file/d/1syRdGJfvM7ZWlvEwuEBFrYDNrtw-NGzh/view?usp=sharing.

Then, generate test cases based on the prompts in `prompts.py`. You can refer to all three `generate_test_*.py` files to understand the detailed usage of different prompts.

Then use `execute_test.sh` to execute tests. 

Finally, use `parse_result.py`, `parse_jacoco.py`, `parse_log_compile.py`, and `parse_log_test_error.py` to analyze the results.
