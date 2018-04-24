import sys

sys.path.insert(0, "d:\\work\\potential_ml\\greenworks\\py")

from openpyxl import load_workbook
from main import df, start_week, end_week_obj
from datetime import datetime, timedelta as td

yhsum = 0
yhssum = 0
gwsum = 0
gwssum = 0


def mape(ori, pred):
    sum = 0
    abs_err = 0
    for i in range(len(ori)):
        sum = sum + ori[i]
        abs_err = abs_err + abs(ori[i] - pred[i])
    return 100 * abs_err / sum


def punish_negative(ori, pred, negative_rate=3):
    sum = 0
    err = 0
    for i in range(len(ori)):
        sum = sum + ori[i]
        diff = pred[i] - ori[i]
        err = err + (diff if diff > 0 else negative_rate * (0 - diff))
    return 100 * err / sum


if __name__ == '__main__':
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

    items = None
    import pickle

    with open('items', 'rb') as f:
        items = pickle.load(f)
    for item in items:
        numbers = []
        date_in_loop = datetime.strptime(start_week, df)
        while date_in_loop <= end_week_obj:
            try:
                val = temp_result["{0:d}_{1:s}".format(item, date_in_loop.strftime(df))]
                # val = 0 if val < 0 else val
                numbers.append(val)
            except:
                numbers.append(0)
            date_in_loop = date_in_loop + td(days=7)
        result[item] = numbers

    print("load data 1")

    with open('result', 'wb') as f:
        pickle.dump(result, f)
