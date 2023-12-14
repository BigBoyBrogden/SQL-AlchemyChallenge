# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    available_routes = ["/api/v1.0/precipitation", "/api/v1.0/stations", "/api/v1.0/tobs", "/api/v1.0/<start>", "/api/v1.0/<start>/<end>"]
    return available_routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_ago = one_year_ago.strftime("%Y-%m-%d")

    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    precipitation_dict = {}
    for date, prcp in precipitation_data:
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    station_list = []
    for station in stations:
        station_list.append(station[0])
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_ago = one_year_ago.strftime("%Y-%m-%d")

    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station_id = most_active_stations[0][0]

    one_year_ago_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()


    tobs_list = []
    for date, tobs in one_year_ago_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    start_date_stats = []
    for result in results:
        start_date_stats.append({"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]})
    return jsonify(start_date_stats)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()

    start_end_date_stats = []
    for result in results:
        start_end_date_stats.append({"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]})
    return jsonify(start_end_date_stats)


if __name__ == "__main__":
    app.run(debug=True)