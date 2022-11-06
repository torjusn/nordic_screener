# data
import pandas as pd

# local
import functions as fn

# pathing
FILE_DIR = Path(__file__).parent
DATA_DIR = FILE_DIR / "data"

# NORWEGIAN_TICKERS_PATH = DATA_DIR / "norwegian_tickers.csv"
DANISH_TICKERS_PATH = DATA_DIR / "danish_tickers.csv"
# FINNISH_TICKERS_PATH = DATA_DIR / "finnish_tickers.csv"
# SWEDISH_TICKERS_PATH = DATA_DIR / "swedish_tickers.csv"


# tickers
# norwegian_tickers = pd.read_csv(NORWEGIAN_TICKERS_PATH, header=None)[0]
danish_tickers = pd.read_csv(DANISH_TICKERS_PATH, header=None)[0]
# finnish_tickers = pd.read_csv(FINNISH_TICKERS_PATH, header=None)[0]
# swedish_tickers = pd.read_csv(SWEDISH_TICKERS_PATH, header=None)[0]

# add suffixes
# norwegian_tickers = fn.add_suffix(norwegian_tickers, ".OL")
danish_tickers = fn.add_suffix(danish_tickers, ".CO")
# finnish_tickers = fn.add_suffix(finnish_tickers, ".HE")
# swedish_tickers = fn.add_suffix(swedish_tickers, ".ST")

# save back to csv
# norwegian_tickers.to_csv(NORWEGIAN_TICKERS_PATH, header=None, index=None)
danish_tickers.to_csv(DANISH_TICKERS_PATH, header=None, index=None)
# finnish_tickers.to_csv(FINNISH_TICKERS_PATH, header=None, index=None)
# swedish_tickers.to_csv(SWEDISH_TICKERS_PATH, header=None, index=None)
