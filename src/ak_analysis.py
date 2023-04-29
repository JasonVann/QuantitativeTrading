import akshare as ak
import datetime
import pandas as pd




def eval_market(market = "上证", num_years=10):
    '''
    Evaluate PB/PE of the market
    # "上证", "深证", "创业板", "科创版"
    :return:
    '''
    # 股市PE估值, 每月月底一条数据
    pe_df = ak.stock_market_pe_lg(market)  # "上证", "深证", "创业板", "科创版"

    today = datetime.date.today()
    hist_start = today.replace(today.year - num_years)

    df2 = pe_df[pe_df['日期'] > hist_start]

    pe_summary_df = get_percentile(df2, index_name='平均市盈率')

    pb_df = ak.stock_market_pb_lg(market)  # "上证", "深证", "创业板", "科创版"

    df3 = pb_df[pb_df['日期'] > hist_start]
    pb_summary_df = get_percentile(df3, index_name='市净率')

    df = ak.stock_index_pe_lg("上证50")  # {"上证50", "沪深300", "上证380", "创业板50", "中证500", "上证180", "深证红利", "深证100", "中证1000", "上证红利", "中证100", "中证800"}
    df2 = df[df['日期'] > hist_start]
    pe_summary_df = get_percentile(df2, index_name='静态市盈率')

    return pe_summary_df


def get_percentile(df, index_name='平均市盈率'):

    df['rank'] = df[index_name].rank(pct=True)
    # print(df)
    temp_df = df.describe()[['指数', index_name, 'rank']]

    temp_df.loc[len(temp_df.index)] = [float(df.tail(1)['指数'].values), float(df.tail(1)[index_name].values),
                           float(df.tail(1)['rank'].values)]
    temp_df = temp_df.rename(index={len(temp_df.index) - 1: df.tail(1)['日期']})

    return temp_df

# res = eval_market(market = "上证", num_years=10)


def eval_sector():
    '''
    "sw_index_representation_spot"  # 申万市场表征数据
    "sw_index_spot"  # 申万一级实时行情
    "sw_index_second_spot"  # 申万二级实时行情
    "sw_index_cons"  # 申万一级、二级板块成份
    "sw_index_daily"  # 申万一级、二级历史行情
    "sw_index_daily_indicator"  # 申万一级、二级历史行情指标
    "sw_index_third_info"  # 申万三级信息
    "sw_index_third_cons"  # 申万三级信息成份
    "index_level_one_hist_sw"  # 申万指数-指数发布-指数体系-一级行业
    "index_market_representation_hist_sw"  # 申万指数-指数发布-指数体系-市场表征
    "index_style_index_hist_sw"  # 申万指数-指数发布-指数体系-风格指数

    "stock_board_industry_cons_ths"  # 同花顺-行业板块-成份股
    "stock_board_industry_index_ths"  # 同花顺-行业板块-指数日频数据

    "stock_board_industry_cons_em"  # 行业板块-板块成份
    "stock_board_industry_hist_em"  # 行业板块-历史行情
    "stock_board_industry_hist_min_em"  # 行业板块-分时历史行情
    "stock_board_industry_name_em"  # 行业板块-板块名称
    '''
    today = datetime.date.today()
    if today.weekday() >= 5:
        today = today.fromordinal(today.toordinal() - (today.weekday() - 4))
    # 股票-行业市盈率
    # {"证监会行业分类", "国证行业分类"}
    ak.stock_industry_pe_ratio_cninfo(symbol='证监会行业分类', date=today.strftime('%Y%m%d'))

    # 行业板块-历史行情
    ak.stock_board_industry_hist_em()

    # 行业板块-板块成份
    ak.stock_board_industry_cons_em()

    # ak.sw_index_daily()

    ak.sw_index_first_info()

    ak.sw_index_third_info()
    ak.sw_index_third_cons()

    df = ak.stock_sector_spot('行业')
    ak.sw_index_daily_indicator()

    # 申万市场表征数据  ??
    ak.sw_index_representation_spot()

    # 申万一级实时行情
    ak.sw_index_spot()

    ak.index_level_one_hist_sw('801120')

    ak.stock_sector_detail()


def eval_industry(thres=0.5):
    df = ak.sw_index_first_info()
    print(df.head())
    df2 = df[(df['TTM(滚动)市盈率分位数'] < thres) & (df['市净率分位数'] < thres)]

    # 成分股
    # ak.sw_index_third_cons("801120.SI")
    ak.sw_index_third_cons('801950.SI').sort_values(by='市值', ascending=False)

    return df2




eval_industry()


def eval_stock(code='600519'):
    '''
    指标: PB, PE, EPS, 夏普比率、最大回撤
    :param code:
    :return:
    '''
    # 财务指标数据 工行财报, 历史
    df = ak.stock_financial_analysis_indicator(code)

    # 财务摘要
    df = ak.stock_financial_abstract(code)

    # 三大财务报表
    df3 = ak.stock_financial_report_sina(code)





def eval_portfolio():
    '''
    指标: PB, PE, EPS, 夏普比率、最大回撤
    :return:
    '''

def test_api():
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20210907', adjust="")
    print(stock_zh_a_hist_df)

    # 期货展期收益率
    get_roll_yield_bar_df = ak.get_roll_yield_bar(type_method="date", var="RB", start_day="20180618", end_day="20180718")
    print(get_roll_yield_bar_df)

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