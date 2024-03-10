#导入需要的库
import pandas as pd
import seaborn as sns
import numpy as np

'''
get_price() 
get_all_securities() 
get_index_stocks() 
get_industry_stocks()

get_price - 获取历史数据

get_extras - 获取基金净值/期货结算价等 
get_fundamentals - 查询财务数据 
get_index_stocks - 获取指数成份股 
get_industry_stocks - 获取行业成份股 
get_concept_stocks - 获取概念成份股 
get_all_securities - 获取所有标的信息 
get_security_info - 获取单个标的信息 
jqdata.get_all_trade_days - 获取所有交易日 
jqdata.get_trade_days - 获取指定范围交易日 
jqdata.get_money_flow - 获取资金流信息
'''

from jqdata import finance

def demo():
    q=query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code=="320013")
    df2=finance.run_query(q)

    code = '600519.XSHG'
    df_moutai = get_price(code, start_date='2010-01-01', end_date='2021-10-21', frequency='daily')


def get_data_fund(code=None):
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
    df['year'] = df.dt.dt.year

    return df


df_gold = get_data_fund('518880')


def calculate_return(df, price_column_name='net_value'):
    import numpy as np
    df['year_start'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 2) & (df['month'] == 1), 1, 0)
    # df['year_end'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] >= 29) & (df['month'] == 12), 1, 0)

    # df['year_end'] = np.where(df.groupby(df.dt.dt.year).apply(
    #     lambda group: group[group['day_of_year'] == group['day_of_year'].max() ]
    # ), 1, 0)

    start_of_year = df.groupby(df.dt.dt.year).apply(
        lambda group: group[group['day_of_year'] == group['day_of_year'].min()]
    )

    end_of_year = df.groupby(df.dt.dt.year).apply(
        lambda group: group[group['day_of_year'] == group['day_of_year'].max() ]
    )

    df2 = pd.merge(start_of_year, end_of_year, on="year", how="left")

    df2['yoy'] = df2['net_value_y']/df2['net_value_x'] - 1

    return df2

df_gold2 = calculate_return(df_gold)


