from tool import  ETFAnalyzer

etf_analyzer = ETFAnalyzer("/Users/aleksa/Code/PY/Py - MY Scripts/ETFs_Tickers.csv")
etf_list = etf_analyzer.make_etf_list
print(etf_list)
