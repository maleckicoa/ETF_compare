from etf_compare import EtfCleaner, EtfAnalyzer
cleaner = EtfCleaner()


cleaner.etf_list_path = "/Users/aleksa/Code/ETF_compare/test/ETF_Tickers.csv"
cleaner.etf_description_path = "/Users/aleksa/Code/ETF_compare/ETF_Description.pkl"
cleaner.etf_data_path = "/Users/aleksa/Code/ETF_compare/ETF_Data.pkl"


df_dict = cleaner.etf_data
etf_description = cleaner.etf_description

analyzer = EtfAnalyzer()
analyzer.etf_dict_maker(df_dict, etf_description)

df_dict = analyzer.etf_dict['TNOW.L']['Description']
print(df_dict)