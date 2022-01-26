import csv
import slcsp


def test_csv_to_df():
    test_file = "_test_.csv"
    row_count = 10
    with open(test_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["c1", "c2"])
        for i in range(10):
            writer.writerow([i, 2*i])

    df = slcsp.csv_to_df(test_file)
    assert df.size == row_count*2
