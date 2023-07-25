import datetime
import json

import jwt
import pandas as pd
from flask import Flask, jsonify, make_response, render_template, request
from flask_jwt_extended import (
    JWTManager,
    decode_token,
    jwt_required,
)
from common.database.sql_models import (
    ResultTable,
    RegisteredClientDataTable
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from passlib.hash import bcrypt
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

from common.constant_database_variables import (
    UPLOAD_DC_CSV_REQUIRED_COLS,
    UPLOAD_ENTERPRISE_VENDORS_CSV_REQUIRED_COLS,
)
from common.database.sql_create_connection import cyber_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from repository.sql_data_extraction_repo import CyberRepository
from repository.sql_cyber_repo.client_login import ClientLoginRepository
from common.database.sql_database_connection import CyberDatabase
from repository.sql_cyber_repo.client_repo import ClientRepository
from flask import Flask, render_template, request, session

cyber_db = CyberDatabase()  # create the database connection  -- Done

cyber_repo = CyberRepository(
    cyber_db.engine(), cyber_db.metadata())  # load the entire schema
sqlsession = Session(cyber_db.engine())  # opens the session with DB
Session = sessionmaker(bind=CyberDatabase().engine())
from common.database.database_utils import (
    get_data_from_current_db,
    predicted_website_db,
    vendor_risk_db,
    Company_db,
)
from common.scoreUtils import res_dict, new_comp_data_prep, api_checker
from datetime import date, datetime, timedelta

application = Flask(__name__)
application.secret_key = "your_secret_key"
Session = sessionmaker(bind=CyberDatabase().engine())
sess = Session()
api_secret_key = "api_secret_key"
application.config["JWT_SECRET_KEY"] = cyber_db.common_props()['jwt_secrets']['secretKey'] # loading jwt sec key from secrets manager. 
application.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
application.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=10)
application.config["JWT_ALGORITHM"] = "HS256"
application.config["JWT_TOKEN_LOCATION"] = ["headers"]
application.config["JWT_HEADER_NAME"] = "Authorization"
application.config["JWT_HEADER_TYPE"] = "Bearer"
limiter = Limiter(
    get_remote_address,
    app=application,
)
today = date.today()
data_mode = 0


jwt = JWTManager(application)


def check_required_cols_present(current_cols, required_cols):
    col_check_validation_status = len(current_cols) == len(required_cols)

    if col_check_validation_status:
        for col in required_cols:
            if col not in current_cols:
                col_check_validation_status = False
                break

    return col_check_validation_status


def check_auth_header(request):
    try:
        auth_header = request.headers["Authorization"]
        if not auth_header:
            return None, jsonify({"error": f"No authorization header found."}), 401
    except KeyError:
        return None, jsonify({"error": f"No authorization header found."}), 401

    token = auth_header.split(" ")[1]
    return token, None, 200


@application.route("/register", methods=["POST"])
@limiter.limit("4/minute", override_defaults=False)
def register():
    try:
        payload = request.get_json()
        if payload is None:
            return (
                jsonify(
                    {
                        "error": "Please provide domain_company_name, domain_name, email_id and password"
                    }
                ),
                400,
            )

        client_name = payload.get("client_name")
        domain_name = payload.get("domain_name")
        email_id = payload.get("email_id")
        password = payload.get("password")

        if not email_id or not password or not client_name or not domain_name:
            return (
                jsonify(
                    {
                        "error": "Please provide - client_name (ex: Amazon), domain_name (ex:amazon.com), email_id, password"
                    }
                ),
                400,
            )

        hashed_password = bcrypt.hash(password)
        result, status = ClientLoginRepository().registration(
            client_name=client_name,
            domain_name=domain_name,
            email_id=email_id,
            hashed_password=hashed_password,
        )

        if status == 200:
            return make_response(
                jsonify({"message": f"User {email_id} created successfully!"}), 201
            )
        elif status == 401:
            return make_response(
                jsonify({"error": f"Email id {email_id} already exists"}), 401
            )
        else:
            return_error = json.loads(result.data.decode("utf-8"))
            return make_response(jsonify({"error": return_error.get("error")}), status)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@application.route("/login", methods=["POST"])
