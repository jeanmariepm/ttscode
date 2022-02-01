import csv
import os
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from slcsp import slcsp

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)
DATA_DIR = os.path.join(BASE_DIR, 'data')


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
