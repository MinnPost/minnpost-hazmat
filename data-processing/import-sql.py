"""
Imports layout and data for HAZMAT data.  Creates a refence table
for Reports, as there are multiple incidents per report.

Ideally we would create a different table for the places to help things like
geocoding but that is not implemented at the moment.
"""
import os
import csv
import dateutil.parser
from sqlalchemy import create_engine, Column, Numeric, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper

# Database configuration.  Change connection
# string to other SQLAlchemy supported databases.
database_file_path = os.path.join(os.path.dirname(__file__), '../data/hazmat.db')
database_connection = 'sqlite:///' + database_file_path

# Custom grouping and translations.  Data entry across reports is not
# consistent so we want to group things together that are very likely the
# same thing.  These get stored in a different column.  We have not gone
# through all the data, but simply picking out the more common occurences.
translations = {
  'Commod_Long_Name': {
    'PAINT INCLUDING PAINT  LACQUER  ENAMEL  STAIN  SHELLAC SOLUTIONS  VARNISH  POLISH  LIQUID FILLER AND LIQUID LACQUER BASE': 'PAINT OR RELATED',
    'PAINT RELATED MATERIAL INCLUDING PAINT THINNING  DRYING  REMOVING  OR REDUCING COMPOUND': 'PAINT OR RELATED',
    'PAINT': 'PAINT OR RELATED',
    'GASOLINE INCLUDES GASOLINE MIXED WITH ETHYL ALCOHOL  WITH NOT MORE THAN 10% ALCOHOL': 'GASOLINE',
    'GASOHOL GASOLINE MIXED WITH ETHYL ALCOHOL  WITH NOT MORE THAN 10% ALCOHOL': 'GASOLINE',
    'PRINTING INK  FLAMMABLE OR PRINTING INK RELATED MATERIAL (INCLUDING PRINTING INK THINNING OR REDUCING COMPOUND)  FLAMMABLE': 'PRINTING INK OR RELATED'
  },
  'C_R_Name': {
    'FEDEX GROUND PACKAGE SYSTEM  INC.': 'FEDEX',
    'FEDEX FREIGHT  INC.': 'FEDEX',
    'FEDERAL EXPRESS CORPORATION': 'FEDEX',
    'UNITED PARCEL SERVICE': 'UPS',
    'UNITED PARCEL SERVICE  INC.': 'UPS',
    'UNITED PARCEL SERVICE OF AMERICA  INC.': 'UPS',
    'UPS GROUND FREIGHT  INC.': 'UPS',
    'UNITED PARCEL SERVICE CO.': 'UPS',
    'YRC WORLDWIDE INC.': 'YRC',
    'YRC INC.': 'YRC',
    'YRC GLOBAL': 'YRC',
    'CON-WAY FREIGHT INC.': 'CON-WAY',
    'CON-WAY FREIGHT INC': 'CON-WAY',
    'CON-WAY FREIGHT  INC': 'CON-WAY',
    'CON-WAY CENTRAL EXPRESS INC.': 'CON-WAY',
    'CONWAY CENTRAL EXPRESS': 'CON-WAY'
  },
  'Ship_Name': {
    'FUJIFILM NORTH AMERICA CORPORATION': 'FUJIFILM',
    'FUJIFILM CORP': 'FUJIFILM',
    'FUJIFILM ELECTRONIC MATERIALS U.S.A.  INC.': 'FUJIFILM',
    'FUJIFILM U.S.A.  INC.': 'FUJIFILM',
    'FUJI PHOTO FILM': 'FUJIFILM',
    'FUJI FILM PHOTO': 'FUJIFILM',
    'THE SHERWIN-WILLIAMS COMPANY': 'THE SHERWIN-WILLIAMS COMPANY',
    'SHERWIN-WILLIAMS AUTOMOTIVE FINISHES CORP.': 'THE SHERWIN-WILLIAMS COMPANY',
    'THE VALSPAR CORPORATION': 'VALSPAR',
    'VALSPAR CORP': 'VALSPAR',
    'VALSPAR': 'VALSPAR',
    'FISHER SCIENTIFIC COMPANY LLC': 'FISHER SCIENTIFIC COMPANY',
    'FISHER SCIENTIFIC INTERNATIONAL  INC.': 'FISHER SCIENTIFIC COMPANY',
    'FISHER SCIENTIFIC COMPANY L.L.C.': 'FISHER SCIENTIFIC COMPANY',
    'VWR INTERNATIONAL  LLC': 'VWR INTERNATIONAL',
    'VWR INTERNATIONAL LLC': 'VWR INTERNATIONAL'
  }
}

