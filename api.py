import hug
import pymysql
import pymysql.cursors
from settings import *

def get_db_connection():
  return pymysql.connect(
    host=HOST,
    user=USER,
    password=PW,
    db=DB,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
  )

@hug.response_middleware()
def CORS(request, response, resource):
  response.set_header('Access-Control-Allow-Origin', '*')
  response.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
  response.set_header(
      'Access-Control-Allow-Headers',
      'Authorization,Keep-Alive,User-Agent,'
      'If-Modified-Since,Cache-Control,Content-Type'
  )
  response.set_header(
      'Access-Control-Expose-Headers',
      'Authorization,Keep-Alive,User-Agent,'
      'If-Modified-Since,Cache-Control,Content-Type'
  )
  if request.method == 'OPTIONS':
      response.set_header('Access-Control-Max-Age', 1728000)
      response.set_header('Content-Type', 'text/plain charset=UTF-8')
      response.set_header('Content-Length', 0)
      response.status_code = hug.HTTP_204

@hug.static('/static')
def static():
  return('public/static',)

@hug.get('/', output=hug.output_format.html)
def index():
  with open('public/index.html') as f:
    contents = f.read()
  f.close()
  return contents

@hug.get('/cattle/inventory/national')
def cattle_inventory_national():
  connection = get_db_connection()
  with connection.cursor() as cursor:
    sql = """
      SELECT
        year,
        value,
        CONCAT(year, '-01-01T00:00:00-00:00') AS timestamp
      FROM
        usda
      WHERE
        program = 'SURVEY'
        AND period = 'FIRST OF JAN'
        AND geo_level = 'NATIONAL'
        AND commodity = 'CATTLE'
        AND data_item = 'CATTLE, INCL CALVES - INVENTORY'
        AND domain = 'TOTAL'
      ORDER BY
        year
    """
    cursor.execute(sql)
    data = cursor.fetchall()
  connection.close()
  return data

@hug.get('/cattle/inventory/state')
def cattle_inventory_state():
  connection = get_db_connection()
  with connection.cursor() as cursor:
    sql = """
      SELECT
        CONCAT(UCASE(LEFT(state, 1)), LCASE(SUBSTRING(state, 2))) AS state,
        year,
        value,
        CONCAT(year, '-01-01T00:00:00-00:00') AS timestamp
      FROM
        usda
      WHERE
        program = 'SURVEY'
        AND period = 'FIRST OF JAN'
        AND geo_level = 'STATE'
        AND commodity = 'CATTLE'
        AND data_item = 'CATTLE, INCL CALVES - INVENTORY'
        AND domain = 'TOTAL'
      ORDER BY
        year,
        state
    """
    cursor.execute(sql)
    data = cursor.fetchall()
  connection.close()
  return data