@limiter.limit("3/minute", override_defaults=False)
def login():
    try:
        payload = request.get_json()
        if not payload:
            return (
                jsonify({"error": "Please provide domain_name, email_id and password"}),
                400,
            )

        if ("email_id" not in payload) or ("password" not in payload):
            return (
                jsonify(
                    {"error": "Please provide email_id and password and domain_name"}
                ),
                400,
            )

        email_id = payload.get("email_id")
        password = payload.get("password")
        result, status = ClientLoginRepository().client_login(
            email_id=email_id, plaintext_password=password
        )

        result_output = json.loads(result.data.decode("utf-8"))
        if status == 200:
            return make_response(
                jsonify(
                    {
                        "message": f"User {email_id} logged in successfully! Attached the token!",
                        "token": result_output["token"],
                    }
                ),
                201,
            )
        else:
            return make_response(jsonify({"error": result_output.get("error")}), status)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Need to update based on the admin and client level access
@application.route("/company/id", methods=["GET"])
@jwt_required()
def get_general_company_data_by_id():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    company_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().get_general_client_data(company_id=company_id)

        if len(all_rows) == 0:
            return (
                jsonify({"message": f"Data for company_id = {company_id} not found!"}),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request.{e}"}),
            500,
        )


# Need to update based on the admin and client level access
@application.route("/company/name/<string:company_name>", methods=["GET"])
def get_general_company_data_by_name(company_name):
    if not company_name:
        return (
            jsonify({"error": f"Please provide company_name!"}),
            500,
        )

    try:
        all_rows = ClientRepository().get_general_client_data(company_name=company_name)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {"message": f"Data for company_name = {company_name} not found!"}
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request.{e}"}),
            500,
        )


@application.route("/client-vendor-relationships/", methods=["GET"])
@jwt_required()
def get_client_vendor_relationships():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]
    try:
        all_rows = ClientRepository().get_client_relationship_data(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Relationship Data for client_id = {client_id} not found!"
                    }
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request.{e}"}),
            500,
        )


@application.route("/client/scores/self-score/", methods=["GET"])
@jwt_required()
def get_self_score_specific_client():
    print("HERE")
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().get_self_client_score(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {"message": f"Self score for client_id = {client_id} not found!"}
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request {e} ."}),
            500,
        )

@application.route("/update-dc-vendors/", methods=["POST"])
@application.route("/update-dc-vendors-technologies/", methods=["POST"])
@application.route("/upload-dc/", methods=["POST"])
@jwt_required()
def post_direct_client_and_technologies():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]
    if "file" not in request.files:
        return jsonify({"error": "Please provide CSV file"})

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No selected file"})

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a CSV file"})

    filename = secure_filename(file.filename)

    # Need to change this for proper server path
    file.save(f"client_uploaded_csv/{filename}")
    new_filename = f"client_uploaded_csv/{filename}"

    current_csv_cols = list(pd.read_csv(new_filename).columns)
    col_check_validation_status = check_required_cols_present(
        current_csv_cols, UPLOAD_DC_CSV_REQUIRED_COLS
    )

    if not col_check_validation_status:
        return (
            jsonify(
                {
                    "error": f"Please ensure columns {UPLOAD_DC_CSV_REQUIRED_COLS} are present in uploaded CSV! You can keep 'technologies' column empty as well!"
                }
            ),
            500,
        )

    try:
        ClientRepository().post_direct_client_technologies(client_id, new_filename)
        return jsonify({"message": f"File {file} uploaded successfully"})

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request. {e}"}),
            500,
        )


