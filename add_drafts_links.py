import logging
from datetime import datetime
from pytodoist import todoist
from credentials import USER, PASS
from pynput import keyboard
import os
import sys
import re
import threading
import urllib

#Setup loggging
FORMAT = '%(asctime)-15s, %(levelname)s: %(message)s'
logging.basicConfig(filename="triage.log", level=logging.INFO, format=FORMAT)
l = logging.getLogger(__name__)

assert sys.argv[1] is not None

print("Starting script")
#Setup pytodoist.todoist
user = todoist.login(USER, PASS)
print("Finished setting up todoist login")

##########################
# Get tasks and projects #
##########################

tasks = user.get_project(sys.argv[1]).get_tasks()

#####################
# Utility functions #
#####################

def task_to_project(task, project):
    task.move(project)
    l.info("{} received '{}'".format(project.name, task.content))

def spawn_process(function, args):
    """
        Spawns a new process.
        Takes 2 args:
            function to run
            args [tuple]
    """
    threading.Thread(target=function, args=args).start()
    l.info("Spawning process with function: {}\n args: {}".format(function, args))

####################
# Script functions #
####################

def process_prefixed(task):
    l.info("Processing as prefixed")
    project = None

    if task.content[0] == "F": #If flashcard
        project = inbox_flashcards
    elif task.content[0] == "I": #If process improvement
        project = inbox_process_improvements
    elif task.content[0] == "C": #If consideration
        project = inbox_considerations

    task.content = task.content[3:]
    task.update()
    spawn_process(task_to_project, (task, project))

def process_suffixed(task):
    l.info("Processing as suffixed")
    project = None

    if task.content[-2:-1] == "I": #If process improvement
        project = inbox_process_improvements
        task.content = task.content[0:-2]
    elif task.content[-1:] == "?": #If consideration
        project = inbox_considerations
        task.content = task.content[0:-1]

    task.update()
    spawn_process(task_to_project, (task, project))

i = 0

for task in tasks:
    if "Drafts" not in task.content:
        base = "drafts5://x-callback-url/create?text="
        suffix = urllib.parse.quote(task.content)
        task.content = task.content + " [[Open in Drafts]]({}{})".format(base, suffix)
        task.update()
    i += 1
