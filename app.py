from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd

from dateutil.relativedelta import relativedelta


from datetime import datetime
from datetime import timedelta
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Variable Declaration
#################################################
session = Session(engine)
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
most_recent_date = most_recent_date[0]
most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d").date()
one_year_ago = most_recent_date - relativedelta(years=1)
active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
most_active_station = active_stations[0][0]
session.close()

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        "Welcome to the Hawaii Weather Data API!<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        "/api/v1.0/stations - List of weather stations<br/>"
        "/api/v1.0/tobs - Temperature observations for the most active station in the last 12 months<br/>"
        "/api/v1.0/start_date - Minimum, Average, and Maximum temperatures for dates greater than or equal to the start date<br/>"
        "/api/v1.0/start_date/end_date - Minimum, Average, and Maximum temperatures for dates between the start and end date (inclusive)<br/>"
        "Note: to access values between a start and end date enter both dates using format: YYYY-mm-dd/YYYY-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation2():
    session = Session(engine)
    # Query precipitation data for the last year
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()
    
    # Create a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    station_list = [station[0] for station in station_data]
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    tobs_list = [[row.date, row.tobs] for row in tobs_data]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    temperature_list = [[tmin, tavg, tmax] for tmin, tavg, tmax in temperature_data]
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    session = Session(engine)
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    temperature_list = [[tmin, tavg, tmax] for tmin, tavg, tmax in temperature_data]
    return jsonify(temperature_list)


if __name__ == "__main__":
    app.run(debug=True)

""" 




 """