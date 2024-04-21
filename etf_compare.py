
import pickle
import pandas as pd
import numpy as np
import statistics as stat
from datetime import date
from collections import OrderedDict
import yfinance as yf
import matplotlib.pyplot as plt
from logger import log_output_to_file

class EtfCleaner:
    def __init__(self):
        self._etf_list_path = None
        self._etf_description_path = None
        self._etf_data_path = None

        self._etf_list = None
        self._etf_description = None
        self._etf_data = None

    @property
    def etf_list_path(self):
        return self._etf_list_path

    @etf_list_path.setter
    def etf_list_path(self, path):
        """
        Set the path to the ETF_Tickers file
        """
        self._etf_list_path = path
        self._etf_list = self.load_etf_list(path)

    @property
    def etf_description_path(self):
        return self._etf_description_path

    @etf_description_path.setter
    def etf_description_path(self, path):
        """
        Set the path to the ETF_Description file
        """
        self._etf_description_path = path
        self._etf_description = self.load_etf_description(path)

    @property
    def etf_data_path(self):
        return self._etf_data_path

    @etf_data_path.setter
    def etf_data_path(self, path):
        """
        Set the path to the ETF_Data file
        """
        self._etf_data_path = path
        self._etf_data = self.load_etf_data(path)

    @property
    def etf_list(self):
        return self._etf_list

    @property
    def etf_description(self):
        return self._etf_description

    @property
    def etf_data(self):
        return self._etf_data

    def load_etf_list(self, path):
        """
        Load the ETF list from a CSV file

        :param path: path to the csv file
        :return: A list of all ETFs in the ETF_Ticker file
        """

        try:
            etf_data = pd.read_csv(path)
            etf_list = etf_data['TICKER'].tolist()
            etf_list = list(OrderedDict.fromkeys(etf_list))
            etf_list = [x for x in etf_list if x != '#NAME?']

            return etf_list
        except Exception as e:
            print(f"Failed to load ETF list: {e}")
            return None

    def load_etf_description(self, path):
        """
        Loads the ETF description from a pickle file

        :param path: path to the pickle file
        :return: A dictionary with all ETF names and short description
        """


        try:
            with open(path, 'rb') as file:
                etf_description = pickle.load(file)
            return etf_description
        except Exception as e:
            print(f"Failed to load ETF description: {e}")
            print(f"To create the description file again run the make_description_file method ")
            return None

    def make_description_file(self, path):
        """
        Calls the Yahoo Finance API and creates the ETF_Description.pkl file for all ETF Tickers

        :param path: path to where the pickle file is stored
        :return: None
        """
        if self._etf_list is None:
            print("ETF list is not loaded. Please set the etf_list_path first.")
            return

        etf_description = {}
        j = 0
        for i in self._etf_list:
            j += 1
            try:
                tickers = yf.Ticker(i)
                print(f"{j} out of {len(self._etf_list)} descriptions loaded.")
                long_name = tickers.info.get('longName', '')
            except Exception as e:
                long_name = ''
                print(f"Error retrieving long name for {i}: {e}")

            try:
                tickers = yf.Ticker(i)
                short_name = tickers.info.get('shortName', '')
            except Exception as e:
                short_name = ''
                print(f"Error retrieving short name for {i}: {e}")

            etf_description[i] = long_name + '_' + short_name

        with open(path, 'wb') as file:
            pickle.dump(etf_description, file)
            print("ETF description file created.")

    def load_etf_data(self, path):
        """
        Loads the ETF price data from a pickle file

        :param path: path to where the pickle file is
        :return: A dictionary of prices for all ETF tickers
        """
        # Load ETF description from a pickle file
        try:
            with open(path, 'rb') as file:
                etf_data = pickle.load(file)
            return etf_data
        except Exception as e:
            print(f"Failed to load ETF data: {e}")
            print(f"To create the data file again run the make_data_file method ")
            return None

    @log_output_to_file('output.log')
    def make_etf_data(self, path):
        """
        Creates the ETF_Data.pkl file

        :param path: path to where the pickle file is stored
        :return: None
        """
        df_dict = {}
        nan_series = self._make_nan_series()

        for idx, i in enumerate(self._etf_list):
            print(i)
            try:
                data = yf.Ticker(i).history(period="max", interval='1mo')
                df = data['Close']
                df.name = i

                if len(df) < 20:
                    print('Series is too short')
                    continue

                if self._gap(df):
                    print('Series has a large gap')
                    continue

                clean_df = self._clean_df_index(df)

                if self._check_last_6_months(clean_df, nan_series):
                    print('Series is missing recent data')
                    continue

                long_df = clean_df.combine_first(nan_series)
                long_df = long_df.interpolate(method='linear', limit_area='inside')

                if self._check_jump(long_df):
                    print('Series has corrupted data')
                    continue

                print(i, idx)
                df_dict[i] = long_df

            except Exception as e:
                print('Error processing {}: {}'.format(i, e))

        with open(path, 'wb') as file:
            pickle.dump(df_dict, file)
            print("ETF data file created.")

    def _gap(self, df, gap_size=5):

        """
        Private method to eliminate ETFs with a given gap in price data

        :param df: dataframe of Yahoo prices for one ETF
        :param gap_size: int
        :return: bool
        """
        data = list(df)
        for idx, i in enumerate(data):
            if isinstance(i, float):
                left = idx
                break
        data_rev = data[::-1]
        for idx, i in enumerate(data_rev):
            if isinstance(i, float):
                right = len(data) - idx
                break
        data = data[left:right]
        series = pd.Series(data)
        is_nan_series = series.isna()
        rolling_sum = is_nan_series.rolling(window=4, min_periods=1).sum()
        has_large_gap = any(rolling_sum >= gap_size)
        return has_large_gap


    def _make_nan_series(self):
        """
        Private method that sets the maximum time series length as of 1993
        :return: pandas Series
        """
        date_range = pd.date_range(start='1993-01-01', end=date.today(), freq='MS')
        nan_series = pd.Series(np.nan, index=date_range)
        nan_series = nan_series.sort_index()
        nan_series.index = pd.to_datetime(nan_series.index)
        nan_series.index = nan_series.index.date
        return nan_series

    def _clean_df_index(self, df):
        """
        Private method that filters out prices which are not from 1st of month
        :param df: dataframe of Yahoo prices for one ETF
        :return: clean dataframe of Yahoo prices for one ETF
        """
        df = df.sort_index()
        df.index = pd.to_datetime(df.index)
        is_first_of_month = df.index.is_month_start
        df = df[df.index[is_first_of_month]]
        df.index = df.index.date
        return df

    def _check_last_6_months(self, df, nan_series):
        """
        Private method that eliminated ETFs for which there are gaps in the last 6 months of data
        :param df: dataframe of Yahoo prices for one ETF
        :param nan_series: the default empty time eries as of 1993
        :return: bool
        """
        set1 = set(list(nan_series[-9:-3].index))
        set2 = set(list(df.index))
        intersection = set1.intersection(set2)
        return len(intersection) != 6

    def _check_jump(self, df, min_series=24, jump_size=3):
        """
        Private method that filters out an ETF if the price series doesn't have a necessary minimum length of 2 years, and if there are any
        large price jumps between 2 consecutive months (jumps/falls larger than +300% /-66%)
        :param df: dataframe of Yahoo prices for one ETF
        :param min_series: (int) minimum price series length in months
        :param jump_size: (maximum) allowed price jump between 2 months
        :return: bool
        """
        clean_list = [x for x in df if not pd.isna(x)]
        jump_list = [x / clean_list[idx - 1] for idx, x in enumerate(clean_list) if idx > 0]
        if len(jump_list) < min_series or max(jump_list) >= jump_size or min(jump_list) <= 1 / jump_size:
            return True



