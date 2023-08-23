# Import all dependencies: 
################################################# 
import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 

# Create connection to Hawaii.sqlite file
#################################################
engine = create_engine("sqlite:///Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# # Save references to the measurement and station tables in the database
Measurement = Base.classes.measurement
Station = Base.classes.station

# Initialize Flask
#################################################
app = Flask(__name__)

# Create Flask Routes 
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes for Hawaii Weather Data:<br/><br>"
        f"-- Daily Precipitation Totals for Last Year: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Daily Temperature Observations for Most Active Station Last Year: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"        
    )

# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation for the last year
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        func.sum(Measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
   
    session.close()

    # Return a dictionary with the date as key and the daily precipitation total as value
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

# Create stations route
@app.route("/api/v1.0/stations")
def station(): 

    session = Session(engine)

    station_results = session.query(Station.station,Station.id).all()

    session.close()  
    
    stations_values = []
    for station, id in station_results:
        stations_values_dict = {}
        stations_values_dict['station'] = station
        stations_values_dict['id'] = id
        stations_values.append(stations_values_dict)
    return jsonify (stations_values) 

# Create temperature observation route 
@app.route("/api/v1.0/tobs") 
def tobs():
    session = Session(engine)
    
    # Create query to find the last date in the database
    last_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first() 

    print(last_date)
    
    # check to see if last year was correctly returned by creating dictionary to return last year value to browser in JSON format
    date_values = []
    for date in last_date:
        last_year_dict = {}
        last_year_dict["date"] = date
        date_values.append(last_year_dict) 
    print(date_values)
   

    # Create query_start_date by finding the difference between date time object of "2017-08-23" - 365 days
    start_date = dt.date(2017, 8, 23)-dt.timedelta(days =365) 
    print(start_date) 
    # returns: 2016-08-23 

    # Find most active station
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = active_station[0] 

    session.close() 
    print(most_active_station)
    # returns: USC00519281  

    # Find dates and tobs for the most active station (USC00519281) within the last year 
    active_station_measurements = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > start_date).\
        filter(Measurement.station == most_active_station) 
    

    # Create a list of dates,tobs,and stations with dictionary values queried above
    active_station_values = []
    for date, tobs, station in active_station_measurements:
        dates_tobs_dict = {}
        dates_tobs_dict["date"] = date
        dates_tobs_dict["tobs"] = tobs
        dates_tobs_dict["station"] = station
        active_station_values.append(dates_tobs_dict)
        
    return jsonify(active_station_values) 

# Create start date route
@app.route("/api/v1.0/<start>")

def start_date(start):
    session = Session(engine) 

    # Find minimum, average, and maxaimum temperature observations
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close() 

    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["TMin"] = min
        start_date_tobs_dict["TAvg"] = avg
        start_date_tobs_dict["TMax"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)

# Create start/end date route
@app.route("/api/v1.0/<start>/<end>")

def Start_end_date(start, end):
    session = Session(engine)     
  

    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
  
    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_end_values = []
    for min, avg, max in start_end_results:
        start_end_dict = {}
        start_end_dict["TMIN"] = min
        start_end_dict["TAVG"] = avg
        start_end_dict["TMAX"] = max
        start_end_values.append(start_end_dict) 
    

    return jsonify(start_end_values)
   
if __name__ == '__main__':
    app.run(debug=True) 