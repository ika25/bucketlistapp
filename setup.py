#!/usr/bin/env /usr/bin/python

from setuptools import setup

setup(name='bucketlistapp',
      version='0.0.1',
      description='The bucket list web app made with flask and angularjs',
      url='',
      author='',
      author_email='',
      license='GPL-2',
      install_requires=[
          'Flask-Testing', 'Flask', 'sqlalchemy', 'bcrypt', 'MySQL-python'
      ],
      zip_safe=False)
