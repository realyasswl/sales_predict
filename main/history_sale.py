import sys

sys.path.insert(0, "d:\\work\\potential_ml\\greenworks\\py")

from openpyxl import load_workbook
from main import df, start_week, end_week_obj
from main.actual_sale import items, sales, gw_fcst
from datetime import datetime, timedelta as td

performance = load_workbook("D:\\deeplearning\\greenworks\\performance.xlsx")
# item_week:summed_number_per_week
temp_result = {}
# item:[summed_number_per_week, ...]
result = {}

for year in range(3):
    table = "TABLE - POS Data {0:d}".format(year + 2015)
    # print(table)
    wb = performance[table]
    i = 0
    for row in wb.rows:
        if i == 0:
            i = 1
            continue

        item = row[4].value
        week = row[6].value
        unit = row[8].value
        key = "{0:d}_{1:s}".format(item, week.strftime(df))
        try:
            temp_result[key] = temp_result[key] + unit
        except:
            temp_result[key] = unit

for item in items:
    numbers = []
    date_in_loop = datetime.strptime(start_week, df)
    while date_in_loop <= end_week_obj:
        try:
            numbers.append(temp_result["{0:d}_{1:s}".format(item, date_in_loop.strftime(df))])
        except:
            numbers.append(0)
        date_in_loop = date_in_loop + td(days=7)
    result[item] = numbers


# for i in result:
#     print(i, len(result[i]), result[i])

def mape(ori, pred):
    sum = 0
    abs_err = 0
    for i in range(len(ori)):
        sum = sum + ori[i]
        abs_err = abs_err + abs(ori[i] - pred[i])
    return 100 * abs_err / sum

print("load data 1")
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import arma_order_select_ic

yhsum = 0
yhssum = 0
gwsum = 0
gwssum = 0

if __name__=="__main__":
    for item in items:
        try:
            print("================================================")
            print("item[{0:d}]========================".format(item))
            ind = items.index(item)
            temp = [float(x) for x in result[item]]
            training = temp[:-12]

            to_be_add = temp[-12:]
            try:
                testing = [float(x) for x in sales[ind]]
            except ValueError:
                continue
            gw_fcsting = gw_fcst[ind][:]
            predictions = []
            print(testing)
            res = arma_order_select_ic(training, ic=['aic', 'bic'], trend='nc')
            for t in range(len(testing)):
                # res.aic_min_order
                # res.bic_min_order
                model = ARIMA(training, order=(res.aic_min_order[0], 1, res.aic_min_order[1]))
                model_fit = model.fit(disp=0)
                output = model_fit.forecast(steps=13)
                # print(len(output))
                yhat = output[0][0]
                obs = testing[t]
                predictions.append(yhat)
                training.append(to_be_add[t])
            yhmape = mape(testing, predictions)
            gwmape = mape(testing, gw_fcsting)
            yhsum = yhsum + yhmape
            yhssum = yhssum + yhmape * yhmape
            gwsum = gwsum + gwmape
            gwssum = gwssum + gwmape * gwmape
            print("YH_MAPE[{0:.3f}]".format(yhmape), predictions)
            print("GW_MAPE[{0:.3f}]".format(gwmape), gw_fcsting)
        except:
            pass
    print(yhsum, gwsum, yhssum, gwssum)
