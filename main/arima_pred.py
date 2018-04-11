import sys

sys.path.insert(0, "d:\\work\\potential_ml\\greenworks\\py")
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import arma_order_select_ic
from main.history_sale import mape, yhssum, yhsum, gwssum, gwsum
from main import items, result, sales, gw_fcst

if __name__ == "__main__":

    for ind, item in enumerate(items):
        try:
            print("================================================")
            print("item[{0:d}]========================".format(item))
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
