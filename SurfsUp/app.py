# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f'Home page for Hawaii Climate API</br>'
        f'The available routes:</br>'
        f'Precipitation Data - /api/v1.0/precipitation</br>'
        f'Weather Stations - /api/v1.0/stations</br>'
        f'Observed Temperature from Station USC00519281 - /api/v1.0/tobs</br>'
        f'List of Min, Max, & Avg Temperature Data from Start Date - /api/v1.0/start</br>'
        f'List of Min, Max, & Avg Temperature Data within Start/End Dates - /api/v1.0/start/end</br>'
        f'Data Available between 2010-01-01 and 2017-08-23 in a yyyy-mm-dd format'
    )

@app.route("/api/v1.0/precipitation")
def precipiation():
    session = Session(engine)
  
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    """Return Stations in Hawaii"""
    # Query stations
    station_query= session.query(Station.station).all()
    
    session.close()
    
    #List of stations
    station_names = list(np.ravel(station_query))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    """Return dates and temperature observations in station USC00519281"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query observed temps of most active station
    tobs_year = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= prev_year).all()
    
    session.close()
    
    #List of tobs
    tobs_year_list = list(np.ravel(tobs_year))
    return jsonify(tobs_year_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tempstats(start=None, end=None):
    session = Session(engine)

    """Return min, man, and avg temperature data"""
    # Query selection
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    #if loop beginning with start only requests
    if not end:
        #Start-only Query
        start_data = session.query(*sel).\
            filter(Measurement.date >= start).all()
        #Start-only temp data list
        start_temp = list(np.ravel(start_data))
        return jsonify(start_temp)
    
    # With end requests
    #Start-to-end Query
    start_end = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    #Start-to-end temp data list
    start_end_temp = list(np.ravel(start_end))
    return jsonify(start_end_temp)
    

if __name__ == "__main__":
    app.run(debug=True)