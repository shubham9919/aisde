import pandas as pd
import numpy as np


class CustomEncoderListData:
    def __init__(self, add_unknowns=False):
        self.all_values = dict()
        self.df = None
        self.columns_fitted = None
        self.add_unknowns = add_unknowns
        self.fitted = False

    def fit(self, dfx):

        if type(dfx) == pd.core.series.Series:
            dfx = dfx.to_frame()

        self.perform_checks(dfx, check_num=3)
        self.df = dfx.copy()
        self.columns_fitted = set(self.df.columns)
        self.df = self.preprocessing_fit_columns(self.df)
        self.fitted = True
        return self

    def transform(self, dfx):
        if type(dfx) == pd.core.series.Series:
            dfx = dfx.to_frame()

        self.perform_checks(dfx, check_num=3)
        self.perform_checks(check_num=1)
        self.perform_checks(df=dfx, check_num=2)

        df = dfx.copy()
        df = self.preprocess_transform_data(df)

        for col in df.columns:

            temp_values = set(
                [val for value_list in df[col].values for val in value_list]
            )
            not_found_in_fitted = temp_values - self.all_values[col]

            for val in sorted(self.all_values[col]):
                new_name = f"{col}_{val}"
                df[new_name] = 0
                df[new_name] = df[[col, new_name]].apply(
                    lambda x: 1 if val in x[0] else 0, axis=1
                )

            for val in sorted(not_found_in_fitted):
                print(not_found_in_fitted)
                new_name = f"{col}_UNKNOWN"
                if self.add_unknowns:
                    df.loc[df[col].apply(lambda x: val in x), new_name] += 1
                else:
                    df.loc[df[col].apply(lambda x: val in x), new_name] = 1

        return df

    def fit_transform(self, dfx):
        self.fit(dfx)
        df = self.transform(dfx)
        return df

    def fit_dataframe(self):
        pass

    def inverse_transform(self):
        pass

    def fill_missing_values(self):
        pass

    def perform_checks(self, df=None, check_num=None):

        # Check 1
        # Check if the encoder is fitted or not
        if check_num == 1 or None:
            if not self.fitted:
                raise Exception("The Encoder is not fitted yet. Please fit it.")

        # Check 2
        # Check if all columns of To-Be-Transformed are fitted or not
        if check_num == 2 or None:
            new_cols = set(df.columns)
            remaining_cols = new_cols - self.columns_fitted

            if remaining_cols:
                raise ValueError(
                    f"The New Dataframe contains columns that were not fitted. "
                    f"\n Columns {remaining_cols} are not fitted. "
                    f"\n Columns fitted are {self.columns_fitted} "
                )

        # Check 3
        # Check if the type of input is DF or Series. If not, raise error
        if check_num == 3 or None:
            if (type(df) != pd.core.frame.DataFrame) and (
                type(df) != pd.core.series.Series
            ):
                raise TypeError(
                    f"The type of input should be DataFrame and not {type(df)}"
                )

    def preprocessing_fit_columns(self, dfx):
        df = dfx.copy()
        df = (
            df.replace(np.NaN, "UNKNOWN")
            .fillna("UNKNOWN")
            .replace(np.nan, "UNKNOWN")
            .replace("nan", "UNKNOWN")
        )
        # Convert all Values to list of vals
        df = df.apply(lambda x: x.apply(lambda y: y if type(y) == list else [y]))

        # Store all unique values to dict
        for col in df.columns:
            temp_values = set(
                [val for value_list in df[col].values for val in value_list]
            )
            temp_values.add("UNKNOWN")
            self.all_values[col] = temp_values

        return df

    @staticmethod
    def preprocess_transform_data(dfx):
        df = dfx.copy()
        df = (
            df.replace(np.NaN, "UNKNOWN")
            .fillna("UNKNOWN")
            .replace(np.nan, "UNKNOWN")
            .replace("nan", "UNKNOWN")
        )
        df = df.apply(lambda x: x.apply(lambda y: y if type(y) == list else [y]))

        return df
