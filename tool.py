
import pickle
import pandas as pd
import numpy as np
import statistics as stat
from datetime import date
from collections import OrderedDict
import yfinance as yf
import matplotlib.pyplot as plt

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
        self._etf_list_path = path
        self._etf_list = self.load_etf_list(path)

    @property
    def etf_description_path(self):
        return self._etf_description_path

    @etf_description_path.setter
    def etf_description_path(self, path):
        self._etf_description_path = path
        self._etf_description = self.load_etf_description(path)

    @property
    def etf_data_path(self):
        return self._etf_data_path

    @etf_data_path.setter
    def etf_data_path(self, path):
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
        # Load ETF list from a CSV file
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
        # Load ETF description from a pickle file
        try:
            with open(path, 'rb') as file:
                etf_description = pickle.load(file)
            return etf_description
        except Exception as e:
            print(f"Failed to load ETF description: {e}")
            print(f"To create the description file again run the make_description_file method ")
            return None

    def make_description_file(self, path):

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
        # Load ETF description from a pickle file
        try:
            with open(path, 'rb') as file:
                etf_data = pickle.load(file)
            return etf_data
        except Exception as e:
            print(f"Failed to load ETF data: {e}")
            print(f"To create the data file again run the make_data_file method ")
            return None

    def make_etf_data(self, path):
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
        date_range = pd.date_range(start='1993-01-01', end=date.today(), freq='MS')
        nan_series = pd.Series(np.nan, index=date_range)
        nan_series = nan_series.sort_index()
        nan_series.index = pd.to_datetime(nan_series.index)
        nan_series.index = nan_series.index.date
        return nan_series

    def _clean_df_index(self, df):
        df = df.sort_index()
        df.index = pd.to_datetime(df.index)
        is_first_of_month = df.index.is_month_start
        df = df[df.index[is_first_of_month]]
        df.index = df.index.date
        return df

    def _check_last_6_months(self, long_df, nan_series):
        set1 = set(list(nan_series[-9:-3].index))
        set2 = set(list(long_df.index))
        intersection = set1.intersection(set2)
        return len(intersection) != 6

    def _check_jump(self, df, min_series=24, jump_size=3):
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
                  compare_list = []):


        if len(list(set(compare_list) - set(list(nested_dict.keys()))))>0:
            raise ValueError("One or more ticker symbols you provided does not exist")


        if boxplot_no >20:
            raise ValueError("Maximum 20 boxplots are supported")


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
            trim = len(list(set(compare_list) - set(sorted_list)))
            sorted_list = list(sorted_dict.keys())[0:boxplot_no - trim]
            combined_dict = dict.fromkeys(sorted_list + compare_list)


            for j in list(combined_dict):
                returns = sorted_dict[j]['Returns'][i]['returns']
                median_return = sorted_dict[j]['Returns'][i]['median_return'].round(2)
                description = sorted_dict[j]['Description']

                tickers.append(j)
                description_list.append(j + ' - ' + str(median_return) + ' - ' + description)
                data_to_plot.append(returns)
                etf_names.append(j)

            summary[i] = tickers

            axes[idx].boxplot(data_to_plot)
            axes[idx].set_title(i)
            axes[idx].set_ylabel('Cumulative Return')
            axes[idx].set_xticks(list(range(1, len(etf_names) + 1)), etf_names,
                                 rotation=90)  # Setting the x-ticks to match stock names
            axes[idx].legend(description_list, loc='upper left', bbox_to_anchor=(1, 1), fontsize=7, handlelength=0,
                             handletextpad=0, markerscale=0)

        df_points_table = cls._etf_ranking(summary, boxplot_no)
        axes[5].table(cellText=df_points_table.values, colLabels=df_points_table.columns, loc='center')
        axes[5].axis('off')

        plt.tight_layout()
        plt.subplots_adjust(hspace=0.5)
        plt.savefig("/Users/aleksa/Code/ETF_compare/boxplots.png")
        #plt.show()

