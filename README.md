# Automatic-Job-Submitter

This automatic job scheduler can be used in HPC clusters that are limited in resources so that you don't look like an ass-hat to other users who submit thousands of jobs at once to the queue like me!

This script will run until canceled. It will check for the current queue, extract the number of slum jobs in PD (pending state), and check if it is lower than a preset threshold. 
If more jobs can be submitted, it will create a new list of pending jobs and save it to a new file with an updated name (date and time). Then it will sleep for a prespecified amount of time till it repeats. 

Suggestions and improvements are welcome!
