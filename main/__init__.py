import datetime
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import pickle

start_week = "2015/2/6"
end_week = "2018/2/2"
df = "%Y/%m/%d"
end_week_obj = datetime.datetime.strptime(end_week, df)

result = None
items = None
sales = None
gw_fcst = None

base_folder = "D:\\work\\potential_ml\\greenworks\\py\\main\\{0:s}"

with open(base_folder.format('result'), 'rb') as f:
    result = pickle.load(f)
with open(base_folder.format('items'), 'rb') as f:
    items = pickle.load(f)
with open(base_folder.format('sales'), 'rb') as f:
    sales = pickle.load(f)
with open(base_folder.format('gw_fcst'), 'rb') as f:
    gw_fcst = pickle.load(f)


def draw(training, item):
    fig, axes = plt.subplots(1, 2, figsize=(15, 4))
    weeks = [i for i in range(len(training))]
    diff = np.diff(np.log(training))
    # Levels
    axes[0].plot(weeks, training)
    axes[0].set(title='{0:d} sales'.format(item))

    # Log difference
    axes[1].plot(weeks[1:], diff)
    axes[1].hlines(0, weeks[0], weeks[-1], 'r')
    axes[1].set(title='{0:d} - difference of sales'.format(item))

    fig, axes = plt.subplots(1, 2, figsize=(15, 4))

    sm.graphics.tsa.plot_acf(diff, lags=52, ax=axes[0])
    sm.graphics.tsa.plot_pacf(diff, lags=52, ax=axes[1])


def draw1(temp, training, testing, predictions, gwfcst, title):
    print(title)
    fig, ax = plt.subplots(figsize=(13, 8))
    weeks = [i for i in range(len(temp) + len(predictions))]
    ax.plot(weeks[len(temp):len(temp) + len(predictions)], predictions, color="#123456", label="yh_pred")
    ax.plot(weeks[len(temp): len(temp) + len(testing)], testing, color="#ab9641", label="ty_sale")
    ax.plot(weeks[:len(temp)], temp, color="#e0e0e0", label="ly_sale")
    ax.plot(weeks[:len(training)], training, color="#999999", label="training")
    ax.plot(weeks[len(temp):len(temp) + len(gwfcst)], gwfcst, color="#f012e6", label="gw_pred")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    ax.set(title=title)
    fig.savefig(title)


def float_list_2_string(flst, sprt=","):
    return sprt.join(["{0:.0f}".format(f) for f in flst])
