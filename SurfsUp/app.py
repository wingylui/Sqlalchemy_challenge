# import sqlachemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np


# Setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with = engine)

# reflect the tables
station = Base.classes.station
measurement = Base.classes.measurement


from flask import Flask, jsonify


# Crete an app
app = Flask(__name__)

@app.route("/")
def home():
    return (
        "<h1>Home Page</h1>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation/date:YYYY-MM-DD<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start_date:YYYY-MM-DD<br/>"
        "/api/v1.0/start_date:YYYY-MM-DD/end_date:YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation/<input_date>")
def precipitation(input_date):
    # create session (link) from Python to the database
    session = Session(bind= engine)

    # query precipitation results by the input date
    results = session.query(measurement.prcp).filter(measurement.date == input_date).all()
    session.close()

    # put all the results into a list and then create a dictionary to hold all the output
    prcp_list = []
    for prcp in results:
        prcp_list.append(prcp[0])
    
    # creating a dictionary to hold all the output
    precipitation_dic  = {
        "date" : input_date,
        "precipitation" : prcp_list
    }

    return jsonify(precipitation_dic)

@app.route("/api/v1.0/stations")
def stations():
    # create session (link) from Python to the database
    session = Session(bind= engine)

    # query a list of stations
    results = session.query(station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    # Create a dictionary from the all the output
    all_stations = []
    for name, lat, lng, elevation in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # create session (link) from Python to the database
    session = Session(bind= engine)
    # dates and tobs of the most active station in the last 12 months
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281").\
        filter(measurement.date.between("2016-08-23","2017-08-23"))
    session.close()

    # Create a dictionary from the all the output
    tobs_in_previous_year = []
    for date, tobs in results:
        tobs_dic = {}
        tobs_dic["date"] = date
        tobs_dic["tobs"] = tobs
        tobs_in_previous_year.append(tobs_dic)
    
    return jsonify(tobs_in_previous_year)


@app.route("/api/v1.0/<start_date>")
def temp_for_first_provide(start_date):
    # create session (link) from Python to the database
    session = Session(bind= engine)


    # last date in the database
    last_date = session.query(func.max(measurement.date)).all()
    last_date = last_date[0][0]

    # calculate lowest, highest and average temp from the start date to the last date in the database
    lowest_temp = session.query(func.min(measurement.tobs)).filter(measurement.date.between(start_date, last_date)).first()
    highest_temp = session.query(func.max(measurement.tobs)).filter(measurement.date.between(start_date, last_date)).first()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date.between(start_date, last_date)).first()
    session.close()
    
    # Create a dictionary from the all the output
    temp = {}
    temp["date"] = start_date
    temp["lowest temp"] = lowest_temp[0]
    temp["highest temp"] = highest_temp[0]
    temp["average temp"] = avg_temp[0]

    return jsonify(temp)


@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_for_first_last_provide(start_date, end_date):
    # create session (link) from Python to the database
    session = Session(bind= engine)

    # calculate lowest, highest and average temp from the start date to the end date in the database
    lowest_temp = session.query(func.min(measurement.tobs)).filter(measurement.date.between(start_date, end_date)).first()
    highest_temp = session.query(func.max(measurement.tobs)).filter(measurement.date.between(start_date, end_date)).first()
    avg_temp = session.query(func.avg(measurement.tobs)).filter(measurement.date.between(start_date, end_date)).first()
    session.close()
    
    # Create a dictionary from the all the output
    temp = {}
    temp["start_date"] = start_date
    temp["end_date"] = end_date
    temp["lowest temp"] = lowest_temp[0]
    temp["highest temp"] = highest_temp[0]
    temp["average temp"] = avg_temp[0]

    return jsonify(temp)


# allow using debug mode so continuously updating the web page
if __name__ == "__main__":
    app.run(debug= True)