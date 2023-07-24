import pickle

import xgboost as xgb
from sklearn.metrics import accuracy_score, auc
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split

from common.pipeline.utils import read_config_file


class TrainingModels:
    def __init__(self, cleaned_df):
        self.df = cleaned_df
        self.x_train, self.x_test, self.y_train, self.y_test = None, None, None, None
        self.xgb_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42, use_label_encoder=False)
        self.training_pipeline()

    def split_to_train_test(self):
        x = self.df.drop(['label', 'company', 'hostname'], axis=1)
        y = self.df['label']

        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(x, y, test_size=0.33, random_state=42)
        return self.x_train, self.x_test, self.y_train, self.y_test

    def model_fitting(self):
        self.xgb_model.fit(self.x_train, self.y_train)

    def test_model_results(self):
        y_pred = self.xgb_model.predict(self.x_test)
        score = accuracy_score(self.y_test, y_pred) * 100

        probabilities = self.xgb_model.predict_proba(self.x_test)[:, 1:].reshape(-1, )
        precision, recall, thresholds = precision_recall_curve(self.y_test, probabilities)
        area = auc(recall, precision) * 100

        if score < 80 or area < 80:
            print("--------------------------------")
            print(f"NOT A GOOD MODEL as SCORE: {score} and AREA AU PR: {area}")
            print("--------------------------------")
        else:
            print("--------------------------------")
            print(f"SEEMS A GOOD MODEL as SCORE: {score} and AREA AU PR: {area}")
            print("--------------------------------")

    def save_model_to_file(self):
        config = read_config_file()

        location_model = config['training']['model_path']
        model_file_name = config['training']['model_name']
        location_with_file = location_model + '/' + model_file_name

        pickle.dump(self.xgb_model, open(location_with_file, "wb"))
        print(f'Model File has been saved to {location_with_file}')

    def training_pipeline(self):
        self.split_to_train_test()
        self.model_fitting()
        self.test_model_results()
        self.save_model_to_file()
        print('Training Finished!')
