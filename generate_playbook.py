#!/usr/bin/env python3

import os
import shutil
import sys
from jinja2 import Template, Environment

# Load the jinja environment
j2 = Environment()

# Get the directory path from the command-line argument
if len(sys.argv) != 2:
    print("Usage: ./generate_playbook.py <directory_path>")
    exit(1)

directory_path = sys.argv[1]

# Count the number of playbooks generated
shell = 0
python = 0

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    # Check if the file is a shell script
    if filename.endswith((".sh", ".py")):
        # Create a subdirectory for the script
        script_directory = os.path.join(
            directory_path, filename.rsplit('.', 1)[0])
        os.makedirs(script_directory, exist_ok=True)

        # Move the script into its subdirectory
        script_path = os.path.join(directory_path, filename)
        shutil.move(script_path, script_directory)

        # Decide which playbook template to use
        playbook_template = None
        with open(script_path, 'r') as f:
            script_contents = f.read()
            if ('?#' in script_contents or '?1' in script_contents) and filename.endswith(".sh"):
                playbook_template = j2.get_template("sh_playbook_with_args.j2")
                shell += 1
            elif filename.endswith(".sh"):
                playbook_template = j2.get_template("sh_playbook.j2")
                shell += 1
            elif filename.endswith(".py"):
                playbook_template = j2.get_template("py_playbook.j2")
                python += 1

        # Create an Ansible playbook that executes the script
        playbook_path = os.path.join(script_directory, "playbook.yml")
        with open(playbook_path, "w") as f:
            f.write(playbook_template.render(filename=filename))

print("Hi {}, you've generated {} playbooks. Happy automating!".format(
    os.getlogin(), shell + python))
print()
print("Shell scripts converted: {}".format(shell))
print("Python scripts converted: {}".format(python))
