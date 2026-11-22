"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
"""

import os
import io
import csv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import flask
from flask import request
from flask import Response, request
from flask_restful import Api, Resource
from datetime import datetime
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
import logging

###############
# Globals
###############

app = flask.Flask(__name__)
api = Api(app)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.brevets

###############
# Pages
###############

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404

###############
# AJAX request handlers
# These return JSON, rather than rendering pages.
###############

@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")

    km = request.args.get('km', type=float)
    distance = request.args.get("distance", type=int)
    begin_date = request.args.get("begin_date")
    begin_time = request.args.get("begin_time")

    app.logger.debug("km={}".format(km))
    app.logger.debug("distance={}".format(distance))
    app.logger.debug("begin_date={}".format(begin_date))
    app.logger.debug("begin_time={}".format(begin_time))
    app.logger.debug("request.args: {}".format(request.args))

    # Handles errors
    try:
        start_time = "{}T{}".format(begin_date, begin_time)
        open_time = acp_times.open_time(km, distance, start_time)
        close_time = acp_times.close_time(km, distance, start_time)
    except (ValueError, TypeError, arrow.parser.ParserError):
        return flask.jsonify(erro="Invalid Input"), 400

    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route("/insert", methods=["POST"])
def insert():
    controls = request.get_json(silent=True)

    # Error handles for invalid or empty inputs
    if not isinstance(controls, list) or not controls:
        return flask.jsonify(error="Invalid control list"), 400
    for control in controls:
        if not isinstance(control, dict): 
            return flask.jsonify(error="Each control must be an object"), 400
        # Check if all the keys exist
        if not all(field in control for field in ("km", "open", "close")):
            return flask.jsonify(error="Missing required control fields"), 400
        # Check if all the keys have a value
        if not all(control[field] not in (None, "") for field in ("km", "open", "close")):
            return flask.jsonify(error="Missing required control values"), 400

    try:    
        db.times.insert_many(controls)
    except PyMongoError:
        app.logger.exception("Unable to save control times")
        return flask.jsonify(error="Unable to save control times"), 500
    
    return flask.jsonify(status="ok")

@app.route("/fetch", methods=["GET"])
def fetch():
    try:
        times = list(db.times.find({}, {"_id": 0}))
    except PyMongoError:
        app.logger.exception("Unable to fetch stored control times")
        return flask.jsonify(error="Unable to fetch stored control times"), 500
    
    return flask.jsonify(times=times)

@app.route("/display")
def display():
    return flask.render_template("display.html")

###############
# Endpoint resource classes
# Flask RESTful resources that respond to HTTP GET requests
###############

# ----------Helper functions----------

def get_control_times():
    try:
        times = list(db.times.find({}, {"_id": 0}))             # Grab the data from MongoDB
        return times, None
    except PyMongoError:
        app.logger.exception("Unable to fetch stored control times")
        return None, ({"error": "Unable to fetch stored control times"}, 500)

def create_csv(times, fields):
    output = io.StringIO()                                      # Create a text buffer
    writer = csv.writer(output)                                 # Create a CSV writer
    writer.writerow(fields)                                     # Write the CSV column headers
    for control in times:
        writer.writerow([control[field] for field in fields])   # Write the selected field values
    return Response(output.getvalue(), mimetype="text/csv")     # Return the CSV response

"""
The line: "2000 " + control[field], "%Y %a %m/%d %H:%M" has a random year 
(being 2000) added to it, this is because my data stored in MongoDB
doesn't include a year, so I got an internal server error and found out 
I couldn't parse a day and month without also providing a year.
"""
def get_top_times(times, field):
    top = request.args.get("top")                               # Get the top K value requested
    if top is not None:                                         # Check if a top K is requested
        try:
            top = int(top)                                      # Convert the requested top K into an int
            if top < 1:
                raise ValueError
        except ValueError:
            return None, ({"error": "top must be a positive integer"}, 400)
        times = sorted(                                         # Sort controls in ascending order
            times,
            key = lambda control: datetime.strptime(            # Convert the time string to a datetime object
                "2000 " + control[field], "%Y %a %m/%d %H:%M"   # Append a year to the front of datetime
            )
        )
        times = times[:top]                                     # Slice the list at the first K times
    return times, None

# ----------Classes----------

class ListAll(Resource):
    def get(self):
        # Retrieve times from MongoDB
        times, error = get_control_times()
        if error:
            return error

        # Check if CSV format is requested
        if request.path.endswith("/csv"):
            return create_csv(times, ["km", "open", "close"])
        
        return {
            "distances": [control["km"] for control in times],
            "open_times": [control["open"] for control in times],
            "close_times": [control["close"] for control in times]
        }

class ListOpenOnly(Resource):
    def get(self):
        # Retrieve times from MongoDB
        times, error = get_control_times()
        if error:
            return error

        # Check if top K is requested
        times, error = get_top_times(times, "open")
        if error:
            return error

        # Check if CSV format is requested
        if request.path.endswith("/csv"):
            return create_csv(times, ["open"])
        
        return {"open_times": [control["open"] for control in times]}

class ListCloseOnly(Resource):
    def get(self):
        # Retrieve times from MongoDB
        times, error = get_control_times()
        if error:
            return error

        # Check if top K is requested
        times, error = get_top_times(times, "close")
        if error:
            return error

        # Check if CSV format is requested
        if request.path.endswith("/csv"):
            return create_csv(times, ["close"])
        
        return {"close_times": [control["close"] for control in times]}

# ----------Supported Endpoints----------

api.add_resource(ListAll, "/listAll", "/listAll/json", "/listAll/csv")
api.add_resource(ListOpenOnly, "/listOpenOnly", "/listOpenOnly/json", "/listOpenOnly/csv")
api.add_resource(ListCloseOnly, "/listCloseOnly", "/listCloseOnly/json", "/listCloseOnly/csv")

###############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
