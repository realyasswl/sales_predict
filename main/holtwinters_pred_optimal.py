from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters
from main import draw1, items, result, sales, gw_fcst, end_week_obj, df, float_list_2_string
import math
from datetime import timedelta as td

step = 0.1
count = math.floor(1 / step)
print(count)

before_head = 0
delay = 12
fcst_len = 12
ga = 0.9

sprt = ","
if __name__ == '__main__':
    non_zero = 0
    with open("report.csv", "w") as write_file:
        write_file.write("item,title,MAPE,{0:s}".
                         format(sprt.join([(end_week_obj + td(weeks=x + 1)).strftime(df) for x in range(fcst_len)])))
        write_file.write("\n")
        for ind, item in enumerate(items):
            # if item != 506892:
            #     continue
            # try:
            # print("{1:d}]item[{0:d}]=================================".format(item, ind))
            temp = [float(x) for x in result[item]]
            if before_head > 0:
                temp = temp[before_head:]
            zero = False
            zero_sum = 0
            for i in temp:
                if i == 0:
                    zero_sum = zero_sum + 1
            if zero_sum > len(temp) / 3:
                print("too much zero!!!!! Skip this item.")
                print(temp)
                continue

            non_zero = non_zero + 1
            training = []
            to_be_add = []
            if delay > 0:
                training = temp[:0 - delay]
                to_be_add = temp[0 - delay:]
            else:
                training = temp[:]
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
                    predictions = holtWinters(training, 52, 3, fcst_len, 'additive', alpha=al, beta=be, gamma=ga)[
                        "predicted"]
                    # predictions = [x if x > 0 else 0 for x in predictions]
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
            write_file.write("{2:d},Actual_Sale,{0:.3f},{1:s}".format(0, float_list_2_string(testing), item))
            write_file.write("\n")
            write_file.write(
                "{2:d},YH_forecast,{0:.3f},{1:s}".format(best_yhmape, float_list_2_string(best_pred), item))
            write_file.write("\n")
            write_file.write("{2:d},GW_forecast,{0:.3f},{1:s}".format(gwmape, float_list_2_string(gw_fcsting), item))
            write_file.write("\n")

            draw1(temp, training, testing, best_pred, gw_fcsting, "{0:d}_optimal.png".format(item))

            # break
            # except Exception as e:
            #     print(e)
            #     break
        print(non_zero)
        print(yhsum, gwsum, yhssum, gwssum)
