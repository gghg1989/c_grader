import tarfile
import glob
import pandas as pd
import subprocess
import shutil
import os
import shlex
import math, operator, functools

from zipfile import ZipFile

import filecmp

class Grader:
    def __init__(self, workspace, assignment_name, commands,numba_accel=True):
        self.path = f'{workspace}{assignment_name}'
        self.reults = None
        self.assignment_name = assignment_name
        self.commands = commands
        self.numba_accel=numba_accel
    
    def extract_all(self,extracted_path='extracted'):
        students = []
        for file in glob.glob(self.path+'/submissions/*.zip'):
            name = file.replace(self.path+'/','').split('_')[-1].split('.')[0]
            name = name.split('-')[0]
            # print(file)
            # continue
            with ZipFile(file, 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall(f'{self.path}/{extracted_path}/{name}')
            
            print([x[0] for x in os.walk(f'{self.path}/{extracted_path}/{name}')])
        # self.results = pd.DataFrame(students,columns=['students']).sort_values('students')
        # return self.results
        return True
    
    def detect_extra_dir(self):
        extracted_dir = f'{self.path}/extracted/'
        submission_list = os.listdir(path=extracted_dir)
        for submission in submission_list:
            extracted_path = extracted_dir+submission
            submission_content = os.listdir(path=extracted_path)
            if 'Makefile' in submission_content:
                has_extra_dir = False
            else:
                has_extra_dir = True

            if has_extra_dir:
                print(f'{submission}:{submission_content} = {has_extra_dir}')
    
    def detect_sys_lint(self):
        ready_dir = f'{self.path}/ready/'
        submission_list = os.listdir(path=ready_dir)
        for submission in submission_list:
            ready_path = ready_dir+submission
            submission_content = os.listdir(path=ready_path)
            if '__MACOSX' in submission_content or '.DS_Store' in submission_content:
                has_sys_lint = True
            else:
                has_sys_lint = False

            if has_sys_lint:
                print(f'{submission}:{submission_content} has system lint.')

    def file_compare(self, no_touch_files):
        ready_path = f'../{self.assignment_name}/ready/'
        submission_list = os.listdir(path=ready_path)
        # Remove original provided files
        submission_list.remove(f'{self.assignment_name}_origin')

        for submission in submission_list:
            for no_touch_file in no_touch_files:
                origin_path = f'{ready_path}{self.assignment_name}_origin/{no_touch_file}'
                submission_path = f'{ready_path}{submission}/{no_touch_file}'
                print(f'{submission}:{no_touch_file}:')
                print(filecmp.cmp(origin_path, submission_path))
    
    def _make(self,name):
        path = '/'+self.path+'/'+self.extracted_path+'/'+name+'/hw{}/'.format(self.hw_number)
        process = subprocess.Popen(['make','-C', path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stderr+stdout

def main():
    workspace = '../../2020FALL/COP4338_UHB/'

    COMMANDS = {
        1:[]
    }
    
    grader = Grader(
        workspace,
        assignment_name='L2',
        commands=COMMANDS[1]
    )
    # Extract all submissions from zip file.
    # df = grader.extract_all()

    # grader.detect_extra_dir()
    grader.detect_sys_lint()

    # Compare no_touch files with the submitted files.
    # grader.file_compare(['Die.java', 'DiceOddsTester.java'])

if __name__ == '__main__':
    main()