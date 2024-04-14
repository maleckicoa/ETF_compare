from tool import ETF_Cleaner
cleaner = ETF_Cleaner()


cleaner.etf_list_path = "/Users/aleksa/Code/ETF_compare/ETF_Tickers.csv"
cleaner.etf_description_path = "/Users/aleksa/Code/ETF_compare/ETF_Description.pkl"
cleaner.etf_data_path = "/Users/aleksa/Code/ETF_compare/ETF_Data.pkl"

d = cleaner.etf_data
print(d)

print(len(d))


