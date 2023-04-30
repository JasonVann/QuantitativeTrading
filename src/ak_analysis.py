import akshare as ak
import datetime
import pandas as pd

pd.set_option('display.max_columns',300)
pd.set_option('display.max_rows', 300)

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


# eval_industry()


def eval_stock(code='601225.SH', sector='801950.SI'):
    '''
    指标: PB, PE, EPS, 夏普比率、最大回撤
    :param code:
    :return:
    '''
    # code = '601225.SH'
    # sector = '801950.SI'
    int_code = code.split('.')[0]
    sector_df = ak.sw_index_third_cons(sector).sort_values(by='市值', ascending=False)
    temp_df1 = sector_df[sector_df['股票代码'] == code]

    # 财务指标数据 工行财报, 历史
    fin_df = ak.stock_financial_analysis_indicator(int_code)
    fin_df['股票代码'] = code
    temp_df2 = fin_df[['股票代码', '日期', '每股收益_调整后(元)', '资产负债率(%)', '净资产收益率(%)', '净利润增长率(%)', '主营业务利润率(%)', '总资产利润率(%)',
            '应收账款周转率(次)', '存货周转率(次)', '总资产周转率(次)']]

    res_df = pd.merge(temp_df1, temp_df2.head(1), on="股票代码", how="left")

    # 财务摘要
    fin_df2 = ak.stock_financial_abstract(int_code)
    temp_df3 = fin_df2[(fin_df2['指标'] == '营业总收入') | (fin_df2['指标'] == '净利润') | (fin_df2['指标'] == '经营现金流量净额') |
                       (fin_df2['指标'] == '毛利率') |
                       (fin_df2['指标'] == '流动比率') | (fin_df2['指标'] == '速动比率') | (fin_df2['指标'] == '股东权益合计(净资产)')]

    a = temp_df3.iloc[:, [1,2]]
    a = a.set_index('指标')
    a = a.T
    a['股票代码'] = code
    a['经营现金流量净额'] = a['经营现金流量净额'].astype('float') / (1e8)
    a['营业总收入'] = a['营业总收入'].astype('float') / (1e8)
    a['净利润'] = a['净利润'].astype('float') / (1e8)
    a['股东权益合计(净资产)'] = a['股东权益合计(净资产)'].astype('float') / (1e8)

    res_df2 = pd.merge(res_df, a, on="股票代码", how="left")

    # 三大财务报表
    fin_df3 = ak.stock_financial_report_sina(int_code)

    a = fin_df3[['流动资产合计', '非流动资产', '应收账款', '无形资产', '商誉']].astype("float") / (1e8)
    a['股票代码'] = code
    res_df3 = pd.merge(res_df2, a.head(1), on="股票代码", how="left")

    score_df = eval_stock_metric(res_df3)

    return score_df


def eval_stock_metric(df):
    total_score = 0
    a = float(df[['资产负债率(%)']].values)
    if a < 35:
        score = 100
    elif a > 50:
        score = 0
    else:
        score = 100 - 50/15 * (a-35)
    df['资产负债率_score'] = score
    total_score += score * 0.05

    a = float(df[['流动比率']].values)
    b = float(df[['速动比率']].values)
    if a >= 1.5 and b > 1:
        score = 100
    elif a >= 1.5 or b > 1:
        score = 75
    else:
        score = 0
    df['偿债能力_score'] = score
    total_score += score * 0.05

    # TODO
    a = float(df[['存货周转率(次)']].values)
    b = float(df[['总资产周转率(次)']].values)
    c = float(df[['应收账款周转率(次)']].values)
    # if a >= 1.5 and b > 1:
    #     score = 100
    # elif a >= 1.5 or b > 1:
    #     score = 75
    # else:
    #     score = 0
    score = 0
    df['经营能力_score'] = score
    total_score += score * 0.05

    a = float(df[['净资产收益率(%)']].values)
    if a > 16:
        score = 100
    elif a < 6:
        score = 0
    else:
        score = 50 + 16 / 6 * a
    df['ROE_score'] = score
    total_score += score * 0.05

    a = float(df[['净利润增长率(%)']].values)
    if a > 30:
        score = 100
    elif a < 0:
        score = 0
    else:
        score = 50 + 50/30 * a
    df['净利润增长率_score'] = score
    total_score += score * 0.05

    num = float(df[['无形资产']].values)
    denom = float(df[['股东权益合计(净资产)']].values)
    a = num/denom
    if a < 3:
        score = 100
    elif a > 12:
        score = 0
    else:
        score = 100 - 50 / (12 - 3) * (a - 3)
    df['无形资产占比_score'] = score
    total_score += score * 0.05

    a = float(df[['市净率']].values)
    if a < 1:
        score = 100
    elif a > 2.5:
        score = 0
    else:
        score = 100 - 50 / (2.5-1) * (a - 1)
    df['市净率_score'] = score
    total_score += score * 0.1

    a = float(df[['市盈率']].values)
    if a < 10:
        score = 100
    elif a > 25:
        score = 0
    else:
        score = 100 - 50 / (25 - 10) * (a - 10)
    df['市盈率_score'] = score
    total_score += score * 0.1

    df['total_score'] = total_score
    df['max_score'] = 0.45

    return df


# stock_df = eval_stock(code='601225.SH', sector='801950.SI')


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


def rank_stocks():
    res_df = []
    cands = [('601225.SH', '801950.SI', '陕西煤业'), ('601088.SH', '801950.SI', '中国神华'),
             ('600188.SH', '801950.SI', '兖矿能源'), ('601898.SH', '801950.SI', '中煤能源'),
             ('601857.SH', '801960.SI', '中国石油'),
             ('601899.SH', '801050.SI', '紫金矿业'),
             ('600519.SH', '801120.SI', '贵州茅台'), ('000858.SZ', '801120.SI', '五粮液'),
             ('002594.SZ', '801880.SI', '比亚迪'),
             ('000651.SZ', '801110.SI', '格力电器'), ('000333.SZ', '801110.SI', '美的集团'),
             ]
    for stock, industry, name in cands:
        stock_df = eval_stock(code=stock, sector=industry)
        res_df.append(stock_df)

    rank_df = pd.concat(res_df)
    return rank_df


rank_df = rank_stocks()