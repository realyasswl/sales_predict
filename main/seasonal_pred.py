import sys

sys.path.insert(0, "d:\\work\\potential_ml\\greenworks\\py")
from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from statsmodels.tsa.statespace.sarimax import SARIMAX
from main import draw, items, result, sales, gw_fcst

if __name__ == "__main__":

    for ind, item in enumerate(items):
        # if item != 101639:
        #     continue
        try:
            print("item[{0:d}]=====================================".format(item))

            temp = [float(x) for x in result[item]]

            # add fake data to deepen the dataset, otherwise "maxlag should be < nods" will appear
            # for record in training[:]:
            #     training.append(record)

            s15 = temp[:52]
            s16 = temp[52:104]
            s14 = [(s15[x] + s16[x]) / 2 for x in range(52)]
            s13 = [x * 2 / 3 for x in s14]
            s12 = [x * 2 / 3 for x in s13]
            s11 = [x * 2 / 3 for x in s12]
            training = s11 + s12 + s13 + s14
            for i in range(len(temp) - 12):
                training.append(temp[i])

            to_be_add = temp[-12:]
            try:
                testing = [float(x) for x in sales[ind]]
            except ValueError:
                continue
            gw_fcsting = gw_fcst[ind][:]
            predictions = []
            print(len(training))
            print(testing)

            # draw(training, item)

            model = SARIMAX(training, order=(1, 1, 1), seasonal_order=(1, 1, 1, 52), enforce_invertibility=False)
            model_fit = model.fit(disp=0)
            # print(model_fit.summary())
            predictions = model_fit.predict(start=157, end=163)

            yhmape = mape(testing, predictions)
            gwmape = mape(testing, gw_fcsting)
            yhsum = yhsum + yhmape
            yhssum = yhssum + yhmape * yhmape
            gwsum = gwsum + gwmape
            gwssum = gwssum + gwmape * gwmape
            print("YH_MAPE[{0:.3f}]".format(yhmape), predictions)
            print("GW_MAPE[{0:.3f}]".format(gwmape), gw_fcsting)
            # break
        except Exception as e:
            print(e)
            # break
    print(yhsum, gwsum, yhssum, gwssum)
