# Bucket List Web App

A central user based todo list app. It's made with help of
Flask, Mysql, SQLAlchemy, AngularJS, bootstrap, etc.

## Dependencies

Primary programs needed to get started.

1. `python 2.7`
2. `npm`
3. Python's `virtualenv`
4. Development Tools & compilers  (`yum groupinstall 'Development Tools' && yum install gcc g++ make autoconf libtool`)
5. `mysql-server` + headers  (`yum install mariadb-devel`)
6. `libffi` + headers  (`yum install libffi-devel`)

### Web server

1. `Flask`
2. `Flask-Testing`
3. `sqlalchemy`
4. `bcrypt`
5. `MySQL-python`

### Client Side

1. `bower`
2. `angular 1.5.x`
3. `angular-resource 1.5.x`
4. `angular-route 1.5.x`
5. `bootstrap 3.3.x`
6. `jquery 2.2.x`
7. `font-awesome 4.7`
8. `jansy-bootstrap 3.1`

## Installation

List of actions to setup.

1. Install dependencies
2. Initiate virtualenv on package
3. Install python package dependencies
4. npm Install dependencies
5. Configure `config.py` file with help of `config-sample.py`

Bellow is detailed install instructions.
Assuming `python 2.7` and `npm` is installed.

1. $ `cd to-project-directory`
1. $ `sudo pip install virtualenv`
2. $ `virtualenv -p /usr/bin/python venv`

Or replace `/usr/bin/python` with the path of python2.7 binary.
This command will create a virutal environment in `venv` directory.

3. $ `. venv/bin/activate`

Notice bash indicates it's in virtual environment `(venv)`

4. $ `python setup.py install`

Installs all web server dependencies in `venv`.
Make sure see success message like `Finished processing dependencies`.

5. $ `npm install`

This command should install all required client side dependencies in `static/bower_components`.

6. Write `config.py` file in projects directory,
   You can copy `config-sample.py` to `config.py`.
   And modify `DBCONFIG` and `SESSION_SECRET`.

You can generate a secret key with python command prompt like this.

```
import os
os.urandom(24)
```

7.  $ `export FLASK_APP=bucketlistapp.py`

Set Flask app envrinoment variable

8. $ `flask run`

Starts the server at port 5000. If you see no error, Web app is running there.

http://localhost:5000/
