# chan_lun_util_py
A personal implement of Zen theory in Python, which is popular among Chinese stock investors. Just for fun. 

For more detail: https://www.joinquant.com/post/4739

chan_lun_util.py 在joinquant上使用分笔功能的demo:

```python

    from chan_lun_util import *
    import matplotlib as mat
    import numpy as np
    import datetime as dt
    import matplotlib.pyplot as plt
    import time

    start_date='2016-02-05'
    end_date='2017-02-07'
    stock_code = '601318.XSHG'
    df = get_price(stock_code, start_date, end_date, frequency='daily', fields=['open','close','high', 'low'],skip_paused=False,fq='pre')

    date_list = df.index.tolist()
    data_per_day = df.values.tolist()

    k_line_list = []
    ''' 将dataframe数据组装进入KLineDTO的列表中 '''
    for index in range(len(date_list)):
        date_time = date_list[index]
        open_price = data_per_day[index][0]
        close_price = data_per_day[index][1]
        high_price = data_per_day[index][2]
        low_price = data_per_day[index][3]
        k_line_dto = KLineDTO(date_time,
                                  date_time,
                                  date_time,
                                  open_price, high_price, low_price, close_price)
        k_line_list.append(k_line_dto)

    len(k_line_list)

    '''1.K线合并,确定顶分型和底分型,得出合并K线列表merge_line_list '''
    merge_line_list = find_peak_and_bottom(k_line_list, "down")

    '''2.分笔'''
    fenbi_result,final_result_array,fenbi_seq_list = fen_bi(merge_line_list)


```

------------------------------------------------
其中：<br/>
1. fenbi_result为boolean，True的话就是分笔成功了；False就是分笔失败后面的final_result_array和fenbi_seq_list都不用看了。<br/>
2. final_result_array，fenbi_seq_list：如果final_result_array[i]为True，则对于merge_line_list来说，merge_line_list[fenbi_seq_list[i]]就为最终顶或者底对应的合并K线dto <br/>
