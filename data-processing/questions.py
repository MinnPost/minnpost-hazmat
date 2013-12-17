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

  # Change data to dictionary for better reference in application
  data_dict = []
  for d in data:
    t = d.__dict__
    del t['_labels']

    data_dict.append(t)

  with open(path, 'w') as output:
    output.write(json.dumps(data_dict, cls=AlchemyEncoder, indent=4))


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

# Year selection
year = func.cast(func.strftime("%Y", Incident.Date_Inc), Integer).label('year')
# Common filter to get specific data
common_filter = year >= 2000
# Some shared values.  This one gets individual incidents and key fields.
common_query_desc = session.query(Incident.Rpt_Num, Incident.C_R_Name, Incident.Ship_Name, Incident.Mode_Transpo, Incident.Tot_Amt_of_Damages, Incident.Date_Inc, Incident.Time_Inc, Incident.What_Failed_Desc, Incident.How_Failed_Desc, Incident.Commod_Long_Name, Incident.Quant_Released, Incident.Unit_of_Measure, Incident.Desc_of_Events).distinct(Incident.Rpt_Num)
# Count of reports
count = func.count(distinct(Incident.Rpt_Num)).label('count')
# Order or group by money
money = desc(func.cast(Incident.Tot_Amt_of_Damages, Numeric))
money_thousands = func.cast(func.cast(Incident.Tot_Amt_of_Damages / 1000, Integer) * 1000, Integer).label('money_thousands')
# Hour
hour = func.cast(func.cast(Incident.Time_Inc, Numeric()) / 100, Integer).label('hour')


# Total number of incidents
print "================================="
print "Making: total incidents"
incidents_total = session.query(count).filter(common_filter).all()
write_json('incidents_total', incidents_total)

# Number of incidents per year
print "================================="
print "Making: incidents by year"
query_data = session.query(year, count).filter(common_filter).group_by(year).order_by(year).all()
write_json('incidents_by_year', query_data)

print "================================="
print "Making: incidents by hour"
query_data = session.query(hour, count).filter(common_filter).group_by(hour).order_by(desc(count)).all()
write_json('incidents_by_hour', query_data)

print "================================="
print "Making: incidents by mode of transportation"
query_data = session.query(Incident.Mode_Transpo, count).filter(common_filter).group_by(Incident.Mode_Transpo).order_by(desc(count)).all()
write_json('incidents_by_transportation', query_data)

print "================================="
print "Making: incidents by zip code"
query_data = session.query(Incident.Inc_Zip, count).filter(common_filter).group_by(Incident.Inc_Zip).order_by(desc(count)).all()
write_json('incidents_by_zip', query_data)

print "================================="
print "Making: incidents by city"
query_data = session.query(Incident.Inc_City, count).filter(common_filter).group_by(Incident.Inc_City).order_by(desc(count)).all()
write_json('incidents_by_city', query_data)

print "================================="
print "Making: incidents by origin state"
query_data = session.query(Incident.Orig_State, count).filter(common_filter).group_by(Incident.Orig_State).order_by(desc(count)).all()
write_json('incidents_by_orig_state', query_data)

print "================================="
print "Making: incidents by weather condition"
query_data = session.query(Incident.Weather_Cond, count).filter(common_filter).group_by(Incident.Weather_Cond).order_by(desc(count)).all()
write_json('incidents_by_weather_cond', query_data)

print "================================="
print "Making: incidents by monetary damage (grouped by $1000 increments)"
query_data = session.query(money_thousands, count).filter(common_filter).group_by(money_thousands).order_by(desc(count)).all()
write_json('incidents_by_monetary_damage', query_data)

print "================================="
print "Making: incidents by material (top 100)"
query_data = session.query(Incident.Commod_Long_Name, count).filter(common_filter).group_by(Incident.Commod_Long_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_material', query_data)

print "================================="
print "Making: incidents by carrier (top 100)"
query_data = session.query(Incident.C_R_Name, count).filter(common_filter).group_by(Incident.C_R_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_carrier', query_data)

print "================================="
print "Making: incidents by shipper (top 100)"
query_data = session.query(Incident.Ship_Name, count).filter(common_filter).group_by(Incident.Commod_Long_Name).order_by(desc(count)).limit(100).all()
write_json('incidents_by_shipper', query_data)

print "================================="
print "Making: incidents where explosions happened"
query_data = common_query_desc.filter(common_filter).filter_by(Explosion_Result_Ind='Yes').order_by(Incident.Date_Inc).all()
write_json('explosion_incidents', query_data)

print "================================="
print "Making: fatal incidents"
query_data = common_query_desc.filter(common_filter).filter_by(HMIS_Serious_Fatal='Yes').order_by(desc(Incident.Tot_Hazmat_Fatal)).all()
write_json('fatal_incidents', query_data)

print "================================="
print "Making: undeclared incidents"
query_data = common_query_desc.filter(common_filter).filter_by(Undeclared_Shpmt='Yes').order_by(Incident.Date_Inc).all()
write_json('undeclared_incidents', query_data)

print "================================="
print "Making: 10 expensive incidents"
query_data = common_query_desc.filter(common_filter).order_by(money).limit(10).all()
write_json('most_expensive_incidents', query_data)

print "================================="
print "Making: 20 most released"
query_data = common_query_desc.filter(common_filter).group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(20).all()
write_json('most_released_incidents', query_data)

print "================================="
print "Making: 10 most released SLB"
query_data = common_query_desc.filter_by(Unit_of_Measure='SLB').filter(common_filter).group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(10).all()
write_json('most_released_incidents_slb', query_data)

print "================================="
print "Making: 10 most released LGA"
query_data = common_query_desc.filter_by(Unit_of_Measure='LGA').filter(common_filter).group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(10).all()
write_json('most_released_incidents_lga', query_data)

print "================================="
print "Making: 10 most released GCF"
query_data = common_query_desc.filter_by(Unit_of_Measure='GCF').filter(common_filter).group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(10).all()
write_json('most_released_incidents_gcf', query_data)

print "================================="
print "Making: 10 most released CI"
query_data = common_query_desc.filter_by(Unit_of_Measure='CI').filter(common_filter).group_by(Incident.Unit_of_Measure, Incident.Quant_Released).order_by(desc(Incident.Quant_Released)).limit(10).all()
write_json('most_released_incidents_ci', query_data)

