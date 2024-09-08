import random
import subprocess
import re
import os
import time
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
from colorama import Fore, Style, init
from pyfiglet import figlet_format

# Inizializza colorama
init(autoreset=True)

# Funzione per stampare una sezione con un titolo decorato, viene usata fra le varie fasi del programma
def print_section(title):
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + title.center(50))
    print(Fore.CYAN + Style.BRIGHT + "=" * 50 + "\n")

# Funzione per mostrare il titolo del programma
def print_title():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.GREEN + figlet_format("TreeXplain", font="slant"))
    print(Fore.YELLOW + "A tool for exploring decision tree structures and for XAI demonstrations\n".center(80))
    print(Style.RESET_ALL)

# Tree exploration and conversion to ASP facts
def tree_to_asp(tree, feature_names, class_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    
    nodes = []
    edges = []
    thresholds = {}

    #recursive function to explore the tree in depth
    def recurse(node):
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            feature = feature_name[node].replace(" ", "")
            threshold = tree_.threshold[node]
            nodes.append(f'node({node},"{feature}<={threshold:.3f}").')
            
            if feature not in thresholds:
                thresholds[feature] = []
            thresholds[feature].append(threshold)
            
            left_child = recurse(tree_.children_left[node])
            right_child = recurse(tree_.children_right[node])
            
            edges.append(f'edge({node},{left_child},"+").')
            edges.append(f'edge({node},{right_child},"-").')
        else:
            class_label = tree_.value[node].argmax()
            class_name = class_names[class_label]
            nodes.append(f'node({node},"{class_name}").')

        return node

    recurse(0)
    return nodes, edges, thresholds

# Input values
def generate_inputs(thresholds, manual=False):
    input_values = {}
    input_strings = []
    random.seed(time.time())
    if manual:
        print(Fore.LIGHTBLACK_EX + f'Decimal number have triple digit precision, insert them with a dot (.) separator.')

    for feature, values in thresholds.items():
        # Ask user for input if manual is True insert values manually, otherwise generate random ones
        if manual:
            while True:
                try:
                    user_value = float(input(Fore.MAGENTA + f'Input value for "{feature}": ' + Fore.WHITE))
                    input_values[feature] = user_value
                    break
                except ValueError:
                    print(Fore.RED + "Please input a valid number.")
        else:
            values.sort()
            random_value = random.uniform(min(values), max(values))
            input_values[feature] = random_value

    for feature, values in thresholds.items():
        for threshold in values:
            if input_values[feature] <= threshold:
                input_strings.append(f'input("{feature}<={threshold:.3f}",1).')
            else:
                input_strings.append(f'input("{feature}<={threshold:.3f}",0).')

    return input_strings, input_values

# Substitute to Embasp😭😭
def run_dlv2_program(program_path, facts):
    asp_input = "\n".join(facts)
    with open("temp_input.asp", "w") as f:
        f.write(asp_input)
    
    result = subprocess.run(['dlv-2.1.1-windows64.exe', program_path, 'temp_input.asp'], capture_output=True, text=True)
    return result.stdout

# Convert the output of the ASP program to an easy to use format
# for inferenza.asp
def extract_output(asp_result):
    output_match = re.search(r'output\((\d+)\)', asp_result)
    name_match = re.search(r'outputName\("(\w+)"\)', asp_result)
    
    if output_match and name_match:
        return int(output_match.group(1)), name_match.group(1)
    return None, None

# for eco.asp
def extracteco(asp_result):
    optimum_match = re.search(r'{([^}]+)}\s*COST\s*\d+@\d\s*OPTIMUM', asp_result)
    
    if not optimum_match:
        return "No optimum result found."
    
    # Estrai il contenuto dell'optimum answer set
    optimum_set = optimum_match.group(1)
    
    # Estrai tutti i fmod solo dall'optimum answer set
    fmod_matches = re.findall(r'fmod\("([^"]+)",(\d)\)', optimum_set)
    
    # Estrai ecooutputname solo dall'optimum answer set
    ecooutputname_match = re.search(r'ecooutputname\("([^"]+)"\)', optimum_set)
    
    # Converti i match fmod in una stringa formattata con valori booleani
    changes = []
    for name, value in fmod_matches:
        # Inverti 1 e 0: '1' diventa 'false', '0' diventa 'true'
        boolean_value = 'false' if value == '1' else 'true'
        changes.append(Fore.GREEN + f"{name}" + Fore.WHITE + " becomes " + Fore.CYAN + f"{boolean_value}")
    
    # Unisci le modifiche
    change_made = ', '.join(changes)
    
    # Ottieni il risultato della modifica da ecooutputname
    result_of_change = ecooutputname_match.group(1) if ecooutputname_match else "Unknown"

    # Format the final output
    formatted_output = f"Change made: {change_made}\nResult of change: " + Fore.GREEN + f"{result_of_change}"
    
    return formatted_output



def extractemc(asp_result):
    # ASP gave suboptimal results along with optimal so had to use regex to isolate the optimal result
    optimum_match = re.search(r'{([^}]+)}\s*COST\s*\d+@\d\s*OPTIMUM', asp_result)
    
    if not optimum_match:
        return "No optimum result found."

    # Extract the content inside the optimal section's braces
    optimum_content = optimum_match.group(1)
    
    # Extract all fpresa
    matches = re.findall(r'fpresa\("([^"]+)",(\d)\)', optimum_content)

    #formatting result string to output
    replaced_values = [(name, "True" if value == '1' else "False") for name, value in matches]
    formatted_output = [Fore.GREEN + f"{name}" + Fore.WHITE + " is " + Fore.CYAN + f"{value}" for name, value in replaced_values]
    
    final_output = "\n".join(formatted_output)
    
    return final_output

# Stampa il titolo
print_title()

# Load dataset
data = load_breast_cancer()
X = data.data
y = data.target

# Decision tree creation
clf = DecisionTreeClassifier(criterion="gini", max_depth=None, random_state=0)
clf.fit(X, y)

# Generate ASP facts
nodes, edges, thresholds = tree_to_asp(clf, data.feature_names, data.target_names)
asp_facts = ["root(0)."] + nodes + edges

# User choice for input method
print_section("User Input")
user_choice = input(Fore.YELLOW + "Do you want to manually input data, choosing not to, will result in automatically generated data? (y/n): ").strip().lower()
print(Style.RESET_ALL)
input_strings, input_values = generate_inputs(thresholds, manual=(user_choice == 'y'))

asp_facts += input_strings

# Print used feature values
print_section("Feature Values")
for feature, value in input_values.items():
    print(Fore.BLUE + f"{feature}: {value:.3f}")
print(Style.RESET_ALL)

# Run ASP programs
asp_programs = ['inferenza.asp', 'eco.asp', 'emc.asp']

# Run first program, inferenza.asp
print_section("ASP Results:")
print(Fore.MAGENTA + f"\nRunning ASP program: {asp_programs[0]}")
result1 = run_dlv2_program(asp_programs[0], asp_facts)

output_value, output_name = extract_output(result1)
if output_value is not None and output_name is not None:
    asp_facts.append(f'output({output_value}).')
    print(Style.RESET_ALL)
    print(Fore.WHITE + f"your input gives result: " + Fore.RED + f"{output_name}")
else:
    print("Failed to extract result from the first program")
    exit(1)


# Run second program eco.asp
print(Fore.MAGENTA + f"\nRunning ASP program: {asp_programs[1]}")
result2 = run_dlv2_program(asp_programs[1], asp_facts)

eco = extracteco(result2)
if output_value is not None and output_name is not None:
    print(Style.RESET_ALL)
    print(eco)
else:
    print("Failed to extract result from the second program")
    exit(1)


# Run third program emc.asp
print(Fore.MAGENTA + f"\nRunning ASP program: {asp_programs[2]}")
result3 = run_dlv2_program(asp_programs[2], asp_facts)

nodie = extractemc(result3)
if output_value is not None and output_name is not None:
    print(Style.RESET_ALL)
    print(Fore.WHITE + f"explaination: " + Fore.RED + f"{nodie}")
else:
    print("Failed to extract result from the third program")
    exit(1)

os.remove("temp_input.asp")
# Set the decision tree for display
plt.figure(figsize=(20,10))
plot_tree(clf, feature_names=data.feature_names, class_names=data.target_names, filled=True, rounded=True)
plt.show()