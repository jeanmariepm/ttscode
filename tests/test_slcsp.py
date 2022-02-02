import csv
import os
import sys
from pathlib import Path
from unittest.mock import patch
from weakref import ref
import pytest
import pandas as pd

from slcsp import slcsp

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)
DATA_DIR = os.path.join(BASE_DIR, 'data')


@pytest.fixture
def load_test_plans():
    '''
    Create a plans df to test scenarios
    '''
    df = pd.DataFrame(columns=('metal_level', 'state', 'rate_area', 'rate'))
    df.loc[0] = ['Silver', 'AZ', 1, 100.1]
    df.loc[1] = ['Silver', 'AZ', 1, 100.5]
    df.loc[2] = ['Silver', 'AZ', 1, 200.1]
    df.loc[3] = ['Gold', 'AZ', 1, 73.1]
    df.loc[3] = ['Silver', 'KY', 1, 73.1]

    return df


@pytest.fixture
def load_test_zips():
    '''
    Create a zips df to test scenarios
    '''
    df = pd.DataFrame(columns=('zipcode', 'state', 'rate_area'))
    df.loc[0] = [100001, 'AZ', 1]
    df.loc[1] = [200001, 'KY', 1]
    df.loc[2] = [200002, 'KY', 2]
    df.loc[3] = [200002, 'KY', 2]

    return df


@pytest.fixture
def load_test_slcsp():
    '''
    Create a slcsp df to test scenarios
    '''
    df = pd.DataFrame(columns=('zipcode', 'rate'))
    df.loc[0] = [100001, None]
    df.loc[1] = [200001, None]
    df.loc[2] = [200002, None]
    df.loc[3] = [200003, None]

    return df


def test_csv_to_df():
    '''
    Ensure file can be read into a pandas df
    '''

    test_file = f"{TMP_DIR}/_test_.csv"
    row_count = 10
    with open(test_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["c1", "c2"])
        for i in range(10):
            writer.writerow([i, 2*i])

    df = slcsp.csv_to_df(test_file)
    assert df.size == row_count*2


@patch('sys.argv', ['slcsp -z zf -s sf -p pf'][0].split())
def test_get_filenames_with_bad_files():
    with pytest.raises(SystemExit):
        slcsp.get_filenames()


@patch('sys.argv', [
    f'slcsp -z {DATA_DIR}/zips.csv -s {DATA_DIR}/slcsp.csv -p {DATA_DIR}/plans.csv'
][0].split())
# Assume files rae in the data folder
def test_get_filenames_with_good_files():
    slcsp.get_filenames()


def test_get_ref_plans_returns_second_for_AZ_1(load_test_plans):
    ref_plans = slcsp.get_ref_plans(load_test_plans)

    AZ_1_FILTER = (ref_plans['state'] == 'AZ') & (ref_plans['rate_area'] == 1)
    result = ref_plans.loc[AZ_1_FILTER].iloc[0]['rate']
    assert result == 100.5


def test_get_ref_plans_returns_only_for_KY_1(load_test_plans):
    ref_plans = slcsp.get_ref_plans(load_test_plans)
    KY_1_FILTER = (ref_plans['state'] == 'KY') & (ref_plans['rate_area'] == 1)
    result = ref_plans.loc[KY_1_FILTER].iloc[0]['rate']
    assert result == 73.1


def test_get_zip_plans_for_good_zips(
        load_test_zips, load_test_plans):
    ref_plans = slcsp.get_ref_plans(load_test_plans)
    zip_plans = slcsp.get_zip_plans(load_test_zips, ref_plans)
    KY_1_FILTER = zip_plans['zipcode'] == 200001
    result = zip_plans.loc[KY_1_FILTER].iloc[0]['rate']
    assert result == 73.1


def test_get_zip_plans_for_ambiguous_zips(
        load_test_zips, load_test_plans):
    ref_plans = slcsp.get_ref_plans(load_test_plans)
    zip_plans = slcsp.get_zip_plans(load_test_zips, ref_plans)
    KY_2_FILTER = zip_plans['zipcode'] == 200002
    result = zip_plans.loc[KY_2_FILTER]
    assert len(result) == 0


def test_get_plans_for_input(
        load_test_zips, load_test_plans, load_test_slcsp):
    ref_plans = slcsp.get_ref_plans(load_test_plans)
    zip_plans = slcsp.get_zip_plans(load_test_zips, ref_plans)
    result = slcsp.get_plans_for_inout(load_test_slcsp, zip_plans)
    assert len(result) == 4
    assert result['rate'].isnull().sum() == 2
