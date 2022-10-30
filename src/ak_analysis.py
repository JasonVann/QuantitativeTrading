import akshare as ak

# 行业数据
stock_szse_sector_summary_df = ak.stock_szse_sector_summary(symbol="当年", date="202204")
print(stock_szse_sector_summary_df)

stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date="20201111")
print(stock_sse_deal_daily_df)

stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date="20211227")
print(stock_sse_deal_daily_df)

# stock
stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)

stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20210907',
                                        adjust="")