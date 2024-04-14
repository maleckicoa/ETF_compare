#import yfinance as yf
import os
import sys
import pickle
import pandas as pd
import numpy as np
import statistics as stat
import math
from datetime import date
from collections import OrderedDict

class ETFAnalyzer:
    def __init__(self, path="ETFs_Tickers.csv"):
        self.path = path
        self.etf_list = []

    @property
    def make_etf_list(self):
        # Read the ETF tickers from a CSV file
        etf_file = pd.read_csv(self.path)
        etf_list = etf_file['TICKER'].tolist()

        # Create a unique ordered list
        etf_list = list(OrderedDict.fromkeys(etf_list))

        # Filter out unwanted entries
        etf_list = [x for x in etf_list if x != '#NAME?']

        # Store the cleaned list in the instance attribute
        self.etf_list = etf_list

        return etf_list


# Usage


