import json
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil


def traverse_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list


input_path = "./test_result/codellama_new"
output_path = "./img/codellama_new_repair"

file_list = traverse_directory(input_path)

def clear_output_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
    os.makedirs(os.path.join(directory, 'detail'))

clear_output_dir(output_path)


project_counts_simple = [0, 0, 0, 0]
project_counts_full = [0, 0, 0, 0]
project_counts_only = [0, 0, 0, 0]
all_errors = ["Syntax Error", "Compile Error", "Test Error", "Accept"]
color_dict = {"Compile Error": "RoyalBlue", "Syntax Error": "red", "Test Error": "Gold", "Accept": "LimeGreen"}

for item in file_list:
    with open(item, 'r') as file:
        json_data = json.load(file)
    item_counts_simple = [0, 0, 0, 0]
    item_counts_full = [0, 0, 0, 0]
    item_counts_only = [0, 0, 0, 0]
    project_name = "null"
    for i in range(len(json_data)):
        data = json_data[i]

        figure_name = data['project_name'] + '_' + data['class_name'] + '_' + data['method_name']
        project_name = data['project_name']
        source_code_simple = data['SourceCode&Simple']
        source_code_full = data['SourceCode&Full']
        source_code_only = data['SourceCodeOnly']

        errors_simple = {error: source_code_simple.count(error) for error in set(source_code_simple)}
        errors_full = {error: source_code_full.count(error) for error in set(source_code_full)}
        errors_only = {error: source_code_only.count(error) for error in set(source_code_only)}

        counts_simple = [errors_simple.get(error, 0) for error in all_errors]
        counts_full = [errors_full.get(error, 0) for error in all_errors]
        counts_only = [errors_only.get(error, 0) for error in all_errors]

        project_counts_simple = [project_counts_simple[j] + counts_simple[j] for j in range(len(all_errors))]
        project_counts_full = [project_counts_full[j] + counts_full[j] for j in range(len(all_errors))]
        project_counts_only = [project_counts_only[j] + counts_only[j] for j in range(len(all_errors))]

        item_counts_simple = [item_counts_simple[j] + counts_simple[j] for j in range(len(all_errors))]
        item_counts_full = [item_counts_full[j] + counts_full[j] for j in range(len(all_errors))]
        item_counts_only = [item_counts_only[j] + counts_only[j] for j in range(len(all_errors))]

        bar_width = 0.35
        index = np.arange(3)

        plt.clf()
        bottom = np.zeros(3)
        for error, count_simple, count_full, count_only in zip(all_errors, counts_simple, counts_full, counts_only):
            plt.bar(index, [count_simple, count_full, count_only], bar_width, bottom=bottom, label=error, color=color_dict[error])
            bottom += [count_simple, count_full, count_only]

        plt.xlabel('Type')
        plt.ylabel('Count')
        plt.xticks(index, ['SourceCode&Simple', 'SourceCode&Full', 'SourceCodeOnly'])
        plt.title(figure_name)
        plt.legend()
        plt.savefig(output_path + "/detail/bar_" + figure_name + '.png')

        plt.close()

    item_counts_total = [item_counts_simple[j] + item_counts_full[j] + item_counts_only[j] for j in range(len(all_errors))]
    plt.clf()
    plt.pie(item_counts_total, labels=all_errors, colors=[color_dict[error] for error in all_errors], autopct='%1.1f%%')
    plt.title('total count')
    plt.savefig(output_path + "/pie_" + project_name + ".png")
    plt.close()

bar_width = 0.35
index = np.arange(3)
plt.clf()
bottom = np.zeros(3)
for error, count_simple, count_full, count_only in zip(all_errors, project_counts_simple, project_counts_full, project_counts_only):
    plt.bar(index, [count_simple, count_full, count_only], bar_width, bottom=bottom, label=error, color=color_dict[error])
    bottom += [count_simple, count_full, count_only]

plt.xlabel('Type')
plt.ylabel('Count')
plt.xticks(index, ['SourceCode&Simple', 'SourceCode&Full', 'SourceCodeOnly'])
plt.title('total count')
plt.legend()
plt.savefig(output_path + "/bar_total.png")

plt.close()

project_counts_total = [project_counts_simple[j] + project_counts_full[j] + project_counts_only[j] for j in range(len(all_errors))]
plt.clf()
plt.pie(project_counts_total, labels=all_errors, colors=[color_dict[error] for error in all_errors], autopct='%1.1f%%')
plt.title('total count')
plt.savefig(output_path + "/pie_total.png")
plt.close()

for counts, name in zip([project_counts_only, project_counts_simple, project_counts_full], ['only', 'simple', 'full']):
    plt.clf()
    plt.pie(counts, labels=all_errors, colors=[color_dict[error] for error in all_errors], autopct='%1.1f%%')
    plt.title(name + ' count')
    plt.savefig(output_path + "/pie_" + name + ".png")
    plt.close()

print("Finish!")