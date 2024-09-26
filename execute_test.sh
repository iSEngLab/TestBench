#!/bin/bash
# Clean up previous logs
> nohup.out
# > filter.out

# Check and remove java_project_execute.log if it exists
if [ -f "./log/java_project_execute.log" ]; then
    rm -f ./log/java_project_execute.log
fi

# Check and remove coverage.json if it exists
if [ -f "./coverage_result/coverage.json" ]; then
    rm -f ./coverage_result/coverage.json
fi

# Check and remove files in test_result if the directory exists
if [ -d "./chatgpt_test_result" ]; then
    rm -rf ./chatgpt_test_result/*
fi

# change conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate testeval

# Run the python script and filter the output
# nohup sh -c 'python execute_test.py | tee nohup.out | grep -E "\d+%|\|.*?\|.*?/\d+.*?\[.*?\].*?/it" > filter.out' &
nohup python execute_test.py &