from etf_compare import EtfCleaner, EtfAnalyzer


your_path = "/Users/aleksa/Code/ETF_compare"

cleaner = EtfCleaner()
cleaner.etf_list_path = your_path + "/ETF_Tickers.csv"
cleaner.etf_description_path = your_path + "/ETF_Description.pkl"
cleaner.etf_data_path = your_path + "/ETF_Data.pkl"

etf_data = cleaner.etf_data
etf_description = cleaner.etf_description
analyzer = EtfAnalyzer()
analyzer.etf_dict_maker(etf_data, etf_description)
EtfAnalyzer.plot_tool( analyzer.etf_dict,
                       boxplot_no=20,
                       compare_list=[],
                       fig_path= your_path + "/boxplots.png" )