# Joel Paul, Term 2 2019
# Digital Technologies Stage 2

from datetime import date
from stocks_queue import StocksQueue
from stocks_dict import StocksDict


# debug options are '+', '-', '$', '>'
# e.g. StocksQueue(debug='$>')
# + for added items
# - for expired items
# $ for sold items
# > for ordered items
stocks = StocksQueue(debug='')
stocks_dict = StocksDict()

# Add initial stock
initial_stock = stocks_dict.get_initial_stock()
initial_date = date(2019, 5, 19)

for name in initial_stock:
	amount = initial_stock[name]
	stocks.add(name, amount, initial_date)

# Implement sales
sales = stocks_dict.get_sales()

for date in sales:
	items = sales[date]
	for item in items:
		for name in item:
			amount = item[name]
			stocks.sell(name, amount, date)

# Estimate sales for x days
stocks.estimate_sales(10)

# Get the all the daily stocks and orders
daily_stocks = stocks.get_daily_stocks()
orders = stocks.get_orders()

# Print daily stocks and orders
print('\nRecord of Daily Stocks:\n=======================')
for date in daily_stocks:
	print('{0}:\n{1}\n'.format(date, daily_stocks[date]))

print('Record of Orders:\n=================')
for date in orders:
	print('{0}:\n{1}\n'.format(date, orders[date]))
