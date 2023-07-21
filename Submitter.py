# Created 7/21/2023 for use in slurm queuing systems - SPIEDIE

import os
import subprocess
import fcntl
import glob
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='slurm_job_submission.log', level=logging.INFO, 
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Define the threshold
threshold = 5

# Define the path to the directory containing the slurm scripts
directory = '/path/to/your/directory'

while True:
    # Find the most recent file that matches the pattern
    list_of_files = glob.glob(f'{directory}/pending_job_list_*.txt')
    slurm_scripts_file = max(list_of_files, key=os.path.getctime)

    # Get the current number of jobs in the queue
    output = subprocess.check_output('squeue -u $USER', shell=True).decode('utf-8')
    lines = output.strip().split('\n')[1:]  # Exclude the header line
    # Filter to get only pending jobs
    pending_jobs = [line for line in lines if "PD" in line.split()]
    num_jobs = len(pending_jobs)

    # Log the number of pending jobs
    logging.info(f'Number of pending jobs: {num_jobs}')

    # Read the slurm scripts from the file
    with open(slurm_scripts_file, 'r') as f:
        slurm_scripts = [line.strip() for line in f]

    # Create a new file to write the remaining slurm scripts
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    new_file_name = f'{directory}/pending_job_list_{date_time}.txt'

    with open(new_file_name, 'w') as f:
        # Lock the file
        fcntl.flock(f, fcntl.LOCK_EX)
        
        # If the number of jobs is less than the threshold, submit more jobs
        if num_jobs < threshold:
            num_jobs_to_submit = threshold - num_jobs
            for _ in range(num_jobs_to_submit):
                if slurm_scripts:  # Check if there are still scripts left
                    slurm_script = slurm_scripts.pop(0)  # Take the first script from the list
                    # Using subprocess.run instead of os.system
                    result = subprocess.run(['sbatch', slurm_script], stdout=subprocess.PIPE)
                    # Log the job submission
                    logging.info(f'Submitted job: {slurm_script}, output: {result.stdout.decode()}')
                    # Check if the job submission was successful
                    if result.returncode != 0:
                        logging.error(f"Job submission failed for {slurm_script}")
                        break
                else:
                    break  # No more scripts left, break the loop

        # Write the remaining slurm scripts to the new file
        for script in slurm_scripts:
            f.write(script + '\n')

        # Unlock the file
        fcntl.flock(f, fcntl.LOCK_UN)
    
    # Pause for 10 minutes
    time.sleep(600)
