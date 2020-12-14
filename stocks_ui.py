# Joel Paul, Term 2 2019
# Digital Technologies Stage 2

import ui
import datetime
from stocks_queue import StocksQueue
from stocks_dict import StocksDict


# Initial states of the switches
is_daily = True
is_order = True

# Initial state of textbox
estimate_days = 0

orders_str = ''
daily_str = ''

def switch_daily(sender):
	""" Determine the state of the 'Save Daily Stocks' switch.
	
	Function called when the switch is interacted with.
	"""
	global is_daily
	is_daily = sender.value

def switch_order(sender):
	""" Determine the state of the 'Save Orders' switch.
	
	Function called when the switch is interacted with.
	"""
	global is_order
	global estimate_days
	
	is_order = sender.value
	estimate_field = sender.superview['txt_estimate']
	
	if is_order:
		estimate_field.enabled = True
	else:
		estimate_field.enabled = False
		estimate_field.text = '0'
		estimate_days = 0

def estimate_value(sender):
	""" Changes days of estimated stocks simulated.
	
	Function called when text is entered into the textfield.
	"""
	global estimate_days
	output = sender.superview['lbl_output']
	
	try:
		estimate_days = int(sender.text)
		output.text = ''
		output.text_color = '#000000'
	except ValueError:
		if not estimate_days == '':
			output.text = 'Please pass an integer!'
			output.text_color = '#ff0000'
		estimate_days = 0

def calculate_stocks(sender):
	""" Calculates the stocks and produces a file with contents depending on user selection.
	
	Function called when 'Calculate Stocks' button is triggered
	"""
	
	global is_daily
	global is_order
	global estimate_days
	global orders_str
	global daily_str
	
	output = sender.superview['lbl_output']
	scroll = sender.superview['scrollview']['textview']
	
	if not is_daily and not is_order:
		output.text = 'Please select at least one option!'
		output.text_color = '#ff8500'
		return
	
	stocks = StocksQueue('+->$')  # debug options are '+', '-', '$', '>'
	stocks_dict = StocksDict()
	
	# Add initial stock
	initial_stock = stocks_dict.get_initial_stock()
	initial_date = datetime.date(2019, 5, 19)
	
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
	stocks.estimate_sales(estimate_days)
	
	debug = stocks.get_debug()
	scroll.text = debug
	
	output.text = 'Simulation finished!'
	output.text_color = '#000000'
	
	# Get all the daily stocks and orders
	if is_order:
		orders_str = 'Orders:\n=======\n'
		orders = stocks.get_orders()
		for date in orders:
			item_str = ''
			for name in orders[date]:
				amount = str(orders[date][name])
				item_str += '\t\t{0}(s): {1}\n'.format(name, amount)
			orders_str += '\t{0}:\n{1}\n'.format(date.strftime('%d %b %Y'), item_str)
	
	if is_daily:
		daily_str = 'Daily Stocks:\n=============\n'
		daily_stocks = stocks.get_daily_stocks()
		for date in daily_stocks:
			item_str = ''
			for name in daily_stocks[date]:
				amount = str(daily_stocks[date][name])
				item_str += '\t\t{0}(s): {1}\n'.format(name, amount)
			daily_str += '\t{0}:\n{1}\n'.format(date.strftime('%d %b %Y'), item_str)
	
def save_stocks(sender):
	global orders_str
	global daily_str
	
	output = sender.superview['lbl_output']
	# Save to file
	file_name = datetime.datetime.now().strftime('orders-%H:%M:%S.txt')
	
	with open(file_name, 'w') as file:
		if is_order:
			file.write(orders_str)
		if is_daily:
			file.write(daily_str)
	
	output.text = 'Saved as {}'.format(file_name)
	output.text_color = '#00b800'

ui.load_view('stocks_ui').present('sheet')
