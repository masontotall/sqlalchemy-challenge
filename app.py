import pandas as pd
import sqlalchemy
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

## database and engine set up

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement

Station = Base.classes.station

#flask set up

app = Flask(__name__)

#flask routes

@app.route("/")
def home():
    return(
        f"Welcome! These are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Return precipt data for the last year of data
    p_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.date <= '2017-08-23').all()

    session.close()

    #Convert to dictionary and jsonify

    prcp_data = []
    for date, prcp in p_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp

        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Return json list of stations based on dataset

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    session.close()

    return jsonify(active_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Query the dates and temperature observations of the 
    #most active station for the last year of data.

    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    most_active = active_stations[0][0]

    ma_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date <='2017-08-23').\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.station == most_active).all()

    session.close()

    #Convert list to dict

    tobs_data = []
    for date, tobs in ma_station:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs

        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    query_result = session.query(func.min(Measurement.tobs),
             func.max(Measurement.tobs),
             func.avg(Measurement.tobs)).\
             filter(Measurement.date >= start).all()

    session.close()

    #create dictionary and append to a list then jsonify

    start_tobs = []
    for min, max, avg in query_result:
        start_tobs_dict = {}
        start_tobs_dict["min_temp"] = min
        start_tobs_dict["max_temp"] = max
        start_tobs_dict["avg_temp"] = avg
        start_tobs.append(start_tobs_dict)

    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    query_result = session.query(func.min(Measurement.tobs),
             func.max(Measurement.tobs),
             func.avg(Measurement.tobs)).\
             filter(Measurement.date >= start).\
             filter(Measurement.date <= end).all()

    session.close()

    #create dictionary, append to list, jsonify

    start_end_tobs = []
    for min, max, avg in query_result:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = min
        start_end_tobs_dict["max_temp"] = max
        start_end_tobs_dict["avg_temp"] = avg
        start_end_tobs.append(start_end_tobs_dict)

    return jsonify(start_end_tobs)





if __name__ == "__main__":
    app.run(debug = True)