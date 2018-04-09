start_week = "2015/2/6"
end_week = "2018/2/2"
df = "%Y/%m/%d"

import datetime

end_week_obj = datetime.datetime.strptime(end_week, df)
