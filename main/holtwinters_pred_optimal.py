from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters
from main import draw1, items, result, sales, gw_fcst
import math

step = 0.1
count = math.floor(1 / step)
print(count)

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

        best_al = 0
        best_be = 0
        best_ga = 0
        best_yhmape = 0
        best_pred = []
        for alpha_i in range(count):
            al = alpha_i * step
            for beta_i in range(count):
                be = beta_i * step
                # for gamma_i in range(count):
                ga = 0.9
                predictions = holtWinters(training, 52, 3, 52, 'additive', alpha=al, beta=be, gamma=ga)["predicted"]
                predictions = [x if x > 0 else 0 for x in predictions]
                yhmape = mape(testing, predictions)
                if best_yhmape == 0 or best_yhmape > yhmape:
                    best_yhmape = yhmape
                    best_al = al
                    best_be = be
                    best_ga = ga
                    best_pred = predictions
        print("Item [{3:d}] {4:f}: alpha:{0:f}, beta:{1:f}, gamma {2:f}".format(best_al, best_be, best_ga, item,
                                                                                best_yhmape))
        yhsum = yhsum + best_yhmape
        yhssum = yhssum + best_yhmape * best_yhmape
        gwmape = mape(testing, gw_fcsting)
        gwsum = gwsum + gwmape
        gwssum = gwssum + gwmape * gwmape
        print("YH_MAPE[{0:.3f}]".format(best_yhmape), best_pred[:len(testing)])
        print("GW_MAPE[{0:.3f}]".format(gwmape), gw_fcsting)
        print("================================================")
        draw1(temp, testing, best_pred,
              "{0:d}[{1:.2f}_{2:.2f}_{3:.2f}]_optimal.png".format(item, best_al, best_be, best_ga))

        # break
        # except Exception as e:
        #     print(e)
        #     break
    print(non_zero)
    print(yhsum, gwsum, yhssum, gwssum)