@application.route("/upload-enterprise/", methods=["POST"])
@jwt_required()
def post_enterprise_and_technologies():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]
    if "file" not in request.files:
        return jsonify({"error": "Please provide CSV file"})

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No selected file"})

    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a CSV file"})

    filename = secure_filename(file.filename)

    # Need to change this for proper server path
    file.save(f"client_uploaded_csv/{filename}")
    new_filename = f"client_uploaded_csv/{filename}"

    current_csv_cols = list(pd.read_csv(new_filename).columns)
    col_check_validation_status = check_required_cols_present(
        current_csv_cols, UPLOAD_ENTERPRISE_VENDORS_CSV_REQUIRED_COLS
    )

    if not col_check_validation_status:
        return (
            jsonify(
                {
                    "error": f"Please ensure columns {UPLOAD_ENTERPRISE_VENDORS_CSV_REQUIRED_COLS} are present in uploaded CSV!"
                }
            ),
            500,
        )

    try:
        ClientRepository().post_enterprise_vendor_technologies(client_id, new_filename)
        return jsonify({"message": f"File {file} uploaded successfully"})

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request. {e}"}),
            500,
        )


@application.route(
    "/client/scores/single-vendor/<string:input_vendor_list>", methods=["GET"]
)
@jwt_required()
def get_dc_single_vendor_score(input_vendor_list: str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set([input_vendor_list.split(",")[0]]))
        all_rows = ClientRepository().get_vendor_score(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found!"
                    }
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )
        
        
@application.route(
    "/client/scores/multiple-vendors/<string:input_vendor_list>", methods=["GET"]
)
@jwt_required()
def get_dc_multiple_vendor_score(input_vendor_list: str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set(input_vendor_list.split(",")))
        all_rows = ClientRepository().get_vendor_score(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found!"
                    }
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )




@application.route("/client/scores/all-vendors/", methods=["GET"])
@jwt_required()
def get_dc_all_vendors_score():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().get_all_vendor_score(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {"message": f"Client_id = {client_id} does not have any vendors!"}
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )

@application.route("/client/features/self-features/", methods=["GET"])
@jwt_required()
def get_self_features_specific_client():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().get_self_client_features(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {"message": f"Self Features for client_id = {client_id} not found!"}
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify({"error": f"An error occurred while processing the request {e} ."}),
            500,
        )


@application.route(
    "/client/features/single-vendor/<string:input_vendor_list>", methods=["GET"]
)
@jwt_required()
def get_dc_single_vendor_features(input_vendor_list: str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set([input_vendor_list.split(",")[0]]))
        all_rows = ClientRepository().get_vendor_features(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found!"
                    }
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )


@application.route(
    "/client/features/multiple-vendors/<string:input_vendor_list>", methods=["GET"]
)
@jwt_required()
def get_dc_multiple_vendor_features(input_vendor_list: str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set(input_vendor_list.split(",")))
        all_rows = ClientRepository().get_vendor_features(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found!"
                    }
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )


@application.route("/client/features/all-vendors/", methods=["GET"])
@jwt_required()
def get_dc_all_vendors_features():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().get_all_vendor_features(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {"message": f"Client_id = {client_id} does not have any vendors!"}
                ),
                404,
            )

        return jsonify(all_rows)

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )


