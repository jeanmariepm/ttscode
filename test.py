import csv
import slcsp


def test_csv_to_dict():
    test_file = "_test_.csv"
    row_count = 10
    with open(test_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["c1", "c2"])
        for i in range(10):
            writer.writerow([i, 2*i])

    rows = slcsp.csv_to_dict(test_file)
    assert len(rows) == row_count
    print(rows[0])
    assert rows[0]['c1'] == '0'
    assert rows[9]['c2'] == str(2*(row_count-1))
