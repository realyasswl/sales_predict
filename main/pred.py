from main.actual_sale import items, sales, gw_fcst
from main.history_sale import result, mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters

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
        predictions = holtWinters(temp, 4, 1, len(testing), 'additive')
        yhmape = mape(testing, predictions)
        gwmape = mape(testing, gw_fcsting)
        yhsum = yhsum + yhmape
        yhssum = yhssum + yhmape * yhmape
        gwsum = gwsum + gwmape
        gwssum = gwssum + gwmape * gwmape
        print("YH_MAPE[{0:.3f}]".format(yhmape), predictions)
        print("GW_MAPE[{0:.3f}]".format(gwmape), gw_fcsting)
    except Exception as e:
        print(e)
        pass
print(yhsum, gwsum, yhssum, gwssum)
