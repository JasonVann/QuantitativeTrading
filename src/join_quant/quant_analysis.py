
import datetime
from jqdata import finance

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

RISK_FREE_INTEREST_RATE = 0.02

class Retriever(object):
    def __init__(self):
        pass

    def get_data(self, code, start_date=None):
        if '.' in code:
            df = self.__get_stock_data(code)
            df['dt'] = df.index
        else:
            df = self.get_fund_data(code)

            df['dt'] = pd.to_datetime(df['day'])

        df['day_of_week'] = df.dt.dt.dayofweek + 1
        df['day_of_month'] = df.dt.dt.day
        df['week_of_year'] = df.dt.dt.weekofyear
        df['day_of_year'] = df.dt.dt.dayofyear
        df['month'] = df.dt.dt.month
        df['year'] = df.dt.dt.year

        df['is_end_of_year'] = df['year'] != df['year'].shift(-1)

        if start_date is not None:
            df = df[df.dt >= start_date]
            df.reset_index(inplace=True)

        return df

    @staticmethod
    def get_industries_for_stock(security_list, date):
        return get_industry(security=['000001.XSHE', '000002.XSHE'], date="2018-06-01")

    def get_fund_data(self, code):
        q = query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == code)
        df = finance.run_query(q)

        # df['price'] = df['net_value']
        df['price'] = df['sum_value']   # 累计单位净值＝单位净值＋成立以来每份累计分红派息的金额

        return df

    def __get_stock_data(self, code='600519.XSHG', end_date=None):
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        df = get_price(code, start_date='2010-01-01', end_date=end_date, frequency='daily', fields=['open',
                'close', 'low', 'high', 'volume', 'money', 'factor', 'high_limit','low_limit', 'avg',
                'pre_close', 'paused','open_interest'])
        df['price'] = df['close']
        return df

    def get_industry_perfomance(self):
        # TODO
        pass

    def get_stock_info(self):
        stock = get_security_info('000001.XSHE')
        print(stock.name)
        print(stock.industries)

    def get_stock_fundamentals(self, code='000001.XSHE'):
        # 查询平安银行2014年3-6月份的单季度报表
        q = query(
            income.statDate,
            income.code,

        ).filter(
            income.code == code,
        )

        ret = get_fundamentals(q, statDate='2014q2')
        return ret

    # 获取多年的季度度数据
    def get_fianancial_reports(self):

        def get_more_state_fund(q_object, year_list):
            df_list = []
            for year in year_list:
                rets = [get_fundamentals(q, statDate=str(year) + 'q' + str(i)) for i in range(1, 5)]
                df = pd.concat(rets).set_index('statDate')  # 个人习惯
                df_list.append(df)
            df_ = pd.concat(df_list, keys=year_list, axis=0)  # axis=1或axis=0,依据个人习惯
            return df_

        # https://www.joinquant.com/help/api/help#Stock:%E8%8E%B7%E5%8F%96%E5%8D%95%E5%AD%A3%E5%BA%A6%E5%B9%B4%E5%BA%A6%E8%B4%A2%E5%8A%A1%E6%95%B0%E6%8D%AE
        q = query(
            indicator.code,
            indicator.statDate,  # 财报统计的季度的最后一天

            income.total_operating_revenue,  # 营业总收入
            income.operating_revenue,  # 营业收入
            income.total_operating_cost,  # 营业总成本=主营业务成本+其他业务成本+利息支出+手续费及佣金支出+退保金+赔付支出净额
                # +提取保险合同准备金净额+保单红利支出+分保费用+营业税金及附加+销售费用+管理费用+财务费用+资产减值损失+其他
            income.basic_eps,

            indicator.inc_total_revenue_year_on_year,
            indicator.inc_net_profit_year_on_year, # 净利润同比增长率(%)
            indicator.eps,
            indicator.adjusted_profit,  # 公司正常经营损益之外的一次性或偶发性损益
            indicator.operating_profit,
            indicator.roa,  # 净利润*2/（期初总资产+期末总资产）
            indicator.roe,
            indicator.inc_return,  # 净资产收益率(扣除非经常损益)(%)
            indicator.gross_profit_margin, # 销售毛利率(%),	毛利/营业收入
            indicator.net_profit_margin,  # 销售净利率(%), 净利润/营业收入

            # 现金流量表
            cash_flow.goods_sale_and_service_render_cash,

            indicator.pubDate,
        ).filter(
            income.code.in_(['000001.XSHE', '601857.XSHG']))  # 带后缀.XSHE 深/.XSHG 沪

        df = get_more_state_fund(q, ['2022', '2023'])
        return


