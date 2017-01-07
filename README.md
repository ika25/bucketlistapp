# Bucket List Web App

A central user based todo list app. It's made with help of
Flask, Mysql, SQLAlchemy, AngularJS, bootstrap, this app has login page where you can login to you personal page,
ones you login you have dashboard,manage,new and log out table.

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

- $ `cd to-project-directory`
- $ `sudo pip install virtualenv`
- $ `virtualenv -p /usr/bin/python venv`

Or replace `/usr/bin/python` with the path of python2.7 binary.
This command will create a virutal environment in `venv` directory.

- $ `. venv/bin/activate`

Notice bash indicates it's in virtual environment `(venv)`

- $ `python setup.py install`

Installs all web server dependencies in `venv`.
Make sure see success message like `Finished processing dependencies`.

- $ `npm install`

This command should install all required client side dependencies in `static/bower_components`.

- Write `config.py` file in projects directory,
   You can copy `config-sample.py` to `config.py`.
   And modify `DBCONFIG` and `SESSION_SECRET`.

You can generate a secret key with python command prompt like this.

```
import os
os.urandom(24)
```

- $ `python initsql.py`

For creating database schema.

- $ `export FLASK_APP=bucketlistapp.py`

Set Flask app envrinoment variable

- $ `flask run`

Starts the server at port 5000. If you see no error, Web app is running there.

http://localhost:5000/

REFERENCE

https://www.youtube.com/watch?v=M1IVwFAH9Wo
https://www.youtube.com/watch?v=mr90d7fp3SE&t=890s
https://www.fullstackpython.com/flask.html
https://realpython.com/blog/python/python-web-applications-with-flask-part-i/
