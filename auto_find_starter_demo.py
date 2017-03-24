from chan_lun_util import *
from k_line_dto import *
import matplotlib as mat
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import time

stock_code = '600527.XSHG'
start_date = '2016-09-01'
end_date = '2017-03-17'
initial_trend = "down"

quotes = get_price(stock_code, start_date, end_date, frequency='daily',skip_paused=False,fq='pre')
quotes[quotes['volume']==0]=np.nan
quotes= quotes.dropna()
Close=quotes['close']
Open=quotes['open']
High=quotes['high']
Low=quotes['low']
T0 = quotes.index.values

length=len(Close)

fig = plt.figure(figsize=(16, 8))
ax1 = plt.subplot2grid((10,4),(0,0),rowspan=10,colspan=4)
#fig = plt.figure()
#ax1 = plt.axes([0,0,3,2])

X=np.array(range(0, length))
pad_nan=X+nan

    #计算上 下影线
max_clop=Close.copy()
max_clop[Close<Open]=Open[Close<Open]
min_clop=Close.copy()
min_clop[Close>Open]=Open[Close>Open]

    #上影线
line_up=np.array([High,max_clop,pad_nan])
line_up=np.ravel(line_up,'F')
    #下影线
line_down=np.array([Low,min_clop,pad_nan])
line_down=np.ravel(line_down,'F')

    #计算上下影线对应的X坐标
pad_nan=nan+X
pad_X=np.array([X,X,X])
pad_X=np.ravel(pad_X,'F')


    #画出实体部分,先画收盘价在上的部分
up_cl=Close.copy()
up_cl[Close<=Open]=nan
up_op=Open.copy()
up_op[Close<=Open]=nan

down_cl=Close.copy()
down_cl[Open<=Close]=nan
down_op=Open.copy()
down_op[Open<=Close]=nan


even=Close.copy()
even[Close!=Open]=nan

#画出收红的实体部分
pad_box_up=np.array([up_op,up_op,up_cl,up_cl,pad_nan])
pad_box_up=np.ravel(pad_box_up,'F')
pad_box_down=np.array([down_cl,down_cl,down_op,down_op,pad_nan])
pad_box_down=np.ravel(pad_box_down,'F')
pad_box_even=np.array([even,even,even,even,pad_nan])
pad_box_even=np.ravel(pad_box_even,'F')

#X的nan可以不用与y一一对应
X_left=X-0.25
X_right=X+0.25
box_X=np.array([X_left,X_right,X_right,X_left,pad_nan])
box_X=np.ravel(box_X,'F')

#Close_handle=plt.plot(pad_X,line_up,color='k') 

vertices_up=array([box_X,pad_box_up]).T
vertices_down=array([box_X,pad_box_down]).T
vertices_even=array([box_X,pad_box_even]).T

handle_box_up=mat.patches.Polygon(vertices_up,color='r',zorder=1)
handle_box_down=mat.patches.Polygon(vertices_down,color='g',zorder=1)
handle_box_even=mat.patches.Polygon(vertices_even,color='k',zorder=1)

ax1.add_patch(handle_box_up)
ax1.add_patch(handle_box_down)
ax1.add_patch(handle_box_even)

handle_line_up=mat.lines.Line2D(pad_X,line_up,color='k',linestyle='solid',zorder=0) 
handle_line_down=mat.lines.Line2D(pad_X,line_down,color='k',linestyle='solid',zorder=0) 

ax1.add_line(handle_line_up)
ax1.add_line(handle_line_down)

v=[0,length,Open.min()-0.5,Open.max()+0.5]
plt.axis(v)

T1 = T0[-len(T0):].astype(dt.date)/1000000000
Ti=[]
for i in range(len(T0)/5):
    a=i*5
    d = dt.date.fromtimestamp(T1[a])
    #print d
    T2=d.strftime('$%Y-%m-%d$')
    Ti.append(T2)
    #print tab
d1= dt.date.fromtimestamp(T1[len(T0)-1])
d2=d1.strftime('$%Y-%m-%d$')
Ti.append(d2)

ax1.set_xticks(np.linspace(-2,len(Close)+2,len(Ti))) 

ll=Low.min()*0.97
hh=High.max()*1.03
ax1.set_ylim(ll,hh) 

ax1.set_xticklabels(Ti)

plt.grid(True)
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

# 处理以上分笔结果，组织成实际上图的点
k_line_list = []
date_list = quotes.index.tolist()
data_per_day = quotes.values.tolist()
x_date_list = quotes.index.values.tolist()

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

#选择最高或者最低点，和走势此后的方向（向上up或者向下down）
min_low = min(Low)
max_high = max(High)
initial_index = 0
for i in range(len(k_line_list)):
    k_line_dto = k_line_list[i]
    if min_low == k_line_dto.low:
        initial_trend = 'up'
        initial_index = i
        print(k_line_dto.begin_time.strftime('%Y-%m-%d %H:%M:%S')) 
        break
    if max_high == k_line_dto.high:
        initial_trend = 'down'
        initial_index = i
        print(k_line_dto.begin_time.strftime('%Y-%m-%d %H:%M:%S')) 
        break
        
# 确定需要划分的K线范围，进行截取
input_k_line_list = []        
if initial_index == 0:
    input_k_line_list = k_line_list
else:
    input_k_line_list = k_line_list[initial_index-1:]

#  1.K线合并,并且确定顶底分型
merge_line_list = find_peak_and_bottom(input_k_line_list, initial_trend)

# 将第一个合并K线单位置为顶/底
m_line_dto = merge_line_list[0]
if initial_trend == "up":
    m_line_dto.is_bottom = "Y"
elif initial_trend == "down":
    m_line_dto.is_peak = "Y"

#  2.分笔
fenbi_result,final_result_array,fenbi_seq_list = fen_bi(merge_line_list)

#  3.得到分笔结果，计算坐标显示
x_fenbi_seq = []
y_fenbi_seq = []
for i in range(len(final_result_array)):
    if final_result_array[i]:
        m_line_dto = merge_line_list[fenbi_seq_list[i]]
        if m_line_dto.is_peak == 'Y':
            peak_time = None
            for k_line_dto in m_line_dto.member_list[::-1]:
                if k_line_dto.high == m_line_dto.high:
                    # get_price返回的日期，默认时间是08:00:00
                    peak_time = k_line_dto.begin_time.strftime('%Y-%m-%d') +' 08:00:00'
                    break
            x_fenbi_seq.append(x_date_list.index(long(time.mktime(datetime.strptime(peak_time, "%Y-%m-%d %H:%M:%S").timetuple())*1000000000)))
            y_fenbi_seq.append(m_line_dto.high)
        if m_line_dto.is_bottom == 'Y':
            bottom_time = None
            for k_line_dto in m_line_dto.member_list[::-1]:
                if k_line_dto.low == m_line_dto.low:
                    # get_price返回的日期，默认时间是08:00:00
                    bottom_time = k_line_dto.begin_time.strftime('%Y-%m-%d') +' 08:00:00'
                    break
            x_fenbi_seq.append(x_date_list.index(long(time.mktime(datetime.strptime(bottom_time, "%Y-%m-%d %H:%M:%S").timetuple())*1000000000)))
            y_fenbi_seq.append(m_line_dto.low)

#  在原图基础上添加分笔蓝线
plt.plot(x_fenbi_seq,y_fenbi_seq)

plt.show()
