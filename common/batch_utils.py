from datetime import datetime, date, timedelta

import pandas as pd

from common.api_utils import get_website_data_from_api, process_data
from common.database.database_utils import predicted_website_db, insert_data_in_db, website_db, batch_db
from common.enums import BatchType
from common.pipeline.utils import read_config_file

config = read_config_file()


def get_old_hostnames_date_based(current_db):
    total_documents = current_db.find({})
    scanned_hostnames = set()

    old_hostnames = set()
    for row in total_documents:
        scanned_hostnames.add(row['hostname'])
        predicted_date = datetime.strptime(f'{row["date_executed"]}', '%Y-%m-%d').date()
        today_buffer = date.today() - timedelta(config['batch']['batch_past_days'])

        if today_buffer > predicted_date:
            old_hostnames.add(row['hostname'])

    return list(old_hostnames), list(scanned_hostnames)


def get_all_old_hostnames(current_db):
    total_documents = current_db.find({})
    old_hostnames = set([row['hostname'] for row in total_documents])
    return list(old_hostnames), list(old_hostnames)


def get_hostnames_from_df(filename):
    if not filename:
        raise Exception(f'Please Input Valid Filename with Location. {filename} is NOT VALID!')
    hostnames = pd.read_csv(filename)
    all_hostnames = set(hostnames['hostname'])
    return list(all_hostnames), list(all_hostnames)


def run_batch(based_on='DATE_BASED', filename=None):
    if based_on == BatchType.PREDICTED_DATE_BASED.value:
        to_be_updated_hostnames, scanned_hostnames = get_old_hostnames_date_based(predicted_website_db)
    elif based_on == BatchType.PREDICTED_ALL_HOSTNAMES.value:
        to_be_updated_hostnames, scanned_hostnames = get_all_old_hostnames(predicted_website_db)
    elif based_on == BatchType.CRAWLED_WEB_DATE_BASED.value:
        to_be_updated_hostnames, scanned_hostnames = get_old_hostnames_date_based(website_db)
    elif based_on == BatchType.CRAWLED_WEB_ALL_HOSTNAMES.value:
        to_be_updated_hostnames, scanned_hostnames = get_all_old_hostnames(website_db)
    elif based_on == BatchType.DATAFRAME_BASED.value:
        to_be_updated_hostnames, scanned_hostnames = get_hostnames_from_df(filename)
    else:
        raise Exception(f'{based_on} is INVALID Batch Mode. Please use one of {[e.value for e in BatchType]}')

    data = dict()
    for hostname in to_be_updated_hostnames:
        data['hostname'] = hostname
        response = get_website_data_from_api(data)
        if response['status'] == 200:
            api_data = response['output']['data']
            api_data['date_executed'] = str(date.today())
            response_with_features = process_data(api_data)
            insert_data_in_db(website_db, api_data)
            insert_data_in_db(predicted_website_db, response_with_features)
        else:
            print('Issue with API or Hostname not found')

    today_datetime = str(datetime.now())
    batch_db.insert_one({'batch_run_date': today_datetime,
                         'batch_mode': based_on,
                         'total_scanned_hosts': len(scanned_hostnames),
                         'total_updated_hosts': len(to_be_updated_hostnames),
                         'scanned_hostnames': scanned_hostnames,
                         'updated_hostnames': to_be_updated_hostnames})
