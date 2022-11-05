# -----------------------------------------------------------------------------
# rate nordic stocks by metrics and save scores + metrics to csv
#
# Torjus Nilsen, Drammen, Norway
# email tornil1996@hotmail.com
# -----------------------------------------------------------------------------

# standard lib
import csv
from pathlib import Path

# data
import numpy as np
import pandas as pd

# finance api
import yfinance as yf

"""
TODO
[x] avoid looping through tickers already in screened_stocks.csv OR empty_tickers.csv
[ ] logging
[ ] rank descending based on metrics
[ ] combine ranks/score
[ ] write each missing ticker as row to csv
[ ] exclude sector/industry
"""


"""
The goal of this script is to:

1.
- extract relevant metrics and save to csv
    - Ebit average 3 year
    - EV (enterprise value)
    - Return On Capital (ROC/ROIC), ROC = operating_income / (net_fixed_assets + net_working_capital)
    - Return On Equity (ROE)

2.
- use said metrics to give each stock a composite score where the lowest is best
- example:
    - rank all stocks by (EBIT 3y average) / Enterprise Value from high to low, e.g. highest score gives 1 point
    - rank all stocks by ROC or ROE from high to low, e.g. highest score gives 1 point
    - final stock score is the sum of its points, the lower the better
"""

# pathing
FILE_DIR = Path(__file__).parent
DATA_DIR = FILE_DIR / "data"

NORWEGIAN_TICKERS_PATH = DATA_DIR / "norwegian_tickers.csv"
DANISH_TICKERS_PATH = DATA_DIR / "danish_tickers.csv"
FINNISH_TICKERS_PATH = DATA_DIR / "finnish_tickers.csv"
SWEDISH_TICKERS_PATH = DATA_DIR / "swedish_tickers.csv"

EMPTY_TICKERS_PATH = DATA_DIR / "empty_tickers.csv"

RESULT_DIR = FILE_DIR.parent / "results"
RESULT_DIR.mkdir(exist_ok=True)
RESULT_NORWAY_PATH = RESULT_DIR / "metrics_norway.csv"


def list_to_csv(mylist: list[str], path: str):
    """
    Helper function to save list to csv
    """
    with open(path, "w", newline="") as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(mylist)


def add_suffix(df: pd.DataFrame, suffix: str) -> pd.DataFrame:
    """""
    Helper function for adding country suffix to stock tickers

    ARGS:
        df: dataframe containing non-suffixed stock ticker codes, e.g. "EQNR"
        suffix: ".OL" country suffix stock codes
    OUT: 
        df: dataframe with suffixed stock tickers, e.g. "EQNR.OL"
    """
    df.iloc[:, 0] = df.iloc[:, 0].astype(str) + f"{suffix}"
    return df


def load_one_stock_data(ticker_code: str) -> tuple[dict, pd.DataFrame]:
    """
    Get info and finance metrics of only one (1) stock/ticker from ticker code
    
    ARGS:
        ticker_code: example "EQNR.OL" = code of equinor listed in oslo stock exchange
    """

    # ticker_code = "AAPL" # apple inc
    stock_ticker = yf.Ticker(ticker_code)

    # info includes return on assets, trailingEps (Price to earnings)
    info = stock_ticker.info

    # financials includes net income
    financials = stock_ticker.get_financials()

    return info, financials


def write_headers_csv(file_path, headers: list[str]):
    """
    Helper function open csv and assign header
    """
    with open(file_path, "w") as csv_file:
        dw = csv.DictWriter(csv_file, delimiter=",", fieldnames=headers)
        dw.writeheader()


def append_row_csv(file_path: str, dict_row: dict, headers: list[str]):
    """
    Append one dict row to csv corresponding to headers
    """
    with open(file_path, "a") as csv_file:
        dw = csv.DictWriter(csv_file, delimiter=",", fieldnames=headers)
        dw.writerow(dict_row)


def rank_stocks():
    return


def main():

    headers = [
        "long_name",
        "ticker_name",
        "EBIT_2021",
        "EBIT_2020",
        "EBIT_2019",
        "EBIT_2018",
        "EBIT_average",
        "enterprise_value",
        "return_on_equity"
        # "final_score",
    ]

    # create csv with headers first time
    if not RESULT_NORWAY_PATH.is_file():
        write_headers_csv(RESULT_NORWAY_PATH, headers)

    # tickers
    norwegian_tickers = pd.read_csv(NORWEGIAN_TICKERS_PATH, header=None)[0]
    danish_tickers = pd.read_csv(DANISH_TICKERS_PATH, header=None)[0]
    finnish_tickers = pd.read_csv(FINNISH_TICKERS_PATH, header=None)[0]
    swedish_tickers = pd.read_csv(SWEDISH_TICKERS_PATH, header=None)[0]

    # broken tickers
    empty_tickers = []

    # add suffixes
    # norwegian_tickers = add_suffix(norwegian_tickers, ".OL")
    # danish_tickers = add_suffix(danish_tickers, ".CO")
    # finnish_tickers = add_suffix(finnish_tickers, ".HE")
    # swedish_tickers = add_suffix(swedish_tickers, ".ST")

    # save back to csv
    # norwegian_tickers.to_csv(NORWEGIAN_TICKERS_PATH, header=None, index=None)
    # danish_tickers.to_csv(DANISH_TICKERS_PATH, header=None, index=None)
    # finnish_tickers.to_csv(FINNISH_TICKERS_PATH, header=None, index=None)
    # swedish_tickers.to_csv(SWEDISH_TICKERS_PATH, header=None, index=None)

    # previously calculated tickers
    previously_calculated = pd.read_csv(RESULT_NORWAY_PATH)  # , header=headers)
    previously_calculated = pd.Series(previously_calculated["ticker_name"])

    # get set of non-calculated tickers
    norwegian_tickers = norwegian_tickers[
        ~norwegian_tickers.isin(previously_calculated)
    ]

    # TODO print log.info(f"==> Extracting metrics of [{len(norwegian_tickers)] {norwegian} tickers}")

    for index, ticker in norwegian_tickers.items():

        # TODO if index % 10 == 0 print(f""[{index}/{len(norwegian_tickers)}]")

        try:
            current_info, current_financials = load_one_stock_data(ticker)

            if current_financials.empty:
                # TODO append row to csv
                empty_tickers.append(ticker)
                list_to_csv(empty_tickers, EMPTY_TICKERS_PATH)
            else:

                # TODO encapsulate current_data inside function

                # get metrics
                long_name = current_info["longname"]
                ebits = current_financials.loc["Ebit"].values
                ebits_mean = np.mean(ebits)
                enterprise_value = current_info["enterpriseValue"]
                return_on_equity = current_info["returnOnEquity"]

                # combine metrics
                current_data = [
                    long_name,
                    ticker,
                    *ebits,
                    ebits_mean,
                    enterprise_value,
                    return_on_equity,
                ]

                # create dict from (headers, current datapoint) and write to csv
                dict_row = dict(zip(headers, current_data))
                append_row_csv(RESULT_NORWAY_PATH, dict_row, headers)

        except Exception as e:
            # TODO logging and save ticker to logfile
            print(ticker)
            print(e)
            continue
    return


if __name__ == "__main__":
    main()
