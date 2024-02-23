import re
import sys

def numerical_sort_key(s):
    """A sorting key function that sorts strings with numerical values correctly."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def sort_file(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Ensure each line ends with a newline character
    lines = [line if line.endswith('\n') else line + '\n' for line in lines]

    # Sort lines with custom sorting key
    lines.sort(key=numerical_sort_key)

    # Write sorted lines to output file
    with open(output_file, 'w') as file:
        file.writelines(lines)

if len(sys.argv) != 3:
    print("Usage: python sort_file.py input.txt output.txt")
    sys.exit(1)

input_file = sys.argv[1] # (str) nom du fichier à trier
output_file = sys.argv[2] # (str) nom du fichier de sortie

sort_file(input_file, output_file)
