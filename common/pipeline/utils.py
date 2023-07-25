import os

import pandas as pd
import yaml

from common.constant_variables import FILL_WITH_SPECIFIC_DATE, FILL_WITH_NA, DROP_ROWS, DROP_ROWS_WEBSITE_STATE, \
    SCORE_FEATURES
from common.enums import StageType


def read_config_file():
    """
    Read the config.yaml file

    """
    with open(f'config/config.yaml') as file:
        config_data = yaml.safe_load(file)
    return config_data


def read_training_data_from_files():
    """
    Read files from datasets folder and label them
    """
    config = read_config_file()
    dataset_paths = config['training']['labeled_datasets_path_dir']
    labeled_0_path = f'{dataset_paths}/0/'
    labeled_1_path = f'{dataset_paths}/1/'

    # Contains all non-breached (files_0) files and breached files (files_1)
    files_0 = os.listdir(labeled_0_path)
    files_1 = os.listdir(labeled_1_path)

    df_0 = pd.DataFrame()
    df_1 = pd.DataFrame()

    for file in files_0:
        path = f'{labeled_0_path}{file}'
        temp_df = pd.read_csv(path)

        # Label = 0
        temp_df = process_read_file(temp_df, 0)
        df_0 = pd.concat([df_0, temp_df], axis=0)

    for file in files_1:
        path = f'{labeled_1_path}{file}'
        temp_df = pd.read_csv(path)

        # Label = 1
        temp_df = process_read_file(temp_df, 1)
        df_1 = pd.concat([df_1, temp_df], axis=0)

    df = pd.concat([df_0, df_1], axis=0).sort_values('hostname').reset_index(drop=True)
    return df


def process_read_file(df, label):
    """
    Method removes unnamed columns, renames all columns in a defined format (lowercase)

    """

    ndf = df.copy()
    ndf = ndf.loc[:, ~ndf.columns.str.contains('^Unnamed')]

    ndf.columns = ndf.columns.str.replace('(', '', regex=True) \
        .str.replace(')', '', regex=True) \
        .str.replace('-', '_', regex=True) \
        .str.replace(' ', '_', regex=True) \
        .str.lower().str.strip()

    ndf = ndf.applymap(lambda s: s.lower() if type(s) == str else s)
    ndf = ndf.rename(columns={"organization_name": "company", "website": "hostname"})

    ndf = ndf.dropna(how='all').reset_index(drop=True)

    ndf['label'] = label

    return ndf


def read_data_for_training():
    """
    Manually reading all files and labelling them. DEPRECATED METHOD
    """

    df1 = pd.read_csv('datasets/breached1.csv')
    df2 = pd.read_csv('datasets/breached3.csv')
    df3 = pd.read_csv('datasets/breached4.csv')
    ndf = pd.read_csv('datasets/non_breached.csv')

    df1 = df1.loc[:, ~df1.columns.str.contains('^Unnamed')]
    df2 = df2.loc[:, ~df2.columns.str.contains('^Unnamed')]
    df3 = df3.loc[:, ~df3.columns.str.contains('^Unnamed')]
    ndf = ndf.loc[:, ~ndf.columns.str.contains('^Unnamed')]

    bdf = pd.concat([df1, df2, df3])

    bdf.columns = bdf.columns.str.replace('(', '', regex=True) \
        .str.replace(')', '', regex=True) \
        .str.replace('-', '_', regex=True) \
        .str.replace(' ', '_', regex=True) \
        .str.lower().str.strip()

    ndf.columns = ndf.columns.str.replace('(', '', regex=True) \
        .str.replace(')', '', regex=True) \
        .str.replace('-', '_', regex=True) \
        .str.replace(' ', '_', regex=True) \
        .str.lower().str.strip()

    bdf = bdf.applymap(lambda s: s.lower() if type(s) == str else s)
    ndf = ndf.applymap(lambda s: s.lower() if type(s) == str else s)
    ndf = ndf.rename(columns={"organization_name": "company", "website": "hostname"})

    bdf = bdf.dropna(how='all').reset_index(drop=True)
    ndf = ndf.dropna(how='all').reset_index(drop=True)

    bdf['label'] = 1
    ndf['label'] = 0

    final_df = pd.concat([bdf, ndf])
    return final_df


def read_data_for_predictions(name_of_csv):
    """
    Read files to make predictions and process it
    """
    df = pd.read_csv(name_of_csv)
    df = df.dropna(how='all').reset_index(drop=True)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = df.columns.str.replace('(', '', regex=True) \
        .str.replace(')', '', regex=True) \
        .str.replace('-', '_', regex=True) \
        .str.replace(' ', '_', regex=True) \
        .str.lower().str.strip()

    df = df.applymap(lambda s: s.lower() if type(s) == str else s)
    df = df.rename(columns={"organization_name": "company", "website": "hostname"})
    return df


def data_cleaning(dfx, stage_type):
    """
    Preprocess the DF.

    """
    df = dfx.copy()

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.applymap(lambda s: s.lower() if type(s) == str else s)
    df = df.rename(columns={"organization_name": "company", "website": "hostname"})

    df[FILL_WITH_NA] = df[FILL_WITH_NA].fillna('UNKNOWN')
    df[FILL_WITH_SPECIFIC_DATE] = df[FILL_WITH_SPECIFIC_DATE].fillna('01-01-2013')
    df[FILL_WITH_SPECIFIC_DATE] = df[FILL_WITH_SPECIFIC_DATE].apply(
        lambda x: pd.to_datetime(x, errors='coerce', format='%Y-%m-%d'))
    df = df.fillna(0)

    if stage_type == StageType.START_TRAINING:
        for i in DROP_ROWS:
            df = df[~(df['dp_matching_fields'] == i)]

        for i in DROP_ROWS_WEBSITE_STATE:
            df = df[~(df['dp_website_state'] == i)]

    df = df.reset_index(drop=True)

    for i in df.columns:
        df[i] = pd.to_numeric(df[i], errors='ignore')

    for col in df.columns:
        if df[col].dtypes == 'float64':
            df[col] = df[col].fillna(0)

    df = df.reset_index(drop=True)
    return df


def perform_feature_selection(dfx, stage_type):
    """
    Perform feature selection. Add 2 methods for row recognition.

    """
    df = dfx.copy()

    SCORE_FEATURES_TEMP = SCORE_FEATURES.copy()
    SCORE_FEATURES_TEMP.append('company')
    SCORE_FEATURES_TEMP.append('hostname')
    if stage_type == StageType.START_TRAINING:
        SCORE_FEATURES_TEMP.append('label')

    df = df[SCORE_FEATURES_TEMP]
    return df


def training_data_processing_pipeline():
    """
    Pipeline for Training Data
    """
    stage_type = StageType.START_TRAINING
    df = read_training_data_from_files()
    df = data_cleaning(df, stage_type)
    df = perform_feature_selection(df, stage_type)
    return df


def prediction_data_processing_pipeline(name_of_csv):
    """
    Pipeline for making predictions
    """
    stage_type = StageType.START_PREDICTIONS
    df = read_data_for_predictions(name_of_csv)
    df = data_cleaning(df, stage_type)
    df = perform_feature_selection(df, stage_type)
    return df
