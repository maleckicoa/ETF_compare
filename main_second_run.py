from etf_compare import EtfCleaner, EtfAnalyzer

if __name__ == "__main__":

    your_path = "/Users/aleksa/Code/ETF_compare"                      # set a path where all files are generated

    cleaner = EtfCleaner()                                            # initialize the cleaner object
    cleaner.etf_list_path = your_path + "/ETF_Tickers.csv"            # set the path to the list of tickers
    cleaner.etf_description_path = your_path + "/ETF_Description.pkl" # set the path to the ETF description file
    cleaner.etf_data_path = your_path + "/ETF_Data.pkl"               # set the path to the ETF price data file

    etf_data = cleaner.etf_data               # make the ETF price data object
    etf_description = cleaner.etf_description # make the ETF description data object

    analyzer = EtfAnalyzer()     # initialize the analyzer object
    analyzer.etf_dict_maker(etf_data, etf_description)
    # read in the ETF price and ETF description into the analyzer object, this creates analyzer.etf_dict attribute

    # Run the plotting tool to obtain a comprehensive visual report about ETF performance.
    EtfAnalyzer.plot_tool( analyzer.etf_dict,
                           boxplot_no=20,
                           compare_list=[],
                           fig_path= your_path + "/boxplots.png" )