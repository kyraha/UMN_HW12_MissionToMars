from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


@app.route("/")
def index():
    mission = mongo.db.mission.find_one()
    return render_template("index.html", mission=mission)


@app.route("/scrape")
def scraper():
    mission = mongo.db.mission
    mission_data = scrape_mars.scrape()
    mission.update({}, mission_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)

