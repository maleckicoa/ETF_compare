from etf_compare import EtfCleaner, EtfAnalyzer
cleaner = EtfCleaner()

your_path = "/Users/aleksa/Code/ETF_compare/test/"

cleaner.etf_list_path = your_path + "//ETF_Tickers_test.csv"

cleaner.etf_description_path = your_path + "//ETF_Description_test.pkl"
cleaner.make_description_file(path = your_path + "//ETF_Description_test.pkl")
cleaner.etf_description_path = your_path + "//ETF_Description_test.pkl"

cleaner.etf_data_path = your_path + "//ETF_Data_test.pkl"
cleaner.make_etf_data(your_path + "//ETF_Data_test.pkl")
cleaner.etf_data_path = your_path + "//ETF_Data_test.pkl"

#print(cleaner.etf_data)

#print(cleaner.etf_description)

etf_data = cleaner.etf_data
etf_description = cleaner.etf_description

analyzer = EtfAnalyzer()
analyzer.etf_dict_maker(etf_data, etf_description)
EtfAnalyzer.plot_tool(
    analyzer.etf_dict,
    boxplot_no=10,
    compare_list=['PSCT'],
    fig_path= your_path + "//boxplots_test.png"
)