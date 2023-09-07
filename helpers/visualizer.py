import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.dates as mdates
from datetime import datetime
import os

binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},  
        "edge": {"up": "#3dc985", "down": "#ef4f60"},  
        "wick": {"up": "#3dc985", "down": "#ef4f60"},  
        "ohlc": {"up": "green", "down": "red"},
        "volume": {"up": "#247252", "down": "#82333f"},  
        "vcedge": {"up": "green", "down": "red"},  
        "vcdopcod": False,
        "alpha": 1,
    },
    "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
    "facecolor": "#1b1f24",
    "gridcolor": "#2c2e31",
    "gridstyle": "--",
    "y_on_right": True,
    "rc": {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": "#474d56",
        "axes.titlecolor": "red",
        "figure.facecolor": "#161a1e",
        "figure.titlesize": "x-large",
        "figure.titleweight": "semibold",
    },
    "base_mpf_style": "binance-dark",
}

def _add_candlestick_labels(ax, ohlc):
    transform = ax.transData.inverted()
    text_pad = transform.transform((0, 10))[1] - transform.transform((0, 0))[1]
    percentages = 100. * (ohlc.close - ohlc.open) / ohlc.open
    kwargs = dict(horizontalalignment='center', color='#FFFFFF', fontsize=6)
    for i, (idx, val) in enumerate(percentages.items()):
        if val != np.nan:
            row = ohlc.loc[idx]
            open = row.open
            close = row.close
            if open < close:
                ax.text(i, row.high + text_pad, np.round(val, 1), verticalalignment='bottom', **kwargs)
            elif open > close:
                ax.text(i, row.low - text_pad, np.round(val, 1), verticalalignment='top', **kwargs)



def draw_candlesticks(candles: list, type_labels: str, mark_index: int):
    # Convert the candlesticks data into a pandas DataFrame
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=False).dt.tz_localize('UTC').dt.tz_convert('Europe/London')
    df.set_index('timestamp', inplace=True)
    figsize = (10, 6)
    # Plot the candlestick chart using mpf.plot()
    fig, axlist = mpf.plot(df, type='candle', style=binance_dark, title=f'Type: {type_labels}', returnfig=True, figsize=figsize)

    # Add percentage labels to the candlestick chart
    # _add_candlestick_labels(axlist[0], df)

    # if type_labels == 'up':
    #     axlist[0].annotate('MARK', (mark_index, df.iloc[mark_index]['open']), xytext=(mark_index, df.iloc[mark_index]['open']-10),
    #                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    # elif type_labels == 'down':
    #     axlist[0].annotate('MARK', (mark_index, df.iloc[mark_index]['open']), xytext=(mark_index, df.iloc[mark_index]['open']+10),
    #                     arrowprops=dict(facecolor='black', arrowstyle='->'))

    # Display the chart
    mpf.show()

def draw_graph(values):
    periods = range(1, len(values) + 1)
    plt.plot(periods, values)
    plt.xlabel('Period')
    plt.ylabel('Value')
    plt.title('Graph for Values')
    plt.show()



# def plot_time_series(data_list: list, save_pic: bool, index: int):
#     path = f'pic/{datetime.now().date().strftime("%Y-%m-%d")}'
#     timestamps = [item[0] for item in data_list]
#     values = [item[1] for item in data_list]
    
#     # Преобразование timestamp в формат даты
#     dates = [datetime.fromtimestamp(ts/1000) for ts in timestamps]
    
#     # Создание графика
#     fig, ax = plt.subplots()
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
#     plt.xticks(rotation=45) # Поворот дат для лучшей читаемости
#     periods = range(1, len(values) + 1)
#     # Построение графика
#     ax.plot(dates, values)
    
#     # Добавление подписей и заголовка
#     plt.xlabel('Period')
#     plt.ylabel('Value')
#     plt.title('Graph for Values')

#      # Add periods close to the dates
#     for i, (date, value) in enumerate(zip(dates, values)):
#         if i == index:
#             ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')
#         elif i == index + 1:
#             ax.axvline(x=date, linestyle='--', color='red')
    
#     for i, (date, value) in enumerate(zip(dates, values)):
#         if i % 50 == 0:
#             ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')
#     # Отображение графика
#     plt.tight_layout()

#     if save_pic:
#         if not os.path.exists(path):
#             os.makedirs(path)
#         end_path = f'{path}/{datetime.now().timestamp()}.png'
#         plt.savefig(end_path)
#         return end_path
#     return None

def plot_time_series(data_list: list, save_pic: bool, date_line: str):
    path = f'pic/{datetime.now().date().strftime("%Y-%m-%d")}'
    timestamps = [item[0] for item in data_list]
    values = [item[1] for item in data_list]
    
    dates = [datetime.fromtimestamp(ts/1000) for ts in timestamps]
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    periods = range(1, len(values) + 1)
    
    ax.plot(dates, values)
    
    plt.xlabel('Period')
    plt.ylabel('Value')
    plt.title('Graph for Values')

    for i, (date, value) in enumerate(zip(dates, values)):
        if i % 25 == 0:
            ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')

    # Convert date_line to a datetime object
    date_line = datetime.strptime(date_line, '%d.%m.%y')
    # Determine the index of the date_line in the dates list
    try:
        date_line_index = next(i for i, date in enumerate(dates) if date > date_line)
    except StopIteration:
        date_line_index = 0

    # Draw a red line after the date_line
    if date_line_index != 0:
        for i, (date, value) in enumerate(zip(dates, values)):
            if i == date_line_index:
                ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')
            elif i == date_line_index + 1:
                ax.axvline(x=date, linestyle='--', color='red')
    
    plt.tight_layout()

    if save_pic:
        if not os.path.exists(path):
            os.makedirs(path)
        end_path = f'{path}/{datetime.now().timestamp()}.png'
        plt.savefig(end_path)
        return end_path
    return None