from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters
from main import draw1, items, result, sales, gw_fcst
import math

al = 0.4
be = 0.3
ga = 0.9

if __name__ == '__main__':
    non_zero = 0
    for ind, item in enumerate(items):
        # if item != 535386:
        #     continue
        # try:
        print("{1:d}]item[{0:d}]========================".format(item, ind))
        temp = [float(x) for x in result[item]]
        zero = False
        zero_sum = 0
        for i in temp:
            if i == 0:
                zero_sum = zero_sum + 1
        if zero_sum > len(temp) / 3:
            print("too much zero!!!!!")
            print(temp)
            continue

        non_zero = non_zero + 1
        training = temp[:-12]
        to_be_add = temp[-12:]
        try:
            testing = [float(x) for x in sales[ind]]
        except ValueError:
            continue
        gw_fcsting = gw_fcst[ind][:]
        predictions = []
        print(testing)

        predictions = holtWinters(training, 52, 3, 52, 'additive', alpha=al, beta=be, gamma=ga)["predicted"]
        predictions = [x if x > 0 else 0 for x in predictions]
        yhmape = mape(testing, predictions)
        yhsum = yhsum + yhmape
        yhssum = yhssum + yhmape * yhmape
        gwmape = mape(testing, gw_fcsting)
        gwsum = gwsum + gwmape
        gwssum = gwssum + gwmape * gwmape
        print("YH_MAPE[{0:.3f}]".format(yhmape), predictions[:len(testing)])
        print("GW_MAPE[{0:.3f}]".format(gwmape), gw_fcsting)
        print("================================================")
        draw1(temp, testing, predictions, "{0:d}[{1:.2f}_{2:.2f}_{3:.2f}].png".format(item, al, be, ga))

        # break
        # except Exception as e:
        #     print(e)
        #     break
    print(non_zero)
    print(yhsum, gwsum, yhssum, gwssum)