@application.route("/client/delete/single-vendor/<string:input_vendor_list>", methods=["GET"])
@jwt_required()
def delete_client_single_vendor(input_vendor_list:str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set([input_vendor_list.split(",")[0]]))
        all_rows = ClientRepository().delete_vendors(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found! It maybe deleted already!"
                    }
                ),
                404,
            )

        return (
                jsonify(
                    {
                        "Deleted Vendors (Format=[company_name, domain_name])": all_rows
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )

@application.route("/client/delete/multiple-vendors/<string:input_vendor_list>", methods=["GET"])
@jwt_required()
def delete_client_multiple_vendor(input_vendor_list:str):
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        vendor_list = list(set(input_vendor_list.split(",")))
        all_rows = ClientRepository().delete_vendors(client_id, vendor_list)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendor={input_vendor_list} for client_id = {client_id} data not found! It maybe deleted already!"
                    }
                ),
                404,
            )

        return (
                jsonify(
                    {
                        "Deleted Vendors (Format=[company_name, domain_name])": all_rows
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )
        
        
@application.route("/client/delete/all-vendors/", methods=["GET"])
@jwt_required()
def delete_client_all_vendors():
    token, error, status_code = check_auth_header(request)

    if error or not token:
        return error, status_code

    decoded_token = decode_token(token)["sub"]
    client_id = decoded_token["client_id"]

    try:
        all_rows = ClientRepository().delete_all_vendors(client_id)

        if len(all_rows) == 0:
            return (
                jsonify(
                    {
                        "message": f"Vendors for client_id = {client_id} data not found! It maybe deleted already!"
                    }
                ),
                404,
            )

        return (
                jsonify(
                    {
                        "Deleted Vendors (Format=[company_name, domain_name])": all_rows
                    }
                ),
                200,
            )

    except Exception as e:
        return (
            jsonify(
                {"error": f"An error occurred while processing the request - {e} ."}
            ),
            500,
        )


@application.route("/", methods=["POST", "GET"])
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
        
        else:
            ID = data["ID"]
            comp_data = Company_db.find_one({"ID": ID})
            if not comp_data:
                error_statement = "Some issue on backend!"
                return render_template("error.html", errorstatement=error_statement)

            result = res_dict(comp_data["Company"], comp_data["Hostname"], data_mode, ID)
            result["Company"] = comp_data["Company"]
            result["hostname"] = comp_data["Hostname"]
            return render_template("index_new.html", data=result)
    return render_template("index.html")


@application.route("/companydetails")
def companydetails():
    hostname = session.get("hostname")
    data = get_data_from_current_db(predicted_website_db, hostname)
    if data:
        return render_template("companyDetails.html", data=data)
    return render_template("companyDetails.html")


@application.route("/scorehistory")
def scorehistory():
    data = list(vendor_risk_db.find({}))
    for item in data:
        item["Company"] = item["Company"].capitalize()
    return render_template("scorehistory.html", data=data)


@application.route("/scorehistory/<int:variable>")
def compScores(variable):
    comp_data = Company_db.find_one({"ID": variable})
    if not comp_data:
        error_statement = "Some issue on backend!"
        return render_template("error.html", errorstatement=error_statement)

    result = res_dict(comp_data["Company"], comp_data["Hostname"], data_mode, variable)
    result["Company"] = comp_data["Company"]
    result["hostname"] = comp_data["Hostname"]
    return render_template("index_new.html", data=result)

@application.route("/all_company_scores")
def result_data():
    subquery = sqlsession.query(ResultTable.vendor_client_row_id, func.max(
        ResultTable.datetime_executed).label('latest')).group_by(ResultTable.vendor_client_row_id).subquery()
    Resultdata = sqlsession.query(ResultTable).join(subquery, ResultTable.vendor_client_row_id ==
                                                    subquery.c.vendor_client_row_id).filter(ResultTable.datetime_executed == subquery.c.latest).all()
    result = []
    for item in Resultdata:
        RegisteredClientData = sqlsession.query(RegisteredClientDataTable).filter(
            RegisteredClientDataTable.client_id == item.vendor_client_row_id
        ).first()

        if (RegisteredClientData is not None):
            d = datetime.strptime(
                str(item.datetime_executed), '%Y-%m-%d %H:%M:%S.%f')
            company_data = {
                'name': RegisteredClientData.client_name,
                'nvd_score': round(float(item.nvd_score), 5) if item.nvd_score else '-',
                'css_score': round(float(item.css_score), 5) if item.css_score else '-',
                'master_score': round(float(item.master_score), 5) if item.master_score else '-',
                'breach_risk_score': round(float(item.breach_risk_score), 5) if item.nvd_score else '-',
                'bss_score': round(float(item.bss_score), 5) if item.bss_score else '-',
                'bss': round(float(item.bss), 5) if item.bss else '-',
                'calculated_on': f"{d.day}-{d.month}-{d.year}"
            }
            result.append(company_data)
    return render_template("all_company_scores.html", data=result)

if __name__ == "__main__":
    application.run(debug=True)
