from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from main.holtwinters import holtWinters
from main import draw1, items, result, sales, gw_fcst, end_week_obj, df, float_list_2_string
import math
from datetime import timedelta as td
import numpy as np
from numpy.random import random as rand

step = 0.1
count = math.floor(1 / step)
print(count)

before_head = 0
delay = 12
fcst_len = 12
ga = 0.9

sprt = ","

def simplebounds(batX, Lower_bound, Upper_bound):
    Index = batX > Lower_bound
    batX = Index * batX + ~Index * Lower_bound
    Index = batX < Upper_bound
    batX = Index * batX + ~Index * Upper_bound
    return batX

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
            if zero_sum > len(temp) // 3:
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

            # Automatically optimize parameter

            #initialize all superparameters
            N_pop = 80 #
            N_gen = 1000
            A = 0.5
            plusRate = 0.5
            Qmin = 0
            Qmax = 2
            d = 3
            lower = 0
            upper = 1
            N_iter = 0  # Total number of function evaluations
            Lower_bound = lower * np.ones((1, d))
            Upper_bound = upper * np.ones((1, d))

            Q = np.zeros((N_pop, 1))  # Frequency
            v = np.zeros((N_pop, d))  # Velocities
            S = np.zeros((N_pop, d))  # bat position S

            # Initialize the population/soutions
            Sol = np.zeros((N_pop, d))
            Fitness = np.zeros((N_pop, 1))

            for i in range(N_pop):
                Sol[i] = np.random.uniform(Lower_bound, Upper_bound, (1, d))
                predictions = \
                holtWinters(training, 52, 3, fcst_len, 'additive', alpha=S[i][0], beta=S[i][1], gamma=S[i][2])[
                    "predicted"]
                Fitness[i] = mape(testing, predictions)

            fmax = min(Fitness)
            Index = list(Fitness).index(fmax)
            best = Sol[Index]
            # Start the iterations
            for t in range(N_gen):
                # Loop over all solutions
                for i in range(N_pop):
                    Q[i] = np.random.uniform(Qmin, Qmax)
                    v[i] = v[i] + (Sol[i] - best) * Q[i]
                    S[i] = Sol[i] + v[i]
                    if rand() > plusRate:
                        S[i] = best + 0.001 * np.random.randn(1, d)
                    # Apply simple bounds/limits
                    S[i] = simplebounds(S[i], Lower_bound, Upper_bound)
                    predictions = \
                    holtWinters(training, 52, 3, fcst_len, 'additive', alpha=S[i][0], beta=S[i][1], gamma=S[i][2])[
                        "predicted"]
                    Fnew = mape(testing, predictions)
                    # Update if the solution improves, or not too loud
                    if (Fnew <= Fitness[i]) and (rand() < A):
                        Sol[i] = S[i]
                        Fitness[i] = Fnew
                    # update the current best solution
                    if Fnew <= fmax:
                        best = S[i]
                        fmax = Fnew
                        best_yhmape = Fnew
                        best_al = S[i][0]
                        best_be = S[i][1]
                        best_ga = S[i][2]
                        best_pred = predictions
                N_iter = N_iter + N_pop

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
