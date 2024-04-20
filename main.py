from tool import EtfCleaner, EtfAnalyzer
cleaner = EtfCleaner()


cleaner.etf_list_path = "/Users/aleksa/Code/ETF_compare/ETF_Tickers.csv"
cleaner.etf_description_path = "/Users/aleksa/Code/ETF_compare/ETF_Description.pkl"
cleaner.etf_data_path = "/Users/aleksa/Code/ETF_compare/ETF_Data.pkl"


df_dict = cleaner.etf_data
etf_description = cleaner.etf_description

analyzer = EtfAnalyzer()
analyzer.etf_dict_maker(df_dict, etf_description)
EtfAnalyzer.plot_tool(
    analyzer.etf_dict,
    boxplot_no=15,
    compare_list=['SOXX','SPY'],
    fig_path= "/Users/aleksa/Code/maleckicoa.github.io/assets/images/2024-04-15-ETF-compare/boxplots.png"
)
#print(df_dict.keys())
