# standard lib
import csv

# data
import numpy as np
import pandas as pd

# finance api
import yfinance as yf


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
    with open(file_path, "w", newline="") as csv_file:
        dw = csv.DictWriter(csv_file, delimiter=",", fieldnames=headers)
        dw.writeheader()


def append_row_csv(file_path: str, dict_row: dict, headers: list[str]):
    """
    Append one dict row to csv corresponding to headers
    """
    with open(file_path, "a", newline="") as csv_file:
        dw = csv.DictWriter(csv_file, delimiter=",", fieldnames=headers)
        dw.writerow(dict_row)


def get_metrics(ticker: str, info: dict, financials: pd.DataFrame):

    # get metrics
    long_name = info["longName"]  # ignore non utf-8 chars
    long_name = long_name.encode("ascii", "ignore")
    long_name = long_name.decode()

    ebits = financials.loc["Ebit"].values
    ebits_mean = np.mean(ebits)
    enterprise_value = info["enterpriseValue"]
    return_on_equity = info["returnOnEquity"]

    # combine metrics
    metrics = [
        long_name,
        ticker,
        *ebits,
        ebits_mean,
        enterprise_value,
        return_on_equity,
    ]

    return metrics


def get_ranked_stocks(metrics):

    original_idx_col = metrics.index

    # EBIT/EV
    metrics["EBIT/EV"] = (
        metrics["EBIT_average"] / metrics["enterprise_value"]
    )
    metrics = metrics.sort_values(by=["EBIT/EV"], ascending=False)
    metrics["EBIT/EV_rank"] = original_idx_col

    # ROE
    metrics = metrics.sort_values(
        by=["return_on_equity"], ascending=False
    )
    metrics["ROE_rank"] = original_idx_col

    # Total rank = EBIT/EV + ROE, low total = good stock
    metrics["total_rank"] = (
        metrics["EBIT/EV_rank"] + metrics["ROE_rank"]
    )
    metrics = metrics.sort_values(by=["total_rank"], ascending=True)

    return metrics


def rank_stocks():
    return
