
from jqdata import finance
from jqdata import finance

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


class Retrieval(object):
    import pandas as pd

    def __init__(self):
        pass

    def get_data(self, code):
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

        return df

    def get_fund_data(self, code):
        q = query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == code)
        df = finance.run_query(q)

        df['price'] = df['net_value']

        return df

    def __get_stock_data(self, code='600519.XSHG', end_date=None):
        df = get_price(code, start_date='2010-01-01', end_date='2024-03-13', frequency='daily', fields=['open',
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
            income.basic_eps,
            cash_flow.goods_sale_and_service_render_cash
        ).filter(
            income.code == code,
        )

        ret = get_fundamentals(q, statDate='2014q2')
        return ret


portfolio = {'沪深300': '510300', 'gold': '518880',
                 '华夏沪深300': '000051', '易方达上证50A': '110003',
                '博时标普500': '050025', '广发纳斯达克100': '006479',
                 '茅台': '600519.XSHG',
                 '中国神华': '601088.XSHG',
                 '中石油': '601857.XSHG'}

retrieval = Retrieval()
df = retrieval.get_data(portfolio['华夏沪深300'])
df = retrieval.get_data(portfolio['茅台'])


def calculate_return(df, code):
    df['daily_return'] = df['price'].pct_change()
    df['weekly_return'] = df['price'].pct_change(periods=5)
    df['monthly_return'] = df['price'].pct_change(periods=22)
    df['quarterly_return'] = df['price'].pct_change(periods=70)
    df['yearly_return'] = df['price'].pct_change(periods=242)

    # df_year = df.groupby(df.dt.dt.year).apply(
    #     lambda group: group[group['day_of_year'] == group['day_of_year'].max()]
    # )

    df_year = df[df['is_end_of_year']]

    df_year['yearly_return'] = df_year['price'].pct_change() * 100
    df_year[code+'_yoy'] = df_year['yearly_return']

    return df_year, df


def compare_target_returns():
    retrieval = Retrieval()

    # TODO fix date misalignment
    df_all = None
    last_names = []
    for name, code in portfolio.items():
        df = retrieval.get_data(code)
        df_year, df2 = calculate_return(df, name)
        # TODO fix merge
        if df_all is not None:
            df_all = df_all[['dt'] + last_names].merge(df_year[['dt', name + '_yoy']], on='dt', how='left')
        else:
            df_all = df_year
        last_names.append(name + '_yoy')

    return df_all


df_all = compare_target_returns()
df_all.plot(x='dt')



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


test_wine()

