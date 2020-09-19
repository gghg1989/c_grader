#%%
import tarfile
import glob
import pandas as pd
import subprocess
import shutil
import os
import shlex
from PIL import Image
import math, operator, functools

#%%
class Grader:
    def __init__(self, submissions_dir, example_path,expected_files,hw_number,commands,numba_accel=True):
        self.path = submissions_dir
        self.example = example_path
        self.reults = None
        self.hw_number = hw_number
        self.expected_files = expected_files
        self.commands = commands
        self.numba_accel=numba_accel
    def extract_all(self,extracted_path='extracted'):
        self.extracted_path=extracted_path
        students = []
        for file in glob.glob(self.path+'/*.tar.gz'):
            name = file.replace(self.path+'/','').split('_')[0]
            with tarfile.open(file) as tf:
                tf.extractall(self.path+'/'+self.extracted_path+'/'+name)
            self._fix_hw4dir_case(name)
            students.append(name)
        self.results = pd.DataFrame(students,columns=['students']).sort_values('students')
        return self.results
    def _fix_hw4dir_case(self,name):
        try:
            path_to_fix = self.path+'/'+self.extracted_path+'/'+name+'/Hw4'
            path = self.path+'/'+self.extracted_path+'/'+name+'/hw4'
            os.rename(path_to_fix,path)
            return
        except FileNotFoundError:
            return
        except OSError:
            return
    def _pre_clean(self,name):
        extra_files = ''
        path=self.path+'/'+self.extracted_path+'/'+name+'/hw{}/'.format(self.hw_number)
        for file in os.listdir(path):
            if file not in self.expected_files:
                try:
                    extra_files+=os.fsencode(file).decode('utf-8') +' | '
                except UnicodeDecodeError:
                    extra_files+='UnicodeDecodeError' + ' | '
                try:
                    os.remove(path+file)
                except:
                    shutil.rmtree(path+file)
        return extra_files
    def _make(self,name):
        path = '/'+self.path+'/'+self.extracted_path+'/'+name+'/hw{}/'.format(self.hw_number)
        process = subprocess.Popen(['make','-C', path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stderr+stdout
    def _run_3(self,name):
        path = './'+self.path+'/'+self.extracted_path+'/'+name+'/hw{}/hw{}'.format(self.hw_number)
        commands = self.commands
        try:
            proc = subprocess.Popen(
                [path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,bufsize=0
            )
            try:
                out = proc.communicate(
                    input='\n'.join(commands),
                    timeout=3)[0]
                out = out.split('\n')
            except subprocess.TimeoutExpired as e:
                out = e
        except FileNotFoundError as e:
            out = e
        return out
    def _run_4(self,name):
        try:
            os.chdir(self.path+'/'+self.extracted_path+'/'+name+'/hw4/')
            shutil.copyfile(self.example,'example.bmp')
        except Exception as e:
            return e            
        outputs = []
        for command in self.commands:
            try:
                proc = subprocess.Popen(shlex.split(command))
                proc.communicate(timeout=15)
                outputs.append(proc.returncode)                    
            except UnicodeDecodeError as e:
                outputs.append(e)
            except subprocess.TimeoutExpired as e:
                outputs.append(e)
            except FileNotFoundError as e:
                outputs.append(e)
            finally:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                except UnboundLocalError:
                    pass
        return outputs   
    def _validate_3(self,name):
        path = './'+self.path+'/'+self.extracted_path+'/'+name+'/hw3/hw3'
        list_states = [['bye','good afternoon','good morning','hello'],['hello','good morning','good afternoon'],['good morning','hello']]
        output = self.results.set_index('students').loc[name]['output']
        lsi = 0
        state = list_states[lsi]
        try:
            for i in range(0,len(output)):
                out_win = output[i:i+len(state)]
                valid_n = 0
                for j in range(0,len(state)):
                    valid_n = valid_n + 1 if state[j] in out_win[j] else valid_n
                    if valid_n == len(state):
                        lsi+=1
                        if lsi == len(list_states):
                            return True
                        state = list_states[lsi]
                    else:
                        continue
        except:
            return False
        return False
    def _validate_4(self,name):
        path = self.path+'/'+self.extracted_path+'/'+name+'/hw4/'
        images = {
            'scale':'example_s2.bmp',
            'rotate':'example_r.bmp',
            'crotate':'example_c.bmp',
            'flip':'example_f.bmp',
            'vflip':'example_v.bmp',
            'pipe':'example_s4cv.bmp',
        }
        results = {}
        for k,v in images.items():
            try:
                example = Image.open(path+'example.bmp')
                target = None
                if k == 'scale':
                    w, h = example.size
                    target = example.resize(((w*2,h*2)))
                if k == 'rotate':
                    target = example.transpose(Image.ROTATE_270)
                if k == 'crotate':
                    target = example.transpose(Image.ROTATE_90)
                if k == 'flip':
                    target = example.transpose(Image.FLIP_LEFT_RIGHT)
                if k == 'vflip':
                    target = example.transpose(Image.FLIP_TOP_BOTTOM)
                if k == 'pipe':
                    w, h = example.size
                    target = example.resize(((w*4,h*4)))
                    target = target.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
                result = Image.open(path+v)
                rms = math.sqrt(
                        functools.reduce(
                            operator.add,map(
                                lambda a,b: (a-b)**2, target.histogram(), result.histogram()))/len(target.histogram()))
                results[k] = True if rms == 0 else False
            except FileNotFoundError:
                results[k] = 'FileNotFoundError'
            except AttributeError:
                results[k] = 'AttributeError'
            except OSError:
                results[k] = 'OSError'
            except ValueError:
                results[k] = 'ValueError'
        return results
    def _validate(self,name):
        if self.hw_number==3:
            return self._validate_3(name)
        elif self.hw_number==4:
            return self._validate_4(name)
    def _clean(self,name):
        path = '/'+self.path+'/'+self.extracted_path+'/'+name+'/hw{}/'.format(self.hw_number)
        process = subprocess.Popen(['make','clean','-C', path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return (stderr+stdout)
    def _check_clean(self,name):
        extra_files = ''
        path=self.path+'/'+self.extracted_path+'/'+name+'/hw{}/'.format(self.hw_number)
        for file in os.listdir(path):
            if file not in self.expected_files:
                try:
                    extra_files+=os.fsencode(file).decode('utf-8') +' | '
                except UnicodeDecodeError:
                    extra_files+='UnicodeDecodeError' + ' | '                    
                try:
                    os.remove(path+file)
                except:
                    shutil.rmtree(path+file)
        return extra_files if extra_files!='' else True
    def pre_clean_all(self):
        self.results['pre_clean'] = self.results['students'].apply(self._pre_clean)
        return self.results
    def run_all(self):
        if self.hw_number==3:
            self.results['students'].apply(self._run_3)
        elif self.hw_number==4:
            self.results['students'].apply(self._run_4)
        return self.results
    def validate_all(self):
        self.results['output_is_valid'] = self.results['students'].apply(self._validate)
        self.results['scale'] = self.results['output_is_valid'].apply(lambda x: x['scale'])
        self.results['rotate'] = self.results['output_is_valid'].apply(lambda x: x['rotate'])
        self.results['crotate'] = self.results['output_is_valid'].apply(lambda x: x['crotate'])
        self.results['flip'] = self.results['output_is_valid'].apply(lambda x: x['flip'])
        self.results['vflip'] = self.results['output_is_valid'].apply(lambda x: x['vflip'])
        self.results['pipe'] = self.results['output_is_valid'].apply(lambda x: x['pipe'])
        return self.results
    def make_all(self):
        self.results['make'] = self.results['students'].apply(self._make)
        return self.results
    def clean_all(self):
        self.results['clean'] = self.results['students'].apply(self._clean)
        return self.results
    def check_clean_all(self):
        self.results['check_clean'] = self.results['students'].apply(self._check_clean)
        return self.results
    def remove_all(self):
        shutil.rmtree(self.path+'/'+self.extracted_path)
        return self.results

#%%

def main():
    SUBMISSIONS_DIR = '../'
    # EXAMPLE_PATH = '/home/admin/Downloads/hw4/submissions/grader/example.bmp'
    HW = [1]
    EXPECTED_FILES = {
        4:['main.c','main.o','bmplib.o','bmplib.h','bmplib.c','Makefile','example.bmp','cybertruck.bmp',
           'example_s2.bmp','example_r.bmp','example_c.bmp','example_f.bmp','example_v.bmp','example_s4cv.bmp','result.bmp',
           'cybertruck_s2.bmp','cybertruck_r.bmp','cybertruck_c.bmp','cybertruck_f.bmp','cybertruck_v.bmp','cybertruck_s4cv.bmp',]
    }
    COMMANDS = {
        3:[
            'list',
            'insert hello',
            'insert good morning',
            'insert bye',
            'insert good afternoon',
            'list',
            'delete bye',
            'list 1',
            'delete whatever',
            'delete good afternoon',
            'list',
            'exit'
        ],
        4:[
            './bmptool -s 2 -o example_s2.bmp example.bmp',
            './bmptool -r -o example_r.bmp example.bmp',
            './bmptool -c -o example_c.bmp example.bmp',
            './bmptool -f -o example_f.bmp example.bmp',
            './bmptool -v -o example_v.bmp example.bmp',
            './bmptool -s 4  example.bmp | ./bmptool -c | ./bmptool -v -o example_s4cv.bmp'
        ]
    }
    grader = Grader(
        SUBMISSIONS_DIR,
        EXAMPLE_PATH,
        expected_files=EXPECTED_FILES[4],
        hw_number=4,
        commands=COMMANDS[4]
    )
    df = grader.extract_all()
    df = grader.pre_clean_all()
    df = grader.make_all()
    df = grader.run_all()
    df = grader.validate_all()
    df = grader.clean_all()
    df = grader.check_clean_all()
    df.to_csv(SUBMISSIONS_DIR+'/extracted/grader_output.csv')
#     grader.remove_all()
    return df

#%%

if __name__ == '__main__':
    main()

#%%