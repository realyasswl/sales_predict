from main.history_sale import punish_negative as mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters
from main import draw1, items, result, sales, gw_fcst, end_week_obj, df, float_list_2_string, ty_sales_money, draw2
import math
from datetime import timedelta as td

count = 10
step = 1 / 10

before_head = 0
delay = 12
fcst_len = 53
ga = 0.9
t_len = 0
sprt = ","
max_layer = 2

param_filepath = "d:\\work\\potential_ml\\greenworks\\py\\param_file"


def read_params():
    params_dict = {}
    try:
        with open(param_filepath, "r") as param_file:
            lines = param_file.readlines()
            for line in lines:
                if len(line) == 0:
                    continue
                strs = line.split(",")
                params_dict[int(strs[0])] = (float(strs[1]), float(strs[2]), float(strs[3]))
    except:
        print("read_params error, return empty dict")
    return params_dict


def store_params(params_dict):
    with open(param_filepath, "w") as param_file:
        for k, v in params_dict.items():
            a, b, g = v
            param_file.write("{0:d},{1:f},{2:f},{3:f}\n".format(k, a, b, g))


def recursive_optimal_param(training, testing, params, step=0.1, layer=0):
    if step == 0.1:
        a_lo = 0
        a_hi = 1
        b_lo = 0
        b_hi = 1
        g_lo = 0
        g_hi = 1
    else:
        base_a, base_b, base_g = params
        a_lo = max(0, base_a - step * count)
        b_lo = max(0, base_b - step * count)
        g_lo = max(0, base_g - step * count)
        a_hi = min(1, base_a + step * count)
        b_hi = min(1, base_b + step * count)
        g_hi = min(1, base_g + step * count)

    len_a = math.floor((a_hi - a_lo) / step)
    len_b = math.floor((b_hi - b_lo) / step)
    len_g = math.floor((g_hi - g_lo) / step)
    best_al = 0
    best_be = 0
    best_ga = 0
    best_yhmape = 0
    best_pred = []
    for alpha_i in range(len_a):
        al = a_lo + alpha_i * step
        for beta_i in range(len_b):
            be = b_lo + beta_i * step

            # for gamma_i in range(len_g):
            #     ga = g_lo + gamma_i * step
            predictions = holtWinters(training, 52, 3, fcst_len, 'additive', alpha=al, beta=be, gamma=ga)[
                "predicted"]

            yhmape = mape(testing, predictions)
            if best_yhmape == 0 or best_yhmape > yhmape:
                best_yhmape = yhmape
                best_al = al
                best_be = be
                best_ga = ga
                best_pred = predictions

    print(
        "Item [{3:d}] {4:f}: alpha:{0:f}, beta:{1:f}, gamma {2:f}".format(best_al, best_be, best_ga, item, best_yhmape))
    if layer == max_layer:
        return best_al, best_be, best_ga, best_pred, best_yhmape
    else:
        return recursive_optimal_param(training, testing, (best_al, best_be, best_ga), step=step / 10, layer=layer + 1)


if __name__ == '__main__':
    non_zero = 0
    non_zero_items = []
    param_dict = read_params()
    calc_param = len(param_dict) == 0
    with open("report.csv", "w") as write_file:
        write_file.write("item,title,MAPE,sum,{0:s}\n".
                         format(sprt.join([(end_week_obj + td(weeks=x + 1)).strftime(df) for x in range(fcst_len)])))
        print(len(items))
        for ind, item in enumerate(items):
            # if item != 535389:
            #     continue

            # prepare data begins
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
            non_zero_items.append(item)
            training = []
            to_be_add = []
            if delay > 0:
                training = temp[:0 - delay]
                to_be_add = temp[0 - delay:]
            else:
                training = temp[:]
            try:
                testing = [float(x) for x in sales[ind]][:t_len] if t_len > 0 else [float(x) for x in sales[ind]]
            except ValueError:
                continue
            gw_fcsting = gw_fcst[ind][:]
            predictions = []
            print(testing)
            sales_dollar = ty_sales_money[ind]
            # prepare data ends

            # output best predict, parameter, model and result
            if calc_param:
                best_al, best_be, best_ga, best_pred, best_yhmape = recursive_optimal_param(training, testing, ())
            else:
                best_al, best_be, best_ga = param_dict[item]
                best_pred = holtWinters(training, 52, 3, fcst_len, 'additive', best_al, best_be, best_ga)["predicted"]
                best_yhmape = mape(testing, best_pred)
            print("Item [{3:d}] {4:f}: alpha:{0:f}, beta:{1:f}, gamma {2:f}".format(best_al, best_be, best_ga, item,
                                                                                    best_yhmape))

            # compute mape
            yhsum = yhsum + best_yhmape
            yhssum = yhssum + best_yhmape * best_yhmape
            gwmape = mape(testing, gw_fcsting)
            gwsum = gwsum + gwmape
            gwssum = gwssum + gwmape * gwmape

            # output report
            write_file.write("{2:d},Actual_Sale,{0:.3f},{1:s}\n".format(0, float_list_2_string(testing), item))
            write_file.write(
                "{2:d},YH_forecast,{0:.3f},{1:s}\n".format(best_yhmape, float_list_2_string(best_pred), item))
            write_file.write("{2:d},GW_forecast,{0:.3f},{1:s}\n".format(gwmape, float_list_2_string(gw_fcsting), item))
            total_sale_dollar = 0
            for i in range(len(testing)):
                total_sale_dollar = total_sale_dollar + testing[i] * sales_dollar[i]
            write_file.write("{2:d},TY_ASP$,{0:.3f},{1:s}\n".format(0, float_list_2_string(sales_dollar), item))

            # draw visualization
            draw1(temp, training, testing, best_pred, gw_fcsting, "{0:d}_optimal.png".format(item))

            # monthly error
            draw2("{0:d}_monthly_err.png".format(item), testing, {"yh": best_pred, "gw": gw_fcsting}, 4, week=fcst_len)

            if calc_param:
                param_dict[item] = (best_al, best_be, best_ga)
        print(non_zero)
        print(non_zero_items)
        print(yhsum, gwsum, yhssum, gwssum)

    if calc_param:
        store_params(param_dict)