def get_data(code=None, is_mutual_fund=False, to_save=False):
    import pandas as pd

    RATIO = 0.999

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

    # df['total_day_in'] = df['day_in'].cumsum()
    # df['total_day_amount'] = df['day_amount'].cumsum()
    # df['total_day_value'] = df['total_day_amount'] * df['close']
    # df['profit_day'] = df['total_day_value'] - df['total_day_in']
    # df['profit_ratio_day'] = df['profit_day'] / df['total_day_in']

    def add_column(name):
        df['{}_amount'.format(name)] = df['{}_in'.format(name)] / df[price_column_name]
        df['total_{}_in'.format(name)] = df['{}_in'.format(name)].cumsum()
        df['total_{}_amount'.format(name)] = df['{}_amount'.format(name)].cumsum()
        df['total_{}_value'.format(name)] = df['total_{}_amount'.format(name)] * df[price_column_name]
        df['cumu_profit_{}'.format(name)] = 0
        df['profit_{}'.format(name)] = df['total_{}_value'.format(name)] - df['total_{}_in'.format(name)]
        df['profit_ratio_{}'.format(name)] = df['profit_{}'.format(name)] / df['total_{}_in'.format(name)]

    invest_amount = 100

    # df['all_in'] = np.where(df.index == 0, df.shape[0] * 100 * 0.999, 0)
    df['all_in'] = np.where(df.index == df[df[price_column_name] > 0].index[0], df.shape[0] * invest_amount * 0.999, 0)
    add_column('all')

    df['day_in'] = np.where(df[price_column_name] > 0, invest_amount * 0.999, 0)
    # df['day_amount'] = invest_amount / df['close']
    add_column('day')

    # df['year_in'] = np.where(df['week_of_year'] == 1 and df['day_of_week'] == 1, 220 * invest_amount * RATIO, 0)
    # df['year_in'] = np.where(df['day_of_year'] == 4, 220 * invest_amount * RATIO, 0)
    # add_column('year')

    # df['janurary_in'] = np.where(df['day_of_year'] == 4, 220 * invest_amount * RATIO, 0)
    df['janurary_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 1), 220 * invest_amount * RATIO, 0)
    add_column('janurary')

    df['february_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 2), 220 * invest_amount * RATIO, 0)
    add_column('february')

    df['march_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 3), 220 * invest_amount * RATIO, 0)
    add_column('march')

    df['april_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 4), 220 * invest_amount * RATIO, 0)
    add_column('april')

    df['may_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 8) & (df['month'] == 5), 220 * invest_amount * RATIO, 0)
    add_column('may')

    df['june_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 6), 220 * invest_amount * RATIO, 0)
    add_column('june')

    df['july_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 9) & (df['month'] == 7), 220 * invest_amount * RATIO, 0)
    add_column('july')

    df['august_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 8), 220 * invest_amount * RATIO, 0)
    add_column('august')

    df['september_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 9), 220 * invest_amount * RATIO, 0)
    add_column('september')

    df['octoboer_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 8) & (df['month'] == 10), 220 * invest_amount * RATIO, 0)
    add_column('octoboer')

    df['november_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 11), 220 * invest_amount * RATIO, 0)
    add_column('november')

    df['december_in'] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == 4) & (df['month'] == 12), 220 * invest_amount * RATIO, 0)
    add_column('december')

    df['monday_in'] = np.where((df[price_column_name] > 0) & (df['day_of_week'] == 1), 5 * invest_amount * RATIO, 0)
    add_column('monday')

    df['tuesday_in'] = np.where((df[price_column_name] > 0) & (df['day_of_week'] == 2), 5 * invest_amount * RATIO, 0)
    add_column('tuesday')

    df['wednesday_in'] = np.where((df[price_column_name] > 0) & (df['day_of_week'] == 3), 5 * invest_amount * RATIO, 0)
    add_column('wednesday')

    df['thursday_in'] = np.where((df[price_column_name] > 0) & (df['day_of_week'] == 4), 5 * invest_amount * RATIO, 0)
    add_column('thursday')

    df['friday_in'] = np.where((df[price_column_name] > 0) & (df['day_of_week'] == 5), 5 * invest_amount * RATIO, 0)
    add_column('friday')

    for i in range(1, 31):
        df['month_d{}_in'.format(i)] = np.where((df[price_column_name] > 0) & (df['day_of_month'] == i), 22 * invest_amount * RATIO, 0)
        add_column('month_d{}'.format(i))


    plt.figure(figsize=[18, 5])
    # df['profit_ratio_day'].plot(label='day')
    # df['profit_ratio_monday'].plot(label='monday')
    # df['profit_ratio_tuesday'].plot(label='tuesday')
    # df['profit_ratio_wednesday'].plot(label='wednesday')
    # df['profit_ratio_thursday'].plot(label='thursday')
    # df['profit_ratio_friday'].plot(label='friday')

    for name in ['janurary', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                 'octoboer', 'november', 'december', 'day']:
        df['profit_ratio_{}'.format(name)].plot(label=name)

    # for i in range(1, 30):
    #     df['profit_ratio_month_d{}'.format(i)].plot(label='month_d{}'.format(i))

    plt.legend(loc='best')

    x = []
    y = []
    for name in ['all', 'janurary', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                 'octoboer', 'november', 'december',  'day', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
        x.append(name)
        y.append(df[['profit_ratio_{}'.format(name)]][-1:].iloc[0, 0])
    for name in range(1, 30):
        x.append('month_d{}'.format(name))
        y.append(df[['profit_ratio_month_d{}'.format(name)]][-1:].iloc[0, 0])
    df_bar = pd.DataFrame({'定投方式': x, '盈利': y})
    print(df_bar.min(), df_bar.max())
    print(df_bar)

    df_bar.plot.bar(x='定投方式', rot=0)

    if to_save:
        pd.set_option('display.max_columns', None)
        df.to_csv('{}.csv'.format(code))

    return df



df_moutai = get_data(code='600519.XSHG')

