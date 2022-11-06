# -----------------------------------------------------------------------------
# rate nordic stocks by metrics and save scores + metrics to csv
#
# Torjus Nilsen, Drammen, Norway
# email tornil1996@hotmail.com
# -----------------------------------------------------------------------------

# standard lib
import time
import logging
from pathlib import Path

# data
import numpy as np
import pandas as pd

# local
import functions as fn

"""
TODO
[x] avoid looping through tickers already in screened_stocks.csv OR empty_tickers.csv
[x] logging
[ ] rank descending based on metrics
[ ] combine ranks/score
[ ] write README
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

# free version of yahoo api has a max request per hour per ip
MAX_TICKERS_PER_HOUR = 25

# pathing
FILE_DIR = Path(__file__).parent

DATA_DIR = FILE_DIR / "data"
ticker_paths = [
    DATA_DIR / filename
    for filename in [
        "norwegian_tickers.csv",
        "danish_tickers.csv",
        "finnish_tickers.csv",
        "swedish_tickers.csv",
    ]
]
EMPTY_TICKERS_PATH = DATA_DIR / "empty_tickers.csv"

RESULT_DIR = FILE_DIR.parent / "results"
RESULT_DIR.mkdir(exist_ok=True)
metric_paths = [RESULT_DIR / ("metrics_" + path.name) for path in ticker_paths]
result_paths = [RESULT_DIR / ("rank_" + path.stem + ".xlsx") for path in ticker_paths]

# logging
logger = logging.getLogger(__name__)

# streamhandler displays to console, filehandler writes to logfile
console_handler = logging.StreamHandler()
log_path = Path(__file__).stem + ".log"
file_handler = logging.FileHandler(log_path)

# format log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)


def main():

    logger.info("==> Started Main Script")

    empty_headers = ["ticker_name"]
    if not EMPTY_TICKERS_PATH.is_file():
        fn.write_headers_csv(EMPTY_TICKERS_PATH, empty_headers)

    metric_headers = [
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

    ticker_count = 0

    # loop each country
    for ticker_path, metric_path, result_path in zip(
        ticker_paths, metric_paths, result_paths
    ):
        tickers = pd.read_csv(ticker_path, header=None)[0]
        # create result csv with headers first time
        if not metric_path.is_file():
            fn.write_headers_csv(metric_path, metric_headers)

        # exclude previously calculated tickers and empty ones
        previously_calculated_tickers = pd.read_csv(metric_path)
        previously_calculated_tickers = pd.Series(
            previously_calculated_tickers["ticker_name"]
        )
        tickers = tickers[~tickers.isin(previously_calculated_tickers)]

        empty_tickers = pd.read_csv(EMPTY_TICKERS_PATH)
        empty_tickers = pd.Series(empty_tickers["ticker_name"])
        tickers = tickers[~tickers.isin(empty_tickers)]

        if len(tickers) > 0:

            logger.info(
                f"Extracting metrics of [{len(tickers)}] tickers from [{ticker_path.name}]..."
            )

            # loop each ticker of that country, extract metrics, save to csv
            for idx, (original_idx, ticker) in enumerate(tickers.items()):

                # display progress
                if idx % 10 == 0:
                    logger.info(f"extracting ticker no. [{idx}/{len(tickers)}]")

                try:
                    current_info, current_financials = fn.load_one_stock_data(ticker)

                    # write broken tickers to separate file
                    if current_financials.empty:
                        empty_row = {empty_headers[0]: ticker}
                        fn.append_row_csv(EMPTY_TICKERS_PATH, empty_row, empty_headers)
                    # write functioning ticker metrics to output
                    else:
                        metrics = fn.get_metrics(
                            ticker, current_info, current_financials
                        )

                        # create dictrow and write to csv
                        dict_row = dict(zip(metric_headers, metrics))
                        fn.append_row_csv(metric_path, dict_row, metric_headers)

                except Exception as e:
                    logging.error(e)
                    logging.error(f"{ticker}")
                    continue

                # wait an hour after using max requests per hour for yfinance api
                ticker_count += 1
                if ticker_count >= MAX_TICKERS_PER_HOUR:
                    sleep_time = 3600
                    logging.info(
                        f"Sleep for {sleep_time}sec to avoid yfi max request cap"
                    )
                    time.sleep(sleep_time)
                ticker_count = 0

        # rank stocks of country by extracted data
        completed_metrics = pd.read_csv(metric_path)
        original_idx_col = completed_metrics.index

        # EBIT/EV
        completed_metrics["EBIT/EV"] = (
            completed_metrics["EBIT_average"] / completed_metrics["enterprise_value"]
        )
        completed_metrics = completed_metrics.sort_values(
            by=["EBIT/EV"], ascending=False
        )
        completed_metrics["EBIT/EV_rank"] = original_idx_col

        # ROE
        completed_metrics = completed_metrics.sort_values(
            by=["return_on_equity"], ascending=False
        )
        completed_metrics["ROE_rank"] = original_idx_col

        # Total rank = EBIT/EV + ROE, low total = good stock
        completed_metrics["total_rank"] = (
            completed_metrics["EBIT/EV_rank"] + completed_metrics["ROE_rank"]
        )
        completed_metrics = completed_metrics.sort_values(
            by=["total_rank"], ascending=True
        )
        # completed_metrics.to_csv(result_path, na_rep="Nan", index=False)
        completed_metrics.to_excel(result_path, na_rep="Nan", index=False)


if __name__ == "__main__":
    main()
