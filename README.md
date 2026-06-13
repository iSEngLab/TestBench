# TestBench: Evaluating Class-Level Test Case Generation Capability of Large Language Models

[![FCS 2025](https://img.shields.io/badge/FCS-2025-blue)]()

TestBench is a class-level benchmark for evaluating the test case generation capability of Large Language Models (LLMs). It comprises **108 Java classes** sourced from popular open-source projects and evaluates generated test cases from **five complementary perspectives**: compilation rate, test execution rate, line coverage, branch coverage, and mutation score.

TestBench provides three distinct context configurations — **Self-Contained Context**, **Full Context**, and **Simple Context** — enabling systematic analysis of how different types and amounts of contextual information affect LLM test generation performance.

## Context Types

| Type | Description |
|------|-------------|
| **Self-Contained Context** | The class under test along with the full source code of all directly referenced classes within the same project. Represents the richest context setting. |
| **Full Context** | The class under test plus a minimal set of dependency information (imports and method signatures of referenced classes), providing a medium level of context. |
| **Simple Context** | Only the class under test with its method signatures and docstrings. Represents the most constrained context setting. |

These three context configurations form a progressive spectrum, allowing researchers to measure how LLMs degrade (or improve) as available context varies from rich to minimal.

## Dataset Overview

TestBench includes 108 Java classes drawn from several well-known open-source projects:

| Project | Description |
|---------|-------------|
| Java | JDK standard library classes |
| commons-lang | Apache Commons Lang utilities |
| commons-math | Apache Commons Math library |
| JCTools | Java Concurrency Tools |
| javacv | JavaCV computer vision library |
| jfreechart | Chart creation library |
| jeecg-boot | Enterprise rapid development platform |
| zxing | Barcode image processing library |
| apollo | Configuration management platform |

Each class is accompanied by an executable path to its Maven `pom.xml`, enabling automated compilation and test execution within the project's native build environment.

## Evaluation Framework

TestBench evaluates LLM-generated test cases through five dimensions, forming a comprehensive pipeline from syntactic correctness to functional adequacy:

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Compilation Rate** | The proportion of generated test files that compile successfully. A basic syntactic correctness gate. |
| **Test Execution Rate** | Among compiled tests, the proportion that run without errors. Validates runtime compatibility. |
| **Line Coverage** | The percentage of source code lines exercised by generated tests, measured via JaCoCo. |
| **Branch Coverage** | The percentage of conditional branches exercised by generated tests, measured via JaCoCo. |
| **Mutation Score** | The proportion of artificial faults (mutants) that are killed by the generated tests, reflecting fault-detection capability. |

### Evaluation Pipeline

```
LLM Output → content_repair.py → execute_test.sh → parse_result.py
                (syntax fix)       (Maven build)     (test results)
                                                   parse_jacoco.py
                                                   (coverage analysis)
```

## Evaluated Systems

| Model | Variant | Contexts Tested |
|-------|---------|-----------------|
| CodeLLama | — | Self-Contained, Full, Simple |
| GPT-3.5 (ChatGPT) | — | Self-Contained, Full, Simple |
| GPT-4 | — | Self-Contained, Full, Simple |

## Repository Structure

```
TestBench/
├── prompts.py                              # Prompt templates for three context types
├── generate_test_chatgpt.py                # GPT-3.5 test generation runner
├── generate_test_gpt4.py                   # GPT-4 test generation runner
├── generate_test_codellama.py              # CodeLLama test generation runner
├── extract_raw_file.py                     # Source file parsing utilities
├── content_repair.py                       # Post-generation syntax repair
├── execute_test.py                         # Test execution logic
├── execute_test.sh                         # Shell wrapper for Maven-based test runs
├── parser_log_compile.py                   # Compilation log parser
├── parser_log_test_error.py                # Test error log parser
├── parse_jacoco.py                         # JaCoCo coverage result parser
├── parse_result.py                         # Aggregated result analysis
│
├── source_file_parser/                     # Source code and metadata (JSON per project)
│   ├── Java_out.json
│   ├── commons-lang_out.json
│   ├── commons-math_out.json
│   ├── JCTools_out.json
│   ├── javacv_out.json
│   ├── jfreechart_out.json
│   ├── jeecg-boot_out.json
│   ├── zxing_out.json
│   └── apollo_out.json
│
├── generate_result/                        # Raw LLM outputs across all contexts
│   ├── chatgpt_generate_result/
│   ├── gpt4_generate_result/
│   └── codellama_generate_result/
│
├── test_result/                            # Test execution results (before/after repair)
│   ├── chatgpt_test_result_before_repair/
│   ├── chatgpt_test_result_after_repair/
│   ├── gpt4_test_result_before_repair/
│   ├── gpt4_test_result_after_repair/
│   ├── codellama_test_result_before_repair/
│   └── codellama_test_result_after_repair/
│
└── coverage_result/                        # Line/branch coverage results (before/after repair)
    ├── chatgpt_coverage_before_repair.json
    ├── chatgpt_coverage_after_repair.json
    ├── gpt4_coverage_before_repair.json
    ├── gpt4_coverage_after_repair.json
    ├── codellama_coverage_before_repair.json
    └── codellama_coverage_after_repair.json
```

## Usage

### Prerequisites

- Python 3.8+
- Java 8+ (JDK)
- Maven 3.x

### Step 1 — Download Java Projects

Download the Java project repositories from Google Drive:

🔗 **Dataset:** https://drive.google.com/file/d/1syRdGJfvM7ZWlvEwuEBFrYDNrtw-NGzh/view?usp=sharing

### Step 2 — Generate Test Cases

Use the generation scripts with the prompts defined in `prompts.py`. Each script targets a specific LLM:

```bash
# Generate with GPT-4
python generate_test_gpt4.py

# Generate with GPT-3.5
python generate_test_chatgpt.py

# Generate with CodeLLama
python generate_test_codellama.py
```

The prompts in `prompts.py` provide three context configurations:
- **Self-Contained Context**: richest, includes full transitive dependency source code
- **Full Context**: medium, includes imports and method signatures of dependencies
- **Simple Context**: minimal, only the class under test

### Step 3 — Execute Tests

```bash
bash execute_test.sh
```

This script compiles and runs all generated test cases within their respective Maven project environments.

### Step 4 — Analyze Results

```bash
# Parse test execution results
python parse_result.py

# Parse JaCoCo coverage data
python parse_jacoco.py

# Analyze compilation logs
python parser_log_compile.py

# Analyze test error logs
python parser_log_test_error.py
```

### Optional — Content Repair

Before execution, `content_repair.py` can automatically fix common syntactic issues (e.g., missing imports, malformed assertions) in generated test code to isolate semantic quality from syntax errors.

## Source File Format

Each entry in `source_file_parser/` follows this JSON schema:

```json
{
    "project_name": "***",
    "file_name": "***.java",
    "relative_path": "method path relative to project root",
    "execute_path": "pom.xml path relative to project root",
    "package": "package declaration",
    "docstring": "***",
    "source_code": "full source code of the class under test",
    "class_name": "class name",
    "method_name": "method name",
    "argument_name": ["arg1", "arg2"],
    "full_context": "dependency classes with full source code",
    "simple_context": "class under test only"
}
```

## Dependencies

```
Python 3.8+
Java 8+ (JDK)
Maven 3.x
```

## Research Applications

TestBench is designed to support research in:

- **LLM-based test generation** — systematic evaluation of how different LLMs perform on unit test generation for real-world Java classes.
- **Context sensitivity analysis** — studying how varying levels of project context (Simple, Full, Self-Contained) impact generation quality.
- **Test repair** — evaluating whether LLMs can fix compilation and runtime errors in their own generated tests via the before/after repair comparison.
- **Coverage-guided generation** — analyzing the relationship between context richness and achieved line/branch coverage.
- **Mutation testing** — assessing the fault-detection strength of LLM-generated test suites.

## Citation

If you use TestBench in your research, please cite:

```bibtex
@article{testbench2025,
  title     = {TestBench: Evaluating Class-Level Test Case Generation Capability of Large Language Models},
  journal   = {Frontiers of Computer Science (FCS)},
  year      = {2025},
  publisher = {Springer}
}
```

## License

This project is provided for research purposes.