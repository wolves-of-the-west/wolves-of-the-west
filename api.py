import copy
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

def get_national_inventory():
  connection = get_db_connection()
  with connection.cursor() as cursor:
    sql = """
      SELECT
        year,
        calf_crop as calves,
        (all_cattle - calves) as cattle,
        CONCAT(year, '-01-01T00:00:00-00:00') AS timestamp
      FROM (
        SELECT
          year,
          MAX(IF(data_item = 'CATTLE - CALF CROP, MEASURED IN HEAD', value, NULL)) as calf_crop,
          MAX(IF(data_item = 'CATTLE, CALVES - INVENTORY', value, NULL)) as calves,
          MAX(IF(data_item = 'CATTLE, INCL CALVES - INVENTORY', value, NULL)) as all_cattle
        FROM
          usda
        WHERE
          program = 'SURVEY'
          AND geo_level = 'NATIONAL'
          AND commodity = 'CATTLE'
          AND domain = 'TOTAL'
          AND (
            period = 'FIRST OF JAN'
            AND data_item IN (
              'CATTLE, CALVES - INVENTORY',
              'CATTLE, INCL CALVES - INVENTORY'
            )
          )
          OR (
            period = 'YEAR'
            AND data_item = 'CATTLE - CALF CROP, MEASURED IN HEAD'
          )
          GROUP BY
            year
          HAVING
            calves IS NOT NULL
            AND all_cattle IS NOT NULL
          ORDER BY
            year
      ) as tmp
    """
    cursor.execute(sql)
    allData = cursor.fetchall()

  calves = list(map(extract_calves, copy.deepcopy(allData)))
  cattle = list(map(extract_cattle, copy.deepcopy(allData)))
  
  return {
    'calf': calves,
    'cattle': cattle
  }

def get_state_inventory(state):
  connection = get_db_connection()
  with connection.cursor() as cursor:
    sql = """
      SELECT
        year,
        state,
        calf_crop as calves,
        (all_cattle - calves) as cattle,
        CONCAT(year, '-01-01T00:00:00-00:00') AS timestamp
      FROM (
        SELECT
          year,
          state,
          MAX(IF(data_item = 'CATTLE - CALF CROP, MEASURED IN HEAD', value, NULL)) as calf_crop,
          MAX(IF(data_item = 'CATTLE, CALVES - INVENTORY', value, NULL)) as calves,
          MAX(IF(data_item = 'CATTLE, INCL CALVES - INVENTORY', value, NULL)) as all_cattle
        FROM
          usda
        WHERE
          program = 'SURVEY'
          AND geo_level = 'STATE'
          AND commodity = 'CATTLE'
          AND domain = 'TOTAL'
    """
    if (state.lower() != 'all'):
      sql += "AND state ='%s'" % state
    sql += """  
        AND (
          period = 'FIRST OF JAN'
          AND data_item IN (
            'CATTLE, CALVES - INVENTORY',
            'CATTLE, INCL CALVES - INVENTORY'
          )
        )
        OR (
          period = 'YEAR'
          AND data_item = 'CATTLE - CALF CROP, MEASURED IN HEAD'            
        )
        GROUP BY
          year, state
        HAVING
          calves IS NOT NULL
          AND all_cattle IS NOT NULL
        ORDER BY
          year, state
      ) as tmp
    """
    cursor.execute(sql)
    allData = cursor.fetchall()

  calves = list(map(extract_calves, copy.deepcopy(allData)))
  cattle = list(map(extract_cattle, copy.deepcopy(allData)))

  return {
    'calf': calves,
    'cattle': cattle
  }

def extract(key, data):
  data['value'] = data.pop(key)
  data.pop('cattle' if key == 'calves' else 'calves')
  return data

def extract_calves(data):
  return extract('calves', data)

def extract_cattle(data):
  return extract('cattle', data)

@hug.get('/usda/cattle/stats')
def usda_cattle_stats():
  connection = get_db_connection()
  with connection.cursor() as cursor:
    sql = """
      SELECT
        min(year) as minYear,
        max(year) as maxYear
      FROM (
        SELECT
          year,
          MAX(IF(data_item = 'CATTLE, CALVES - INVENTORY', value, NULL)) as calves,
          MAX(IF(data_item = 'CATTLE, INCL CALVES - INVENTORY', value, NULL)) as all_cattle
        FROM
          usda
        WHERE
          program = 'SURVEY'
          AND period = 'FIRST OF JAN'
          AND geo_level = 'NATIONAL'
          AND commodity = 'CATTLE'
          AND data_item IN (
            'CATTLE, CALVES - INVENTORY',
            'CATTLE, INCL CALVES - INVENTORY'
          )
          AND domain = 'TOTAL'
        GROUP BY
          year
        HAVING
          calves IS NOT NULL
          AND all_cattle IS NOT NULL
        ORDER BY
          year
      ) as tmp
    """
    cursor.execute(sql)
    data = cursor.fetchone()
  connection.close()
  return data

@hug.get('/usda/cattle/national')
def usda_cattle_national():
  inventoryData = get_national_inventory()
  return {
    'cattleInventoryData': inventoryData['cattle'],
    'calfInventoryData': inventoryData['calf'],
    'cattleLossData': get_national_loss('CATTLE, (EXCL CALVES) - LOSS, DEATH, MEASURED IN HEAD'),
    'calfLossData': get_national_loss('CATTLE, CALVES - LOSS, DEATH, MEASURED IN HEAD')
  }

def get_national_loss(data_item):
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
        AND period = 'YEAR'
        AND geo_level = 'NATIONAL'
        AND commodity = 'CATTLE'
        AND data_item = '{0}'
        AND domain = 'TOTAL'
    """.format(data_item)
    sql += """
      ORDER BY
        year
    """
    cursor.execute(sql)
    data = cursor.fetchall()
  return data

@hug.get('/usda/cattle/state')
def usda_cattle_state(state):

  connection = get_db_connection()
  with connection.cursor() as cursor:
    maxSQL = """
      SELECT
        MAX(value) as maxStateValue
      FROM
        usda
      WHERE
        program = 'SURVEY'
        AND period = 'FIRST OF JAN'
        AND geo_level = 'STATE'
        AND commodity = 'CATTLE'
        AND data_item = 'CATTLE, INCL CALVES - INVENTORY'
        AND domain = 'TOTAL'
    """
    cursor.execute(maxSQL)
    maxStateValue = cursor.fetchone()['maxStateValue']
    
  inventoryData = get_state_inventory(state)

  return {
    'cattleInventoryData': inventoryData['cattle'],
    'calfInventoryData': inventoryData['calf'],
    'cattleLossData': get_state_loss('CATTLE, (EXCL CALVES) - LOSS, DEATH, MEASURED IN HEAD', state),
    'calfLossData': get_state_loss('CATTLE, CALVES - LOSS, DEATH, MEASURED IN HEAD', state),
    'maxStateValue': maxStateValue
  }

def get_state_loss(data_item, state):
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
        AND period = 'YEAR'
        AND geo_level = 'STATE'
        AND commodity = 'CATTLE'
        AND data_item = '{0}'
        AND domain = 'TOTAL'
    """.format(data_item)
    if (state.lower() != 'all'):
      sql += "AND state ='%s'" % state
    sql += """
      ORDER BY
        year,
        state
    """
    cursor.execute(sql)
    data = cursor.fetchall()
  return data