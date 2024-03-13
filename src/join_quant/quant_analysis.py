import numpy as np
import pandas as pd
from jqdata import finance
from matplotlib import pyplot as plt


from jqdata import finance
class Retrieval(object):
    import pandas as pd

    def __init__(self):
        pass

    def get_data(self, code):
        if '.' in code:
            return self.get_stock_data(code)
        else:
            return self.get_fund_data(code)

    def get_fund_data(self, code):

        q = query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == code)
        df = finance.run_query(q)

        df['dt'] = pd.to_datetime(df['day'])
        df['day_of_week'] = df.dt.dt.dayofweek + 1
        df['day_of_month'] = df.dt.dt.day
        df['week_of_year'] = df.dt.dt.weekofyear
        df['day_of_year'] = df.dt.dt.dayofyear
        df['month'] = df.dt.dt.month

        df['price'] = df['net_value']

        return df

    def get_stock_data(self, code='600519.XSHG', end_date=None):
        df = get_price(code, start_date='2010-01-01', end_date='2024-03-13', frequency='daily')

        price_column_name = 'close'

        df['dt'] = df.index
        df['day_of_week'] = df.index.dayofweek + 1
        df['day_of_month'] = df.index.day
        df['week_of_year'] = df.index.weekofyear
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month

        df['price'] = df['close']
        return df


target_lookup = {'hs300': '510300', 'gold': '518880', 'moutai': '600519.XSHG'}

# retrieval = Retrieval()
# df = retrieval.get_fund_data(target_lookup['hs300'])
#
# df_moutai = retrieval.get_stock_data()


def get_data(code=None, is_mutual_fund=False, to_save=False):
    import pandas as pd

    if code is None:
        code = '510300.XSHG'

    if is_mutual_fund:
        from jqdata import finance
        q = query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == code)
        df = finance.run_query(q)
        price_column_name = 'net_value'

        df['dt'] = pd.to_datetime(df['day'])
        df['day_of_week'] = df.dt.dt.dayofweek + 1
        df['day_of_month'] = df.dt.dt.day
        df['week_of_year'] = df.dt.dt.weekofyear
        df['day_of_year'] = df.dt.dt.dayofyear
        df['month'] = df.dt.dt.month
    else:
        # 获取股票510300.XSHG2015年1月的日级交易数据
        df = get_price(code, start_date='2010-01-01', end_date='2021-10-21', frequency='daily')
        # df = get_price(code, start_date='2021-09-01', end_date='2021-10-20', frequency='daily')
        price_column_name = 'close'

        df['dt'] = df.index
        df['day_of_week'] = df.index.dayofweek + 1
        df['day_of_month'] = df.index.day
        df['week_of_year'] = df.index.weekofyear
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month

    df_end_of_year = annual_return(df, is_mutual_fund)
    plot_df(df_end_of_year, is_mutual_fund)
    return df, df_end_of_year


def calculate_return(df, code):
    df['daily_return'] = df['price'].pct_change()
    df['yearly_return'] = df['price'].pct_change(periods=242)

    df_year = df.groupby(df.dt.dt.year).apply(
        lambda group: group[group['day_of_year'] == group['day_of_year'].max()]
    )

    df_year['yearly_return'] = df_year['price'].pct_change() * 100
    df_year[code+'_yoy'] = df_year['yearly_return']

    return df_year


def compare():
    retrieval = Retrieval()

    # TODO
    df_temp = None
    # for name, code in target_lookup.items():
    #     df = retrieval.get_data(code)
    #     df_year = calculate_return(df)

    df_hs300 = retrieval.get_data(target_lookup['hs300'])
    df_hs300_year = calculate_return(df_hs300, 'hs300')

    df_gold = retrieval.get_data(target_lookup['gold'])
    df_gold_year = calculate_return(df_gold, 'gold')

    df_moutai = retrieval.get_data(target_lookup['moutai'])
    df_moutai_year = calculate_return(df_moutai, 'moutai')

    df_all = df_hs300_year[['dt', 'hs300_yoy']].merge(df_gold_year[['dt', 'gold_yoy']], on='dt', how='left')\
        .merge(df_moutai_year[['dt', 'moutai_yoy']], on='dt', how='left')

    return df_all, df_hs300_year, df_gold_year, df_moutai_year


df_all, df_all, df_hs300_year, df_gold_year, df_moutai_year = compare()
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