class EtfAnalyzer:
    def __init__(self):
        self.etf_dict = None

    def etf_dict_maker(self,
                             df_dict,
                             etf_description,
                             year_list=(1, 2, 5, 7, 10),
                             window=5):
        """
        The Method returns a dictionary of the format:

        Ticker
            Description : the description of the ETF
            Original_series : the original ETF price data
            Returns
                1_Years
                    name: ETF ticker name
                    data points: length of series
                    median_return: the median value of the returns series
                    returns: a series of 1-year ETF returns in a rolling window, always on the 1st of the month,
                2_Years
                    name: ...
                    data points: ...
                    median_return: ...
                    returns: a series of 2-year ETF returns, always on the 1st of the month, on a rolling window
                5_Years
                7_Years
                10_Years

        :param df_dict: a dictionary of price data for all ETFs
        :param etf_description: a dictionary of descriptions for all ETFs
        :param year_list: (tuple) ETF holding periods
        :param window: the number of years added to the holding period to define the total time frame of the ETF investment
        :return: None
        """

        nested_dict = {}

        for i in df_dict.keys():
            nested_dict[f'{i}'] = {}

            orig_series = df_dict[i].dropna()
            start_date = str(orig_series.index[0])

            try:
                description = etf_description[i]
            except:
                description = 'No Description'

            nested_dict[f'{i}'] = {'Description': description}
            nested_dict[f'{i}'][f'Original_Series'] = {'series': orig_series, 'start_date': start_date}
            nested_dict[f'{i}']['Returns'] = {}

            for year in year_list:
                core_series = orig_series[len(orig_series) - (year + window) * 12:len(orig_series)]
                returns = [core_series.iloc[j] / core_series.iloc[j - year * 12] for j in
                           list(range(0, len(core_series))) if (j >= year * 12)]

                if len(returns) > 0:
                    med_return = stat.median(returns)
                else:
                    med_return = 0

                nested_dict[f'{i}']['Returns'][f'{year}_Years'] = {'name': i, 'data_points': len(returns),
                                                                   'median_return': med_return, 'returns': returns}
        self.etf_dict = nested_dict

    @classmethod
    def _etf_ranking(cls, summary_dict: dict, row_no:int):
        """
        Private class method that yields the points table at the end of the report

        :param summary_dict: (dict) a dictionary of ETFs and their respective points obtained within each holding period group
        :param row_no: (int) number of rows in the table /number of ETFs
        :return: (dataframe) dataframe of ETFs ranked by their overall performance
        """
        df = pd.DataFrame(summary_dict)
        df_reversed = df.iloc[::-1].reset_index(drop=True)
        df_reversed['rank'] = df_reversed.index + 1
        df_melted = df_reversed.melt(id_vars='rank', var_name='', value_name='Ticker')
        df_pivot = df_melted.pivot(index='Ticker', columns='', values='rank')
        df_pivot['Points'] = df_pivot.sum(axis=1, skipna=True)
        df_points = df_pivot.sort_values(by=['Points'], ascending=False)
        df_points = df_points.astype('Int64')
        df_points['Ticker'] = df_points.index
        df_points = df_points[['Ticker', '1_Years', '2_Years', '5_Years', '7_Years', '10_Years', 'Points']].fillna(0)
        return df_points.head(row_no)


    @classmethod
    def _contain_substr(cls, s, substrings):
        return any(sub in s for sub in substrings)

    @classmethod
    def plot_tool(cls,
                  nested_dict,
                  leveraged_substrings=('2X', '2x', '3X', '3x', 'Leveraged', 'ProShares'),
                  corrupt_keys=['EU', 'RYF','EEP.PA', 'BITCOIN-XBT.ST'],
                  year_window=('1_Years', '2_Years', '5_Years', '7_Years', '10_Years'),
                  boxplot_no=20,
                  compare_list = [],
                  fig_path = './boxplot.png'):
        """
        Class method for plotting the final report

        :param nested_dict: (dict) A processed and comprehensive dictionary of original prices, returns, descriptions, etc. for all ETFs
        :param leveraged_substrings: (tuple) substrings provided to locate and filter out the leverage ETFs
        :param corrupt_keys: (list) ETF tickers for which the Yahoo Finance API returns corrupted/incorrect prices
        :param year_window: (tuple) holding periods
        :param boxplot_no: (int) number of boxplots to be plotted per holding period, maximum 20 boxplots
        :param compare_list: (list) list of ETFs the user can include to be compared against the best performing ETFs
        :param fig_path: (str) path to where the report is stored
        :return: PNG image
        """


        if len(list(set(compare_list) - set(list(nested_dict.keys()))))>0:
            raise ValueError("One or more ticker symbols you provided does not exist in the ETF_Tickers input list")


        if boxplot_no >20:
            raise ValueError("Maximum 20 boxplots are supported in the figure")


        leveraged_keys = [key for key, values in nested_dict.items() if
                          cls._contain_substr(values['Description'], leveraged_substrings) == True]

        remove_keys = corrupt_keys + leveraged_keys
        nested_dict_clean = {key: value for key, value in nested_dict.items() if key not in remove_keys}


        fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(15, 30))
        axes = axes.flatten()

        summary = dict()

        for idx, i in enumerate(year_window):

            sorted_keys = sorted(nested_dict_clean.keys(), reverse=True,
                                 key=lambda x: nested_dict_clean[x]['Returns'][i]['median_return'])
            sorted_dict = {key: nested_dict_clean[key] for key in sorted_keys}

            tickers = list()
            description_list = list()
            data_to_plot = list()
            etf_names = list()

            sorted_list = list(sorted_dict.keys())[0:boxplot_no]
            compare_list_trim = [x for x in compare_list if x not in sorted_list]
            trim = len(compare_list_trim)
            sorted_list = list(sorted_dict.keys())[0:boxplot_no - trim]
            combined_dict = dict.fromkeys(sorted_list + compare_list_trim)
            for j in list(combined_dict):

                returns = sorted_dict[j]['Returns'][i]['returns']
                median_return = sorted_dict[j]['Returns'][i]['median_return']
                description = sorted_dict[j]['Description']

                tickers.append(j)
                description_list.append(j + ' - ' + f'{median_return:.3g}' + ' - ' + description)
                data_to_plot.append(returns)
                etf_names.append(j)

            summary[i] = tickers

            axes[idx].boxplot(data_to_plot)
            axes[idx].set_title(i)
            axes[idx].set_ylabel('Cumulative Return')
            axes[idx].set_xticks(list(range(1, len(etf_names) + 1)), etf_names,
                                 rotation=90)
            axes[idx].legend(description_list, loc='upper left', bbox_to_anchor=(1, 1), fontsize=7, handlelength=0,
                             handletextpad=0, markerscale=0)

        df_points_table = cls._etf_ranking(summary, boxplot_no)
        axes[5].table(cellText=df_points_table.values, colLabels=df_points_table.columns, loc='center')
        axes[5].axis('off')

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.5)
        plt.savefig(fig_path)
        #plt.show()

