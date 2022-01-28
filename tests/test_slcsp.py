import csv
import os
from pathlib import Path

from slcsp import slcsp

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)


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
