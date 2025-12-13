# -*- coding: utf-8 -*-
import os
import subprocess

class RunRepositoryDeadline(object):
    def __init__(self, deadlinebin="Z:/netrende/Thinkbox/Deadline10/bin",repository="Z:/netrende/ProgramData/Thinkbox/Deadline10"):
        self._deadlinebin = deadlinebin
        self._repository = repository

    def submit_deadline(self, job_info, plugin_info,job_info_file=None,plugin_info_file=None):
        """
        Submits a job to Deadline.
        :param job_info: Dictionary containing job information
        :param plugin_info: Dictionary containing plugin-specific information
        :return: Tuple (output, error) from the Deadline command execution
        """
        return self.__submit_deadline(job_info, plugin_info,job_info_file,plugin_info_file)

    def __submit_deadline(self, job_info, plugin_info,job_info_file=None,plugin_info_file=None):
        if job_info_file==None:
            job_info_file = "job_info.job"
        if plugin_info_file==None:
            plugin_info_file = "plugin_info.job"


        # Create job info file
        with open(job_info_file, 'w') as f:
            for key, value in job_info.items():


                f.write("{}={}\n".format(key, value))

        # Create plugin info file
        with open(plugin_info_file, 'w') as f:
            for key, value in plugin_info.items():
                print(key, value)
                f.write("{}={}\n".format(key, value))

        deadline_command = os.path.join(self._deadlinebin, "deadlinecommand.exe")
        deadline_command='{} -RunCommandForRepository {}'.format(deadline_command,self._repository)
        command = [deadline_command, job_info_file, plugin_info_file]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        # Decode output and error
        out = out.decode('utf-8')
        err = err.decode('utf-8')

        # print("Output:\n", out)
        # print("Error:\n", err)

        # Clean up temporary files
        os.remove(job_info_file)
        os.remove(plugin_info_file)

        if "Error" in out or err:
            print("Failed to submit job to Deadline.")
            return False, err
        return True, out

if __name__ == '__main__':
    # Corrected job info with Plugin specified
    job_info = {
        "Plugin": "MarkerCleanUp",
        "Name": "My Test Job",
        "Comment": "Testing Deadline Submission",
        "Department": "Development",
        "Pool": "shogun",
        "Group": "shogun",
        "Priority": "50"

    }

    # Plugin info
    plugin_info = {
        "FileType": "mcp",
        "FilePath": "E:/test/Session/click_S0556_01_V01.mcp",
        "SavePath": "E:/test/batch_save"
    }

    # Submit job
    deadline_runner = RunDeadline()
    success, message = deadline_runner.submit_deadline(job_info, plugin_info)

    if success:
        print("Job submitted successfully!")
    else:
        print("Job submission failed: {}".format(message))
