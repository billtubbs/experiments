"""Python script to automate the execution of shell scripts

Put jobdispatcher.py in a new sub-directory on a server where you want
to execute the shell scripts.  Launch it and let it run in the background.

It creates a new directory in the parent directory from which it was
launched with a name like 'gpu0' (the number is determined by the --gpu
argument).

It then creates three subdirectories in that directory:
- queue
- completed
- failed

Then it waits for shell scripts (extension .sh) to appear in the 'queue'
directory. It checks every second and when it sees one or more they are
added to a queue and each job is executed one after the other.

To start running jobs, copy script files (e.g. my_script.sh) to the
'queue' directory.

First jobdispatcher moves the script to the parent directory and then
executes it with subprocess.run.  When complete, it is moved to the
'complete' directory.

Log output is written to logfile.txt.
"""

import subprocess
import datetime
import time
import os
import shutil
from collections import deque
import logging
import argparse

# Parse input arguments with argparse
parser = argparse.ArgumentParser("Python script to automate the execution of "
                                 "shell scripts on GPUs.")
parser.add_argument('--gpu', type=int, required=True, metavar='GPU',
                    help='GPU id')
parser.add_argument('--dir', type=str, default='../', metavar='DIR',
                    help="Directory name for queues (default: '../')")
parser.add_argument('--wait', type=int, default=1, metavar='SEC',
                    help="Wait time (seconds) between checks for new items "
                    "in queue.")
args = parser.parse_args()


# Create subdirectories
if args.dir:
    base = os.path.join(".", args.dir)
else:
    base = '../'
base = os.path.join(base, "gpu" + str(args.gpu))

queue_path = os.path.join(base, 'queue')
execution_path = './'
completed_jobs_path = os.path.join(base, 'completed')
failed_jobs_path = os.path.join(base, 'failed')
logfile_path = base

for directory in [queue_path, execution_path, completed_jobs_path,
                  failed_jobs_path, logfile_path]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Log messages go to log file
logging.basicConfig(filename=os.path.join(logfile_path, 'logfile.txt'),
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("------------ Job Dispatcher Started ------------")

def get_script_filenames(path=None):
    """Return a list containing the file names of any shell scripts
    in the specified directory (i.e. filenames ending in '.sh').

    If path is None, uses path='.'.  For other details on path, see
    os.listdir() documentation.
    """

    return [fname for fname in os.listdir(path) if fname.endswith('.sh')]


job_queue = deque()
time_now = datetime.datetime.now()

while True:

    files_now_in_queue = get_script_filenames(queue_path)

    if not files_now_in_queue:
        logging.info("Job queue empty. Waiting...")

        while not files_now_in_queue:
            time.sleep(args.wait)
            files_now_in_queue = get_script_filenames(queue_path)

    # Check for new script files added to queue
    any_new_jobs = sorted(list(set(get_script_filenames(queue_path)) -
                          set(job_queue)))
    if any_new_jobs:
        job_queue.extend(any_new_jobs)
        logging.info("%d new jobs added to queue %s", len(any_new_jobs),
                     any_new_jobs.__repr__())

    # Check if any script files removed from queue
    any_jobs_removed = set(job_queue) - set(files_now_in_queue)
    if any_jobs_removed:
        logging.info("Detected %d jobs removed from queue",
                     len(any_jobs_removed))
        for job in any_jobs_removed:
            job_queue.remove(job)

    current_job = job_queue.popleft()

    shutil.move(os.path.join(queue_path, current_job),
                os.path.join(execution_path, current_job))

    # Execute next script in queue
    logging.info("Running job %s...", current_job)
    destination_path = completed_jobs_path

    env_vars = {'CUDA_VISIBLE_DEVICES': str(args.gpu)}
    os.environ.update(env_vars)
    try:
        sb = subprocess.run([os.path.join(execution_path, current_job)])
    except PermissionError as err:
        logging.warning("PermissionError: {}".format(err))
        destination_path = failed_jobs_path
    else:
        if sb.returncode == 0:
            logging.info("%s returned %d", current_job, sb.returncode)
        else:
            logging.warning("%s returned %d", current_job, sb.returncode)
            destination_path = failed_jobs_path

    try:
        shutil.move(os.path.join(execution_path, current_job),
                    os.path.join(destination_path, current_job))
    except FileNotFoundError as err:
        logging.warning("FileNotFoundError: {}".format(err))
