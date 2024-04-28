import pytest
import os.path
from etf_compare import EtfCleaner, EtfAnalyzer

@pytest.fixture
def ticker(your_path = "/Users/aleksa/Code/ETF_compare/tests"):
    cleaner = EtfCleaner()
    cleaner.etf_list_path = your_path + "/ETF_Tickers_test.csv"
    return cleaner
@pytest.fixture
def ticker_descr(ticker, your_path = "/Users/aleksa/Code/ETF_compare/tests"):
    ticker.etf_description_path = your_path + "/ETF_Description_test.pkl"
    return ticker
@pytest.fixture
def ticker_descr_data(ticker_descr, your_path = "/Users/aleksa/Code/ETF_compare/tests"):
    ticker_descr.etf_data_path = your_path + "/ETF_Data_test.pkl"
    return ticker_descr
@pytest.fixture
def analyzer_load(ticker_descr_data):
    etf_description = ticker_descr_data.etf_description
    etf_data = ticker_descr_data.etf_data
    analyzer = EtfAnalyzer()
    analyzer.etf_dict_maker(etf_data, etf_description)
    return analyzer


def test_if_ticker_is_loaded(ticker):
    assert isinstance(ticker.etf_list, list)

def test_if_description_file_exists(ticker_descr):
    assert os.path.isfile(ticker_descr.etf_description_path)

def test_if_description_file_is_generated(ticker, your_path = "/Users/aleksa/Code/ETF_compare/tests"):
    full_path = your_path + "/ETF_Description_test_2.pkl"
    ticker.make_description_file(path = full_path )
    ticker.etf_description_path = full_path
    assert ticker.etf_description_path == full_path
    assert os.path.isfile(full_path)
    os.remove(full_path)

def test_if_data_file_exists(ticker_descr_data):
    assert os.path.isfile(ticker_descr_data.etf_data_path)

def test_if_data_file_is_generated(ticker_descr, your_path = "/Users/aleksa/Code/ETF_compare/tests"):
    full_path = your_path + "/ETF_Data_test_2.pkl"
    ticker_descr.make_etf_data(path = full_path)
    ticker_descr.etf_description_path = full_path
    assert ticker_descr.etf_description_path == full_path
    assert os.path.isfile(full_path)
    os.remove(full_path)

def test_descr_property_format(ticker_descr_data):
    assert isinstance(ticker_descr_data.etf_description,dict)
    assert len(ticker_descr_data.etf_description.keys()) > 0

def test_data_property_format(ticker_descr_data):
    assert isinstance(ticker_descr_data.etf_data,dict)
    assert len(ticker_descr_data.etf_data.keys())>0

def test_if_analyzer_dictionary_is_loaded(analyzer_load):
    assert isinstance(analyzer_load.etf_dict,dict)
    assert len(analyzer_load.etf_dict) > 0

def test_if_plot_works_with_empty_compare_list(analyzer_load, your_path = "/Users/aleksa/Code/ETF_compare/tests" ):
    full_path = your_path + "/boxplots_test_2.png"
    EtfAnalyzer().plot_tool(
        analyzer_load.etf_dict,
        boxplot_no=10,
        compare_list=[],
        fig_path = full_path)
    assert os.path.isfile(full_path)
    os.remove(full_path)

def test_if_plot_with_nonexistent_ticker_in_compare_list_raises_error(analyzer_load, your_path = "/Users/aleksa/Code/ETF_compare/tests" ):
    full_path = your_path + "/boxplots_test_2.png"
    with pytest.raises(ValueError):
        EtfAnalyzer().plot_tool(
            analyzer_load.etf_dict,
            boxplot_no=10,
            compare_list=['SOME_NONEXISTENT_TICKER','SOME_NONEXISTENT_TICKER2'],
            fig_path = full_path)

def test_if_plot_works_with_duplicate_tickers(analyzer_load, your_path = "/Users/aleksa/Code/ETF_compare/tests" ):
    full_path = your_path + "/boxplots_test_2.png"
    EtfAnalyzer().plot_tool(
        analyzer_load.etf_dict,
        boxplot_no=10,
        compare_list=['SPY','SPY','XLG','SPY'],
        fig_path = full_path)
    assert os.path.isfile(full_path)
    os.remove(full_path)


def test_if_exceeding_boxplot_no_raises_error(analyzer_load, your_path = "/Users/aleksa/Code/ETF_compare/tests" ):
    full_path = your_path + "/boxplots_test_2.png"
    with pytest.raises(ValueError):
        EtfAnalyzer().plot_tool(
            analyzer_load.etf_dict,
            boxplot_no=22,
            compare_list=[],
            fig_path = full_path)

def test_if_exceeding_boxplot_no_raises_error(analyzer_load, your_path = "/Users/aleksa/Code/ETF_compare/tests" ):
    full_path = your_path + "/boxplots_test_2.png"
    EtfAnalyzer().plot_tool(
        analyzer_load.etf_dict,
        boxplot_no=20,
        compare_list=[],
        fig_path = full_path)
    os.remove(full_path)