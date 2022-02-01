import sys
from os.path import exists
import argparse
import pandas as pd


def get_filenames():
    """
    Collect filenames as input

    Return:
      plans, zips, slcsp
    """
    parser = argparse.ArgumentParser(description='Accept file names.')
    parser.add_argument('-p', '--plans',
                        help='csv file with all the health plans in the U.S. on the marketplace',
                        required=True)
    parser.add_argument('-z', '--zips',
                        help='''
                        csv file with a mapping of ZIP Code to county/counties & rate area(s)
                        ''',
                        required=True)
    parser.add_argument('-s', '--slcsp',
                        help='csv file wit the ZIP codes that need to be processed',
                        required=True)
    args = parser.parse_args()
    for path in (args.plans, args.zips, args.slcsp):
        if not exists(path):
            print(f'Error: {path} is not a valid file name')
            parser.print_help()
            sys.exit(9)
    return (args.plans, args.zips, args.slcsp)


def csv_to_df(filename: str):
    """
    Read a csv file and convert to a pandas dataframe
    path (str): The path to a csv file

    Returns:
      pandas Dataframe
    """
    return pd.read_csv(filename)


def get_ref_plans(plans: pd.DataFrame):
    """
    Compute the refeence plans to be used for SLCSP

    Select only the silver plans.
    Rank them in ascending rate for each state and area
    Pick the second lowest from the ranked plans
    Pick the only (lowest) plan if there is no second-ranked plan
    Merge the picked plans

    Params:
      plans Pandas dataframe that needs to includ state, rate_area and rate

    Returns:
      ref_plans: Pandas dataframe that has exactly one rate per state and rate area
    """
    COLS_TO_RETURN = ['state', 'rate_area', 'rate']
    silver_filter = plans['metal_level'] == 'Silver'
    silver_plans = plans[silver_filter]
    silver_plans = silver_plans[COLS_TO_RETURN]
    ranked_selver_plans = silver_plans.assign(
        rn=silver_plans.sort_values(["rate"])
        .groupby(['state', 'rate_area'])
        .cumcount() + 1
    ).sort_values(['state', 'rate_area', "rn"])
    second_lowest = ranked_selver_plans[
        ranked_selver_plans['rn'] == 2]

    # lowest = ranked_silver minus plans with many rates
    tmp = pd.merge(ranked_selver_plans, second_lowest, indicator=True,
                   on=['state', 'rate_area'], how='outer',
                   suffixes=[None, '_y'])
    lowest = tmp[tmp['_merge'] == 'left_only']
    return pd.concat([lowest, second_lowest],
                     ignore_index=True)[COLS_TO_RETURN]


def get_zip_plans(zips: pd.DataFrame, ref_plans: pd.DataFrame):
    """
    Compute a ref plan for each zipcode

    Drop zipcode if it maps to more than one state and rate_area
    Params:
    zips dataframe mapping zipcode to state and rate_area
    refs_plan dataframe mapping state and rate_area to rate

    Returns:
    zip_plans dataframe mapping zipcode to rate
    """
    zips_df = zips[['zipcode', 'state', 'rate_area']] \
        .drop_duplicates(keep=False)
    zip_plans = pd.merge(zips_df, ref_plans)
    return zip_plans[['zipcode', 'rate']]


if __name__ == "__main__":
    fnames = get_filenames()
    plans, zips, slcsp = (csv_to_df(fname) for fname in fnames)

    try:
        ref_plans = get_ref_plans(plans)
    except KeyError as err:
        print(err, file=sys.stderr)
        print('Invalid plan file. Must be a csv file with state, rate_area and rate')
        sys.exit(1)
    # print(ref_plans)

    try:
        zip_plans = get_zip_plans(zips, ref_plans)
    except KeyError as err:
        print(err, file=sys.stderr)
        print('Invalid zips file. Must be a csv file with zipcode, state, rate_area')
        sys.exit(1)
    # print(zip_plans)

    slcsp_out = slcsp.merge(zip_plans, on='zipcode', how='left').rename(
        columns={'rate_y': 'rate'})[['zipcode', 'rate']]
    slcsp_out.to_csv(sys.stdout, index=False)