# Source files
layout_path = os.path.join(os.path.dirname(__file__), '../data/layout-cleaned.csv')
data_path = os.path.join(os.path.dirname(__file__), '../data/original/Minnesota.csv')

# Create connection/database.
db = create_engine(database_connection)
Base = declarative_base()

# Layout
class Layout(Base):
  __tablename__ = 'layout'

  name = Column(String, primary_key=True)
  title = Column(String)
  column_type = Column(String)
  description = Column(Text)

# Incidents
class Incident(Base):
  __tablename__ = 'incidents'

  id = Column(Integer, primary_key=True)
  grouped_Commod_Long_Name = Column(String)
  grouped_C_R_Name = Column(String)
  grouped_Ship_Name = Column(String)

# Reports
class Report(Base):
  __tablename__ = 'reports'

  Rpt_Num = Column(String, primary_key=True)

# Read in layout information to make columns for incidents
with open(layout_path, 'rU') as csv_layout:
  layout = csv.reader(csv_layout, dialect='excel')
  reading = 0

  for row in layout:
    if row[0] != '' and row[0] is not None and reading != 0:
      column_class = String
      if row[2] == 'Numeric':
        column_class = Numeric
      elif row[2] == 'Date':
        column_class = Date

      addition_column = Column(row[0], column_class)
      setattr(Incident, row[0], addition_column)

    reading = reading + 1

# Make tables
Base.metadata.create_all(db)

# Start db session
Session = sessionmaker(bind=db)
session = Session()

# Remove all data
for tbl in reversed(Base.metadata.sorted_tables):
  db.execute(tbl.delete())

# Read in layout information
print "Importing layout data..."
with open(layout_path, 'rU') as csv_layout:
  layout = csv.reader(csv_layout, dialect='excel')
  reading = 0

  for row in layout:
    if row[0] is not None and reading != 0:
      layout_row = Layout(
        name=unicode(row[0], errors='ignore').strip(),
        title=unicode(row[1], errors='ignore').strip(),
        column_type=unicode(row[2], errors='ignore').strip(),
        description=unicode(row[3], errors='ignore').strip()
      )
      session.merge(layout_row)

    reading = reading + 1

  session.commit()

# Update tables with column information
layout_fields = session.query(Layout).all()

# Read in hazmat data
with open(data_path, 'rU') as csv_data:
  data = csv.DictReader(csv_data, dialect='excel')

  # Basic method to see what columns may be different
  # between incident rows
  # multi = {}
  # for row in data:
  #   if row['MultRows'] == 'Yes':
  #     if row['Rpt_Num'] in multi:
  #       print '============ %s ============' % (row['Rpt_Num'])
  #       for key in row:
  #         if row[key] != multi[row['Rpt_Num']][key]:
  #           print '%s: %s <> %s' % (key, row[key], multi[row['Rpt_Num']][key])
  #
  #     multi[row['Rpt_Num']] = row

  # Get layout data so that we can do some conversions
  layout = session.query(Layout)

  # Start importing data
  reading = 1

  print "Importing incident data..."
  for row in data:
    # Create row in reports
    report_row = Report(Rpt_Num=row['Rpt_Num'])
    session.merge(report_row)

    # Do some conversoins, like convert numbers to floats
    for key in row:
      layout_info = layout.filter_by(name=key).first()

      if row[key] == 'NULL':
        row[key] = None
      if layout_info.column_type == 'Numeric' and row[key] is not None:
        row[key] = float(row[key])
      elif layout_info.column_type == 'Date' and row[key] is not None:
        row[key] = dateutil.parser.parse(row[key]).date()
      elif row[key] is not None:
        row[key] = unicode(row[key], errors='ignore').strip()

    # Handle some translations
    for t in translations:
      if row[t] is not None and row[t] in translations[t]:
        row['grouped_' + t] = translations[t][row[t]]
      else:
        row['grouped_' + t] = row[t]

    # Add an ID
    row['id'] = reading

    # Create row for incident
    incident_row = Incident(**row)
    session.merge(incident_row)

    # Some feedback and commit occasionally
    if reading % 100 == 0:
      print reading
      session.commit()

    reading = reading + 1

  session.commit()

# Verify some data
layout_count = session.query(Layout).count()
report_count = session.query(Report).count()
incident_count = session.query(Incident).count()

print "Layout rows: %s" % layout_count
print "Report rows: %s" % report_count
print "Incident rows: %s" % incident_count

