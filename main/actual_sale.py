from openpyxl import load_workbook

import pickle


def get_column(column_name):
    return column_names.index(column_name)


def get_row(number_name):
    return number_names.index(number_name)


class Item:
    def __init__(self, category, platform, erp, litem, desc):
        self.category = category
        self.platform = platform
        self.erp = erp
        self.litem = litem
        self.desc = desc
        self.weeklyInfos = []


class WeeklyInfo:
    def __init__(self, item, time):
        self.item = item
        self.time = time
        self.numbers = {}


def get_info(start_index):
    subrows = rows[start_index:start_index + item_rows]


if __name__ == '__main__':

    pipeline = load_workbook("D:\\deeplearning\\greenworks\\pipeline_0413.xlsx")
    fcst = pipeline["Forecasting"]
    rows = list(fcst.rows)
    column_names = list(c.value for c in rows[1])

    # rows per item info
    item_rows = 17

    # index within {item_rows} to read item info
    item_index = 0

    # start from this row to read item info; 3-1
    item_start = 2

    number_names = list(c.value.strip() for c in list(fcst.columns)[9][item_start:item_start + item_rows])

    lyas = "LY Acutal Sales"
    tyas = "TY Actual Sales"
    gwfcst = "GW Final POS Forecast"
    ASP = "ASP"

    items = []
    sales = []
    gw_fcst = []
    ty_sales_money = []

    curr = item_start
    # BK to BT, 2018/2/9 to 2018/4/13
    start_cell = 62
    end_cell = 72
    while curr < len(rows):
        item = rows[curr][get_column("Lowe's Item")].value
        items.append(item)

        sales.append([cell.value for cell in rows[curr + get_row(tyas)][start_cell:end_cell]])
        gw_fcst.append([cell.value for cell in rows[curr + get_row(gwfcst)][start_cell:end_cell]])
        ty_sales_money.append([cell.value for cell in rows[curr + get_row(ASP)][start_cell:end_cell]])
        curr = curr + item_rows

    print("load data 0")
    # for i in range(len(items)):
    #     print(items[i], sales[i])

    # with open("items", "w") as fitems:
    #     for item in items:
    #         fitems.write(str(item))
    #         fitems.write("\r\n")
    #
    # with open("gw_fcst") as fgwfcst:
    #     for item in gw_fcst:
    #         fgwfcst.write(str(item))
    #         fgwfcst.write("\r\n")
    #
    # with open("sales") as fsales:
    #     for item in sales:
    #         fsales.write(str(item))
    #         fsales.write("\r\n")

    with open('items', 'wb') as f:
        pickle.dump(items, f)

    with open('sales', 'wb') as f:
        pickle.dump(sales, f)

    with open('gw_fcst', 'wb') as f:
        pickle.dump(gw_fcst, f)
    with open('ty_sales_money', 'wb') as f:
        pickle.dump(ty_sales_money, f)
