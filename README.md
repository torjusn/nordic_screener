# Nordic Screener
![this is an image](images/nordic_screener.png)

## Description
This repo is a scaled down version of [stock crawler](https://github.com/torjusn/stock_crawler_and_screener) that collects stock metrics through the [`Yahoo Finance API`](https://pypi.org/project/yfinance/) for the nordic markets and ranks them based on a set of composite metrics from ["The little book that beats the market"](https://www.amazon.com/Little-Book-Still-Beats-Market/dp/0470624159) by J. Greenblatt. Stock metrics are obtained by referencing ticker codes in yf, e.g. `CRAYN.OL` for `Crayon Group Holding ASA`, and responds with financial- and general info for that stock. Final scores for each stock are saved to excel as `.xlsx`.

## Screening algorithm
1. Rank each stock by `(EBIT 3y average)/EV`. Largest gets 1 point, second largest 2, etc.
2. Rank each stock by `ROC` OR `ROE`. Largest gets 1 point, second largest 2, etc.
3. Get each stocks final score by summing over all points. The smaller final score the better.

The philosophy behind this screener is to find a set of companies that on average trades at a bargain price relative to their true value. This is done with a margin of safety as the companies generally earn well compared to their cost with little debt and is further improved by spreading the portfolio over 20-30 stocks over a year. 

## Prerequisites
Install python packages from the requirements-file:
```
pip install -r requirements.txt
```

## Usage
Run mainscript for all tickers and save results to `.xlsx`-file:
```
main.py
```

## References
```
Greenblatt J. The Little Book That Still Beats the Market. 
Hoboken N.J: J. Wiley & Sons; 2010. http://site.ebrary.com/id/10419167. 
Accessed October 1 2022.
```

Special thanks to my colleague Thomas for giving me the opportunity to assist him in his stock adventures.