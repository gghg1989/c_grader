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
    def __init__(self, submissions_dir, assignment_number, commands,numba_accel=True):
        self.path = submissions_dir
        self.reults = None
        self.assignment_number = assignment_number
        self.commands = commands
        self.numba_accel=numba_accel
    
    def extract_all(self,extracted_path='extracted'):
        self.extracted_path=extracted_path
        students = []
        for file in glob.glob(self.path+'/*.zip'):
            name = file.replace(self.path+'/','').split('_')[-1].split('.')[0]
            # print(file)
            # continue
            with ZipFile(file, 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall(f'../A1/{extracted_path}/{name}')
            
            print([x[0] for x in os.walk(f'../A1/{extracted_path}/{name}')])
        # self.results = pd.DataFrame(students,columns=['students']).sort_values('students')
        # return self.results
        return True

    def file_compare(self, no_touch_files):
        ready_path = '../A1/ready/'
        submission_list = os.listdir(path=ready_path)
        # Remove original provided files
        submission_list.remove('A1_origin')

        for submission in submission_list:
            for no_touch_file in no_touch_files:
                origin_path = f'{ready_path}A1_origin/{no_touch_file}'
                submission_path = f'{ready_path}{submission}/{no_touch_file}'
                print(f'{submission}:{no_touch_file}:')
                print(filecmp.cmp(origin_path, submission_path))

def main():
    SUBMISSIONS_DIR = '../A1/submissions/'

    COMMANDS = {
        1:[]
    }
    
    grader = Grader(
        SUBMISSIONS_DIR,
        assignment_number=1,
        commands=COMMANDS[1]
    )
    # Extract all submissions from zip file.
    df = grader.extract_all()

    # Compare no_touch files with the submitted files.
    # grader.file_compare(['Die.java', 'DiceOddsTester.java'])

if __name__ == '__main__':
    main()