class Metric(object):
    def __init__(self):
        pass

    @staticmethod
    def get_drawdown(p):
        """
        计算净值回撤
        """
        T = len(p)
        hmax = [p[0]]
        for t in range(1, T):
            hmax.append(np.nanmax([p[t], hmax[t - 1]]))
        dd = [p[t] / hmax[t] - 1 for t in range(T)]

        return dd

    @staticmethod
    def calculate_return(df):
        df['daily_return'] = df['price'].pct_change()
        df['weekly_return'] = df['price'].pct_change(periods=5)
        df['monthly_return'] = df['price'].pct_change(periods=22)
        df['quarterly_return'] = df['price'].pct_change(periods=70)
        df['half_year_return'] = df['price'].pct_change(periods=121)
        df['yearly_return'] = df['price'].pct_change(periods=242)
        df['yearly_return3'] = df['price'].pct_change(periods=242 * 3)
        df['yearly_return5'] = df['price'].pct_change(periods=242 * 5)

        # df_year = df.groupby(df.dt.dt.year).apply(
        #     lambda group: group[group['day_of_year'] == group['day_of_year'].max()]
        # )

        df['dd'] = Metric.get_drawdown(df['price'])
        mdd = np.nanmin(df['dd'])  # 最大回撤

        annret = np.nanmean(df['daily_return']) * 242
        annvol = np.nanstd(df['daily_return']) * np.sqrt(242)
        sr = (annret - RISK_FREE_INTEREST_RATE) / annvol
        calmar = annret / -mdd

        df['mdd'] = mdd
        df['annret'] = annret
        df['annvol'] = annvol
        df['sr'] = sr
        df['calmar'] = calmar

        return df

    @staticmethod
    def calculate_yearly_return(df):

        df_year = df[df['is_end_of_year']]
        df_year['yearly_return'] = df_year['price'].pct_change() * 100

        return df_year


class Strategy(object):
    def __init__(self):
        pass

    @staticmethod
    def calculate_pe(df, pe_rank_window=242*5):
        pctrank = lambda x: x.rank(pct=True).iloc[-1]
        df['pe_rank'] = df['index_pe'].rolling(window=pe_rank_window).apply(pctrank)


portfolio = {
            # '沪深300': '510300', 'gold': '518880',
            '广发中债国开行债券': '003376', '鹏华丰禄债券': '003547',

            '华夏沪深300': '000051', '易方达上证50A': '110003',
            '富国上证综指': '100053', '华夏科创50': '011612',
            '富国中证煤炭': '161032', '富国中证红利': '009052',
            '交银施罗德中证海外互联': '164906', '天弘恒生科技': '012349',

            '博时标普500': '050025', '广发纳斯达克100': '006479',
            '国泰黄金ETF': '000218', '广发道琼斯美国石油开发与生产指数': '162719',
            }

index_list = {
    ''
}

stock_list = {'茅台': '600519.XSHG',
                 '中国神华': '601088.XSHG',
                 '中石油': '601857.XSHG'
              }

def test_retrieval():
    retrieval = Retriever()
    df = retrieval.get_data(portfolio['华夏沪深300'], start_date='2019-01-01')
    df2 = retrieval.get_data(portfolio['茅台'], start_date='2019-01-01')


def get_portfolio_snapshot(start_date=None):
    retrieval = Retriever()
    result = None
    for name, code in portfolio.items():
        print(name, code)
        df = retrieval.get_data(code, start_date=start_date)
        print(df.tail())
        df2 = Metric.calculate_return(df)
        df2['name'] = name
        df2['code'] = code
        df_temp = df2[['dt', 'name', 'code', 'price', 'daily_return', 'weekly_return', 'monthly_return', 'quarterly_return',
             'half_year_return', 'yearly_return','yearly_return3', 'yearly_return5',
                       'annret', 'annvol', 'sr', 'mdd', 'calmar']].tail(n=1)
        if result is None:
            result = df_temp
        else:
            result = result.append(df_temp)

    return result


df_portfolio = get_portfolio_snapshot(start_date='2019-03-21')

today = datetime.datetime.now()

df_portfolio.to_csv('./data/portfolio_{}.csv'.format(today.strftime('%Y%m%d_%H%M')))


def compare_target_returns():
    retrieval = Retriever()

    # TODO fix date misalignment
    df_all = None
    last_names = []
    for name, code in portfolio.items():
        df = retrieval.get_data(code)
        df_year = Metric.calculate_yearly_return(df)
        df_year[code + '_yoy'] = df_year['yearly_return']
        # TODO fix merge
        if df_all is not None:
            df_all = df_all[['dt'] + last_names].merge(df_year[['dt', name + '_yoy']], on='dt', how='left')
        else:
            df_all = df_year
        last_names.append(name + '_yoy')

    return df_all


# df_all = compare_target_returns()
# df_all.plot(x='dt')



# df_moutai_year = calculate_return(df_moutai)
# df_moutai_year['moutail_yoy'] = df_moutai_year['yearly_return']
#
# df_hs300_year = calculate_return(df)
# df_hs300_year['hs300_yoy'] = df_moutai_year['yearly_return']

def annual_return(df, is_mutual_fund=False):
    df_end_of_year = df.loc[df['week_of_year'] == 52][df['day_of_week'] == 5]

    if is_mutual_fund:
        df_end_of_year['YoY'] = df_end_of_year['refactor_net_value'].pct_change()
    else:
        df_end_of_year['YoY'] = df_end_of_year['close'].pct_change()
    return df_end_of_year


def plot_df(df, is_mutal_fund=False):
    plt.figure(figsize=[18, 5])
    # df_end_of_year['net_value'].plot(label='net_value')

    if is_mutal_fund:
        df.plot(x='dt', y='refactor_net_value')
    else:
        df.plot(x='dt', y='close')

    df.plot(x='dt', y='YoY')
    plt.show()


def test_wine():
    df, df_end_of_year = get_data(code='161725', is_mutual_fund=True)
    print('Next is moutai')
    df, df_end_of_year = get_data(code='600519.XSHG', is_mutual_fund=False)


# test_wine()

