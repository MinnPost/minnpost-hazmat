"""
Asking questions of the data and producing data files
for the final pieces.
"""
import json
import os
import csv
import dateutil.parser
import datetime
from decimal import Decimal
from sqlalchemy import create_engine, MetaData, Table, distinct, func, Numeric, Integer, desc, asc
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, mapper, class_mapper

# Database configuration.  Change connection
# string to other SQLAlchemy supported databases.
database_file_path = os.path.join(os.path.dirname(__file__), '../data/hazmat.db')
database_connection = 'sqlite:///' + database_file_path

# Custom class to turn SQLAlchemy object to JSON
class AlchemyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return float(obj)

    if isinstance(obj, datetime.date):
      return obj.strftime('%Y-%m-%d')

    if isinstance(obj, Incident):
      # an SQLAlchemy class
      fields = {}
      for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
        data = obj.__getattribute__(field)
        try:
          # this will fail on non-encodable values, like other classes
          json.dumps(data)
          fields[field] = data
        except TypeError:
          fields[field] = None
      # a json-encodable dict
      return fields

    return json.JSONEncoder.default(self, obj)


# Function to handle writing out json files
def write_json(name, data):
  path = os.path.join(os.path.dirname(__file__), '../data/question-%s.json' % name)
  with open(path, 'w') as output:
    output.write(json.dumps(data, cls=AlchemyEncoder, indent=4))


# Create connection/database.
db = create_engine(database_connection)
Base = declarative_base()
metadata = MetaData(db)

# Database ORM objects
# Layout
class Layout(object):
  pass

# Incidents
class Incident(object):
  pass

# Reports
class Report(object):
  pass

# Connect existing tables
layout_table = Table('layout', metadata, autoload=True)
layout_mapper = mapper(Layout, layout_table)
incidents_table = Table('incidents', metadata, autoload=True)
incidents_mapper = mapper(Incident, incidents_table)
reports_table = Table('reports', metadata, autoload=True)
reports_mapper = mapper(Report, reports_table)

# Create session
Session = sessionmaker(bind=db)
session = Session()

# How many reports
layout_count = session.query(Layout).count()
report_count = session.query(Report).count()
incident_count = session.query(Incident).count()
print "Layout rows: %s" % layout_count
print "Report rows: %s" % report_count
print "Incident rows: %s" % incident_count

# Some shared values.  This one gets individual incidents and key fields.
common_query_desc = session.query(Incident.Rpt_Num, Incident.C_R_Name, Incident.Ship_Name, Incident.Tot_Amt_of_Damages, Incident.Date_Inc, Incident.Time_Inc, Incident.What_Failed_Desc, Incident.How_Failed_Desc, Incident.Commod_Long_Name, Incident.Quant_Released, Incident.Unit_of_Measure, Incident.Desc_of_Events).distinct(Incident.Rpt_Num)
# Count of reports
count = func.count(distinct(Incident.Rpt_Num))

# Total number of incidents
print "================================="
print "Making: total incidents"
incidents_total = session.query(count).all()
write_json('incidents_total', incidents_total)

# Number of incidents per year
print "================================="
print "Making: incidents by year"
year = func.strftime("%Y", Incident.Date_Inc)
incidents_by_year = session.query(year, count).group_by(year).order_by(year).all()
write_json('incidents_by_year', incidents_by_year)

print "================================="
print "Making: incidents by hour"
hour = func.cast(func.cast(Incident.Time_Inc, Numeric()) / 100, Integer)
incidents_by_hour = session.query(hour, count).group_by(hour).order_by(desc(count)).all()
write_json('incidents_by_hour', incidents_by_hour)

print "================================="
print "Making: incidents by mode of transportation"
incidents_by_transportation = session.query(Incident.Mode_Transpo, count).group_by(Incident.Mode_Transpo).order_by(desc(count)).all()
write_json('incidents_by_transportation', incidents_by_transportation)

print "================================="
print "Making: incidents by zip code"
incidents_by_zip = session.query(Incident.Inc_Zip, count).group_by(Incident.Inc_Zip).order_by(desc(count)).all()
write_json('incidents_by_zip', incidents_by_zip)

print "================================="
print "Making: incidents by city"
incidents_by_city = session.query(Incident.Inc_City, count).group_by(Incident.Inc_City).order_by(desc(count)).all()
write_json('incidents_by_city', incidents_by_city)

print "================================="
print "Making: incidents by origin state"
incidents_by_orig_state = session.query(Incident.Orig_State, count).group_by(Incident.Orig_State).order_by(desc(count)).all()
write_json('incidents_by_orig_state', incidents_by_orig_state)

print "================================="
print "Making: incidents by weather condition"
incidents_by_weather_cond = session.query(Incident.Weather_Cond, count).group_by(Incident.Weather_Cond).order_by(desc(count)).all()
write_json('incidents_by_weather_cond', incidents_by_weather_cond)

print "================================="
print "Making: incidents by monetary damage (grouped by $1000 increments)"
thousands = func.cast(Incident.Tot_Amt_of_Damages / 1000, Integer) * 1000
incidents_by_monetary_damage = session.query(thousands, count).group_by(thousands).order_by(desc(count)).all()
write_json('incidents_by_monetary_damage', incidents_by_monetary_damage)

print "================================="
print "Making: incidents by material (top 100)"
incidents_by_material = session.query(Incident.Commod_Long_Name, count).group_by(Incident.Commod_Long_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_material', incidents_by_material)

print "================================="
print "Making: incidents by carrier (top 100)"
incidents_by_carrier = session.query(Incident.C_R_Name, count).group_by(Incident.C_R_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_carrier', incidents_by_carrier)

print "================================="
print "Making: incidents by shipper (top 100)"
incidents_by_shipper = session.query(Incident.Ship_Name, count).group_by(Incident.Commod_Long_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_shipper', incidents_by_shipper)

print "================================="
print "Making: incidents where explosions happened"
explosion_incidents = common_query_desc.filter_by(Explosion_Result_Ind='Yes').order_by(Incident.Date_Inc).all()
write_json('explosion_incidents', explosion_incidents)

print "================================="
print "Making: fatal incidents"
fatal_incidents = common_query_desc.filter_by(HMIS_Serious_Fatal='Yes').order_by(desc(Incident.Tot_Hazmat_Fatal))
write_json('fatal_incidents', fatal_incidents.all())

print "================================="
print "Making: undeclared incidents"
undeclared_incidents = common_query_desc.filter_by(Undeclared_Shpmt='Yes').order_by(Incident.Date_Inc)
write_json('undeclared_incidents', undeclared_incidents.all())

print "================================="
print "Making: 10 expensive incidents"
money = desc(func.cast(Incident.Tot_Amt_of_Damages, Numeric))
most_expensive_incidents = common_query_desc.order_by(money).limit(10)
write_json('most_expensive_incidents', most_expensive_incidents.all())

print "================================="
print "Making: 20 most released"
most_released_incidents = common_query_desc.group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(20)
write_json('most_released_incidents', most_released_incidents.all())

