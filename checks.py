from tool import  ETF_Cleaner
cleaner = ETF_Cleaner()



cleaner.etf_list_path = "/Users/aleksa/Code/ETF_compare/ETF_Tickers_delete.csv"

cleaner.etf_description_path = "/Users/aleksa/Code/ETF_compare/ETF_Description_delete.pkl"
cleaner.make_description_file(path = "/Users/aleksa/Code/ETF_compare/ETF_Description_delete.pkl")
cleaner.etf_description_path = "/Users/aleksa/Code/PY/ETF_compare/ETF_Description_delete.pkl"

cleaner.etf_data_path = "/Users/aleksa/Code/ETF_compare/ETF_Data_delete.pkl"
cleaner.make_etf_data("/Users/aleksa/Code/ETF_compare/ETF_Data_delete.pkl")
cleaner.etf_data_path = "/Users/aleksa/Code/ETF_compare/ETF_Data_delete.pkl"

print(cleaner.etf_data)