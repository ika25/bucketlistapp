
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

DBCONFIG = {
  "DRIVER": "mysql",
  "USER": "<DBUSER>",
  "PASSWORD": "<DBPASSWORD>",
  "DBNAME": "<DBNAME>",
  "HOST": "localhost"
# 'PORT' is also supported
}

SESSION_SECRET = 'A SECRET KEY (recommended to have at least 24 bytes)'

VERBOSE = False

API_PREFIX = '/api'

STATIC_URL_PATH = ''

STATIC_PATH = dir_path + '/static'

UPLOAD_PATH = STATIC_PATH + '/uploads'

UPLOAD_URL = STATIC_URL_PATH + '/uploads'

SUPPORTED_UPLOAD_IMAGES = [ '.jpg', '.jpeg', '.png', '.gif' ]

PRODUCTION = False
