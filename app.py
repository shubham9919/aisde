from flask import Flask, render_template, request, session
from common.database.database_utils import (
    get_data_from_current_db,
    predicted_website_db,
    vendor_risk_db,
    Company_db,
)
from common.scoreUtils import res_dict, new_comp_data_prep, api_checker
from datetime import date


app = Flask(__name__)
app.config["ENV"] = "development"
app.config["DEBUG"] = False
app.config["TESTING"] = True
app.secret_key = "super secret key"
today = date.today()
data_mode = 0


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        req = request.form
        session["hostname"] = req["hostname"]
        session["company"] = req["company"]
        company = session.get("company")
        hostname = session.get("hostname")
        data = Company_db.find_one({"Company": company})
        if data == None:
            status = api_checker(company, hostname)
            if status == None:
                error_statement = "Please enter a valid company and hostname"
                return render_template("error.html", errorstatement=error_statement)
            elif status == True:
                error_statement = "Please type the company details again in 10 mins, we have added the company in the database and our AI is working on generating scores"
                # ID = new_comp_data_prep(company, hostname) - # for now I have stopped the new company creation flow 
                return render_template("error.html", errorstatement=error_statement)
        ID = data["ID"]
        comp_data = Company_db.find_one({"ID": ID})
        result = res_dict(comp_data["Company"], comp_data["Hostname"], data_mode, ID)
        result["Company"] = comp_data["Company"]
        result["hostname"] = comp_data["Hostname"]
        return render_template("index_new.html", data=result)
    return render_template("index.html")


@app.route("/companydetails")
def companydetails():
    hostname = session.get("hostname")
    data = get_data_from_current_db(predicted_website_db, hostname)
    if data:
        return render_template("companyDetails.html", data=data)
    return render_template("companyDetails.html")


@app.route("/scorehistory")
def scorehistory():
    data = list(vendor_risk_db.find({}))
    for item in data:
        item["Company"] = item["Company"].capitalize()
    return render_template("scorehistory.html", data=data)


@app.route("/scorehistory/<int:variable>")
def compScores(variable):
    comp_data = Company_db.find_one({"ID": variable})
    result = res_dict(comp_data["Company"], comp_data["Hostname"], data_mode, variable)
    result["Company"] = comp_data["Company"]
    result["hostname"] = comp_data["Hostname"]
    return render_template("index_new.html", data=result)


if __name__ == "__main__":
    app.run(debug=True)
