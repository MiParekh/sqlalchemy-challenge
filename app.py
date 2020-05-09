#################################################
# Dependency Setup
#################################################

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Variables
#################################################

#Determine Maximum Date in Measurement table

max_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
max_date = list(np.ravel(max_date))[0]
max_date = dt.datetime.strptime(max_date, '%Y-%m-%d')

#Convert Year, Month, and Day into Integers for PY Calc

max_year = int(dt.datetime.strftime(max_date, '%Y'))
max_month = int(dt.datetime.strftime(max_date, '%m'))
max_day = int(dt.datetime.strftime(max_date, '%d'))

#Determine One year prior to max date using timedelta 

prior_year_date = dt.date(max_year, max_month, max_day) - dt.timedelta(days=365)
prior_year_date

#################################################
# Flask Routes
#################################################

@app.route("/")

#################################################
# Home Page and Available Routes
#################################################
def welcome():
    """Welcome to the Surfs Up Assignment Home Page."""
    return (
        f"Welcome to Surf's Up Assignment Home Page!<br/>"
        f"-----------------------------------------------<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/daterangeanalysis/start<br/>"
        f"/api/v1.0/daterangeanalysis/start_and_end"
        

    )

@app.route("/api/v1.0/precipitation")

#################################################
# Dates and Preciptiation records of last 12 months
#################################################
def precipitation():

    #Return query for list of dates and precipitation data
    results1 = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > prior_year_date).order_by(Measurement.date).all())

    #Create dictionary
    precip_data_dict = []
    for date, prcp in results1:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_data_dict.append(precip_dict)

    #Jsonify dictionary
    return jsonify(precip_data_dict)

@app.route("/api/v1.0/stations")

#################################################
# List of Stations
#################################################

def stations():
   
    #Return query for list of stations
    results2 = session.query(Station.name).all()
    
    #List of Stations
    stations_list = list(np.ravel(results2))

    #Jsonify list
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")

#################################################
# Date and Temp Observation of Most Active Station over the last 12 months
#################################################


def tobs():
   
    #Run query for all stations activity
    stations_activity = (session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())
    
    #Identify most active station
    most_active_station = stations_activity[0][0]

    #Return query for date and temperature observations
    results3 = (session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date > prior_year_date).order_by(Measurement.date).all())
 
    #Create dictionary
    tobs_data_dict = []
    for date, tobs in results3:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data_dict.append(tobs_dict)

    #Jsonify dictionary
    return jsonify(tobs_data_dict)


@app.route("/api/v1.0/daterangeanalysis/start")

#################################################
# Min, Max and Avg temp from Start Date to End of Data
#################################################

def startdate():
    
    #Start Date Variable
    
    start_date = "2015-01-14"

     #Return query for min temp, max temp and avg temp greater than and equal to start date
    results4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    #Create dictionary
    start_dict = []
    for min_temp2, avg_temp2, max_temp2 in results4:
        temp_dict2 = {}
        temp_dict2["min_temp"] = min_temp2
        temp_dict2["avg_temp"] = avg_temp2
        temp_dict2["max_temp"] = max_temp2
        start_dict.append(temp_dict2)

    #Jsonify dictionary
    return jsonify(start_dict)

@app.route("/api/v1.0/daterangeanalysis/start_and_end")

#################################################
# Min, Max and Avg temp from Start Date to End Date
#################################################

def startenddate():
    
    #Start and End Date Variables
   
    start_date2 = "2015-01-14"
    
    end_date2 = "2016-08-23"
    
     #Return query for min temp, max temp and avg temp between start and end date

    results5 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date2).filter(Measurement.date <= end_date2).all()

    #Create dictionary
    start_end_dict = []
    for min_temp, avg_temp, max_temp in results5:
        temp_dict = {}
        temp_dict["min_temp"] = min_temp
        temp_dict["avg_temp"] = avg_temp
        temp_dict["max_temp"] = max_temp
        start_end_dict.append(temp_dict)

    #Jsonify dictionary
    return jsonify(start_end_dict)

if __name__ == '__main__':
    app.run(debug=True)

