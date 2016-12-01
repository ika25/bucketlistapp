from config import DBCONFIG
from service.models import metadata
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine

dbengine = create_engine(URL(DBCONFIG['DRIVER'], DBCONFIG['USER'], DBCONFIG['PASSWORD'], DBCONFIG['HOST'], DBCONFIG.get('PORT'), DBCONFIG['DBNAME']), echo=True)

metadata.create_all(dbengine)
