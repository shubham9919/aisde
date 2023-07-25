import pickle
from datetime import datetime

import pandas as pd

from common.pipeline.utils import read_config_file


class MakePredictions:
    def __init__(self, cleaned_df):
        self.df = cleaned_df
        self.output_df = None
        self.xgb_model = None
        self.name_df = self.df[["company", "hostname"]].copy()
        self.prediction_pipeline()

    def pre_prediction_process_columns(self):
        self.df = self.df.drop(["company", "hostname"], axis=1)

    def post_prediction_process_columns(self):
        self.output_df = pd.concat(
            [
                self.name_df,
                self.df[["Breach_Possibility", "Breach_Possibility_Probability"]],
            ],
            axis=1,
        )
        self.output_df.loc[
            self.output_df["Breach_Possibility"] == 1, "Breach_Possibility"
        ] = "High Possibility"
        print(self.output_df)

    def read_model_from_file(self):
        config = read_config_file()
        location_model = config["training"]["model_path"]
        model_file_name = config["training"]["model_name"]
        location_with_file = location_model + "/" + model_file_name
        self.xgb_model = pickle.load(open(location_with_file, "rb"))

    def make_predictions(self):
        y_pred_proba = self.xgb_model.predict_proba(self.df)[:, 1]
        y_pred = self.xgb_model.predict(self.df)

        self.df["Breach_Possibility_Probability"] = y_pred_proba
        self.df["Breach_Possibility"] = y_pred

    def save_to_csv(self):
        config = read_config_file()
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        location_to_save_predicted_files = config["prediction"][
            "prediction_reports_path_dir"
        ]
        name_predicted_file = f"predictions_{current_time}.csv"
        location_with_predicted_file = (
            location_to_save_predicted_files + "/" + name_predicted_file
        )
        self.output_df.to_csv(location_with_predicted_file)
        print(f"File has been saved to {location_with_predicted_file}")

    def prediction_pipeline(self):
        print("Started Prediction")
        self.read_model_from_file()
        self.pre_prediction_process_columns()
        self.make_predictions()
        self.post_prediction_process_columns()
        self.save_to_csv()
        print("Predictions Finished!")


class MakePredictionsFlask:
    def __init__(self, cleaned_df):
        self.df = cleaned_df
        self.output_df = None
        self.xgb_model = None
        self.name_df = self.df[["company", "hostname"]].copy()
        self.prediction_pipeline()

    def pre_prediction_process_columns(self):
        self.df = self.df.drop(["company", "hostname"], axis=1)

    def post_prediction_process_columns(self):
        self.output_df = pd.concat(
            [
                self.name_df,
                self.df[["Breach_Possibility", "Breach_Possibility_Probability"]],
            ],
            axis=1,
        )
        self.output_df.loc[
            self.output_df["Breach_Possibility"] == 1, "Breach_Possibility"
        ] = "High Possibility"

    def read_model_from_file(self):
        config = read_config_file()

        location_model = config["training"]["model_path"]
        model_file_name = config["training"]["model_name"]
        location_with_file = location_model + "/" + model_file_name
        self.xgb_model = pickle.load(open(location_with_file, "rb"))

    def make_predictions(self):
        y_pred_proba = self.xgb_model.predict_proba(self.df)[:, 1]
        y_pred = self.xgb_model.predict(self.df)

        self.df["Breach_Possibility_Probability"] = y_pred_proba
        self.df["Breach_Possibility"] = y_pred

    def save_to_csv(self):
        config = read_config_file()
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        location_to_save_predicted_files = config["prediction"][
            "prediction_reports_path_dir"
        ]
        name_predicted_file = f"predictions_{current_time}.csv"
        location_with_predicted_file = (
            location_to_save_predicted_files + "/" + name_predicted_file
        )
        self.output_df.to_csv(location_with_predicted_file)
        print(f"File has been saved to {location_with_predicted_file}")

    def prediction_pipeline(self):
        self.read_model_from_file()
        self.pre_prediction_process_columns()
        self.make_predictions()
        return [
            self.df["Breach_Possibility_Probability"][0],
            self.df["Breach_Possibility"][0],
        ]

    def get_preds(self):
        return [
            self.df["Breach_Possibility_Probability"][0],
            self.df["Breach_Possibility"][0],
        ]

