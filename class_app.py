import time

from common.pipeline.utils import training_data_processing_pipeline, prediction_data_processing_pipeline
from prediction.prediction_repository import MakePredictions
from training.training_repositories import TrainingModels


class App:
    def __init__(self, filename=None):
        # Read name of the file
        self.filename = filename
        self.df = None

    def make_predictions(self):
        self.df = prediction_data_processing_pipeline(self.filename)
        MakePredictions(self.df)

    def start_training(self):
        # Preprocess DF (Reading, Cleaning and feature selection)
        self.df = training_data_processing_pipeline()
        TrainingModels(cleaned_df=self.df)

    def make_predictions_time(self):
        start_time = time.time()
        self.make_predictions()
        total_time = time.time() - start_time
        print(f'Total Time for Prediction (Rows = {self.df.shape[0]}) took -- {total_time} secs')
        return total_time

    def start_training_time(self):
        start_time = time.time()
        self.start_training()
        total_time = time.time() - start_time
        print(f'Total Time for Training (Rows = {self.df.shape[0]}) took -- {total_time} secs')
        return total_time
