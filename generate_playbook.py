#!/usr/bin/env python3

import os
import shutil
import sys
from jinja2 import Environment, FileSystemLoader

# Load the jinja environment
j2 = Environment(loader=FileSystemLoader(searchpath="./templates"))

# Get the directory path from the command-line argument
if len(sys.argv) != 2:
    print("Usage: ./generate_playbook.py <directory_path>")
    exit(1)

directory_path = sys.argv[1]

# Count the number of playbooks generated
shell_no_args = 0
shell_args = 0
python_no_args = 0
python_args = 0

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    # Check if the file is a shell script
    if filename.endswith((".sh", ".py")):
        # Determine script path
        script_path = os.path.join(directory_path, filename)

        # Decide which playbook template to use
        playbook_template = None
        with open(script_path, 'r') as f:
            script_contents = f.read()
            if ('$#' in script_contents or '$1' in script_contents) and filename.endswith(".sh"):
                playbook_template = j2.get_template("shell_playbook_with_args.j2")
                shell_args += 1
            elif filename.endswith(".sh"):
                playbook_template = j2.get_template("shell_playbook.j2")
                shell_no_args += 1
            elif ('optparse' in script_contents or 'argparse' in script_contents or 'argv' in script_contents) and filename.endswith(".py"):
                playbook_template = j2.get_template('python_playbook_with_args.j2')
                python_args += 1
            elif filename.endswith(".py"):
                playbook_template = j2.get_template("python_playbook.j2")
                python_no_args += 1
            else:
                continue

        # Create a subdirectory for the script
        script_directory = os.path.join(
            directory_path, filename.rsplit('.', 1)[0])
        os.makedirs(script_directory, exist_ok=True)

        # Move the script into its subdirectory
        shutil.move(script_path, script_directory)

        # Create an Ansible playbook that executes the script
        playbook_path = os.path.join(script_directory, "playbook.yml")
        with open(playbook_path, "w") as f:
            f.write(playbook_template.render(filename=filename))

print("Hi {}, happy automating!".format(
    os.getlogin(), ))
print()
print("Playbooks generated:")
print("Shell scripts converted (without args): {}".format(shell_no_args))
print("Shell scripts converted (with args): {}".format(shell_args))
print("Python scripts converted (without args): {}".format(python_no_args))
print("Python scripts converted (with args): {}".format(python_args))
print("Total playbooks generated: {}".format(
    shell_no_args + shell_args + python_no_args + python_args))
