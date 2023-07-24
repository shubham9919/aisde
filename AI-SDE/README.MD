========================================================================================================
Steps to run the Flask app:
========================================================================================================

1. Upload all the json files inside the DB folder to a mongoDB database as seperate collections.(try to create the database with the name 'Cyber')
	- Note: Make sure that you whitelist your ip address before doing any mongo DB operation

2. Update your mongoDB 'uri' in the config/config.yaml file.(replace the 'uri' key with your MongoDB 'uri' value)

2. Create a virtual envoirment and install the requirements.txt

	python -m venv "venv_name" [replace venv_name with your desired name]
	pip install -r requirements.txt
	.\<replace venv_name with your desired virtual environment name>\Scripts\activate


3. For running the flask app, type 'flask run' in the terminal
	- Go to http://127.0.0.1:5000/

========================================================================================================
Documentation:
========================================================================================================

1. Documentation for BSS:
	- https://visionbox-ai.atlassian.net/wiki/spaces/VS/pages/203456513/Brand+Sentiment+Score+BSS+using+GDELT

2. Documentation for API usage and cost statistics
	- https://visionbox-ai.atlassian.net/wiki/spaces/VS/pages/212467713/Cyber+Project+API+and+Cost+Statistics

========================================================================================================
Project info
========================================================================================================
All the information about this project is available under the folder notes on file Cyber_info.txt