# C Grader

An automatic c program grader for system progrogramming class.

> Basing on Victor Potapenko's previous work.

## Pre-request Environment

### Environment Requirement

python3.7 or higher version is required.

### Setup Environment
1. Install virtual environment
```
pip install virtualenv
```

2. Create venv directory
* For Linux/Mac
```
python3 -m venv .venv
```
* For Windows
```
virtualenv env
```

3. Activate virtual environment
* For Linux/Mac
```
source .venv/bin/activate
```
* For Windows
```
.\.venv\Scripts\activate
```

4. Install packages from requirements.txt
```
pip install -r requirements.txt
```

5. Deactivate virtual environment
```
deactivate
```
## Running via Docker

Docker not set up yet. Use grader.py with submission.zip from canvas extracted into project root or modify SUBMISSIONS_PATH in grader.py\n
docker build -t grader .\n
docker run -it -v /home/victor/Projects/grader:/home/grader --rm --name grader grader\n
