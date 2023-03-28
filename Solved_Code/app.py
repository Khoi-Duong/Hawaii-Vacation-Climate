# Import the dependencies.
import numpy as np
import json
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
Base.prepare(engine, reflect = True)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available API routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(measurement.date).all()[-1][0]
    recent_date_split = most_recent_date.split("-")
    recent_date = dt.date(int(recent_date_split[0]), int(recent_date_split[1]), int(recent_date_split[2]))
    oneyear_date = recent_date - dt.timedelta(days = 365)

    date_precip_scores = session.query(measurement.date, measurement.prcp)\
                                .filter(measurement.date >= oneyear_date)\
                                .filter(recent_date >= measurement.date).limit(365).all()
    
    date_precip_dict = {}

    for date, precipitation in date_precip_scores:
        date_precip_dict[date] = precipitation

    return jsonify(date_precip_dict)


@app.route("/api/v1.0/stations")
def s():
    station_options = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    station_list = []

    for s, n, long, lat, ele in station_options:
        station_list.append(n)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp():
    most_active_stations = session.query(station.station, func.count(measurement.station))\
                    .filter(station.station == measurement.station)\
                    .group_by(station.station)\
                    .order_by(func.count(measurement.station).desc()).all()
    
    most_recent_date = session.query(measurement.date).all()[-1][0]
    recent_date_split = most_recent_date.split("-")
    recent_date = dt.date(int(recent_date_split[0]), int(recent_date_split[1]), int(recent_date_split[2]))
    oneyear_date = recent_date - dt.timedelta(days = 365)

    station_temp = session.query(measurement.tobs, measurement.date)\
                        .filter(measurement.station == most_active_stations[0][0])\
                        .filter(measurement.date >= oneyear_date)\
                        .filter(recent_date >= measurement.date).limit(365).all()
    
    station_temp_list = []

    for temp, date in station_temp:
        station_temp_list.append(temp)

    return jsonify(station_temp_list)

@app.route("/api/v1.0/<start>")
def start(start):
    start_date = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                        .filter(measurement.date >= start).all()
                        #.filter(station.station == measurement.station).all()

    min_avg_max_list = []

    for d, min, max, avg in start_date:
        min_avg_max_dict = {"TMIN" : min, "TAVG" : avg, "TMAX" : max}
        min_avg_max_list.append(min_avg_max_dict)
     

    return jsonify(min_avg_max_list)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    start_date = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                        .filter(measurement.date >= start)\
                        .filter(end >= end).all()
    
    min_avg_max_list = []

    for d, min, max, avg in start_date:
        min_avg_max_dict = {"TMIN" : min, "TAVG" : avg, "TMAX" : max}
        min_avg_max_list.append(min_avg_max_dict)

        return jsonify(min_avg_max_list)
    
if __name__ == '__main__':
    app.run(debug = True)
