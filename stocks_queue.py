# Joel Paul, Term 2 2019
# Digital Technologies Stage 2
# (Apologies for the messy code, bodged together some stuff near the end)

from collections import OrderedDict
from datetime import date, timedelta
from stocks_dict import StocksDict


ROUND = 1


class StocksQueue():
	""" Stores stock items in queue, using FIFO (First In First Out) """
	def __init__(self, debug=''):
		
		# Debugging values
		self.__db_add = False
		self.__db_order = False
		self.__db_expiry = False
		self.__db_sell = False
		
		# Check configuration
		if '+' in debug:
			self.__db_add = True
		if '>' in debug:
			self.__db_order = True
		if '-' in debug:
			self.__db_expiry = True
		if '$' in debug:
			self.__db_sell = True
		
		if debug != '':
			self.__debug = True
		else:
			self.__debug = False
		
		self.__debug_str = ''
		
		# Keep track of how many times we rerun the simulation
		self.__restart_counter = 1
		
		# An ordered list containing items with their
		# name, amount, added_date and expiry_date
		# e.g. [['carrot', 30, datetime.date(2019, 5, 19), datetime.date(2019, 5, 29)], ...]
		# Used to keep track of stocks and expiration dates
		self.__current_stocks = []
		
		# A dictionary with dates as the key referring
		# to a dictionary with items and total amount
		# e.g. {datetime.date(2019, 5, 19): {'carrot': 30}, ...}
		# Used to keep track of total stocks for specific dates
		self.__daily_stocks = OrderedDict()
		
		# A dictionary with dates as the key referring
		# to a dictionary with items and attempted selling for each date
		# e.g. {datetime.date(2019, 5, 19): {'carrot': 30, 'potato': 20}, ...}
		# Used to keep track of demand per day
		self.__demand = OrderedDict()
		
		# Dictionary to keep track of restock orders
		# e.g. {datetime.date(2019, 5, 19): {'carrot': 30, 'potato': 20}, ...}
		self.__orders = OrderedDict()
		self.__temp_orders = self.__orders.copy()
		
		# Dictionary to keep track of directly added items
		# e.g. {datetime.date(2019, 5, 19): {'carrot': 30, 'potato': 20}, ...}
		self.__added_items = OrderedDict()
		
		# A queue of items to add
		self.__add_queue = []
		
		# Get stock data from stocks_dict
		stocks_dict = StocksDict()
		self.__item_categories = stocks_dict.get_item_categories()
		self.__holding_times = stocks_dict.get_holding_times()
		self.__delivery_times = stocks_dict.get_delivery_times()
		
		if self.__debug:
			string = '\n\n\t\t======== STOCK SIMULATION #{} ========\n'.format(self.__restart_counter)
			#print(string)
			self.__debug_str += string
	
	def __deplete_items_from_daily_stocks(self, name, amount, current_date):
		""" Decrease the amount of items in self.__dated_stocks for a given date """
		
		try:
			# Decrease the amount
			self.__daily_stocks[current_date][name] -= amount
			
		except KeyError:
			# Since we have no values for the current date, use the previous day's values
			yesterday = current_date - timedelta(days=1)
			
			self.__daily_stocks[current_date] = self.__daily_stocks[yesterday].copy()
			
			# Decrease the amount
			self.__daily_stocks[current_date][name] -= amount
		
		finally:
			# Round values
			self.__daily_stocks[current_date][name] = round(self.__daily_stocks[current_date][name], ROUND)
	
	def __get_demand_total(self):
		""" Return the sum of demands.
		
		Calculate the total demand.
		"""
		demand_total = {}  # Dict to hold sales
		
		# Add up demand
		for date in self.__demand:
			item = self.__demand[date]
			
			for name in item:
				amount = item[name]
				
				try:
					# Try to append to the item if it exists
					demand_total[name] += amount
				except KeyError:
					# If the item does not exist, create it
					demand_total[name] = amount
		
		return demand_total
	
	def __get_demand_average(self):
		""" Return the average demand.
		
		Calculate the rate items are demanded.
		"""
		demand_average = {}
		days = len(self.__demand)  # The period in days
		demand_total = self.__get_demand_total()
		
		for item in demand_total:
			amount = demand_total[item]
			demand_average[item] = amount / days
		
		return demand_average
	
	def __check_expiry(self, date):
		""" Checks if items have expired for a given date """
		for item in self.__current_stocks:
			name = item[0]
			amount = item[1]
			expiry_date = item[3]
			
			if date >= expiry_date:
				if self.__db_expiry:
					string = '\n[-] {0} {1}(s) expired on {2}.'.format(amount, name, date)
					#print(string)
					self.__debug_str += string
				
				self.__deplete_items_from_daily_stocks(name, amount, date)
				self.__current_stocks.remove(item)
	
	def __determine_order(self, name, amount, date):
		""" Determine when to order to ensure the stock never reaches zero. """
		
		category = self.__item_categories[name]  # Get category
		holding_time = self.__holding_times[category]  # Get holding time
		delivery_time = self.__delivery_times[category]  # Get delivery time
		rate = self.__get_demand_average()[name] # Get the average sales
		
		order_amount = round(holding_time * rate, ROUND)
		order_days = delivery_time
		order_date = date - timedelta(days=order_days)
		
		if self.__db_order:
			string = '\n[!] Recommended to order {0} {1}(s) on {2}.'.format(order_amount, name, order_date)
			#print(string)
			self.__debug_str += string
		
		if not order_date in self.__orders:
			self.__orders[order_date] = {name: order_amount}
		elif not name in self.__orders[order_date]:
			self.__orders[order_date][name] = order_amount
		else:
			self.__orders[order_date][name] += order_amount
		
		if not order_date in self.__temp_orders:
			self.__temp_orders[order_date] = {name: order_amount}
		elif not name in self.__temp_orders[order_date]:
			self.__temp_orders[order_date][name] = order_amount
		else:
			self.__temp_orders[order_date][name] += order_amount
		
		self.__restart()
	
	def __check_orders(self, check_date):
		# Order new items
		del_dates = []
		
		for date in self.__temp_orders:
			if date == check_date:
				items = self.__temp_orders[date]
				for name in items:
					amount = items[name]
					self.order(name, amount, date)
				del_dates.append(date)
		
		for date in del_dates:
			del self.__temp_orders[date]
	
	def __check_added(self, check_date):
		for items in self.__add_queue:
			date = items[0]
			name = items[1]
			amount = items[2]
			
			if date == check_date:
				self.__add_queue.remove(items)
				self.add(name, amount, date, order=True)
	
	def __restart(self):
		""" Restart stock simulation from the start, implementing reccomended orders """
		self.__restart_counter += 1
		
		if self.__debug:
			string1 = '\nRestarting...'
			string2 = '\n\n\t\t======== STOCK SIMULATION #{} ========\n'.format(self.__restart_counter)
			#print(string1)
			#print(string2)
			self.__debug_str += string1
			self.__debug_str += string2
		
		# Reset some lists
		self.__current_stocks = []
		self.__daily_stocks.clear()
		
		added_items = self.__added_items.copy()
		self.__added_items.clear()
		
		demand = self.__demand.copy()
		self.__demand.clear()
		
		self.__temp_orders = self.__orders.copy()
		
		# Add initial items
		for date in added_items:
			items = added_items[date]
			for name in items:
				amount = items[name]
				self.add(name, amount, date)
		
		# Try buy stuff
		for date in demand:
			items = demand[date]
			for name in items:
				amount = items[name]
				self.sell(name, amount, date)
	
	def add(self, name, amount, added_date, order=False):
		"""
		Add stock items to object.
		
		Requires an item name, amount, and added_date.
		"""
		self.__check_orders(added_date)  # Check if items need to be ordered
		self.__check_added(added_date)  # Check if there are ordered items to add
		
		# Output for debugging
		if self.__db_add:
			string = '\n[+] Adding {0} {1}(s) on {2}.'.format(amount, name, added_date)
			#print(string)
			self.__debug_str += string
		
		if not order:
			if not added_date in self.__added_items:
				self.__added_items[added_date] = {name: amount}
			elif not name in self.__added_items[added_date]:
				self.__added_items[added_date][name] = amount
			else:
				self.__added_items[added_date][name] += amount
			
			# Round
			self.__added_items[added_date][name] = round(self.__added_items[added_date][name], ROUND)
		
		# Get the category of the item
		category = self.__item_categories[name]
		# Use the category to get holding time
		holding_time = int(self.__holding_times[category])
		# Use holding time to calculate expiry date
		expiry_date = added_date + timedelta(days=holding_time)
		
		self.__current_stocks.append([name, amount, added_date, expiry_date])
		
		## Add the values to self.__daily_stocks
		# Get yesterday's date
		yesterday = added_date - timedelta(days=1)
		
		# Get a valid copy of yesterday's stocks if needed
		if not added_date in self.__daily_stocks:
			if yesterday in self.__daily_stocks:
				self.__daily_stocks[added_date] = self.__daily_stocks[yesterday].copy()
		
		# Add the values to self.__daily_stocks
		try:
			self.__daily_stocks[added_date][name] += amount
		except KeyError:
			try:
				self.__daily_stocks[added_date][name] = amount
			except KeyError:
				self.__daily_stocks[added_date] = {name: amount}
		finally:
			# Round
			self.__daily_stocks[added_date][name] = round(self.__daily_stocks[added_date][name], ROUND)
	
	def order(self, name, amount, order_date):
		"""
		Orders items similarly to StocksQueue.add(), but accounts for delivery time
		"""
		
		# Output for debugging
		if self.__db_order:
			string = '\n[>] Ordering {0} {1}(s) on {2}.'.format(amount, name, order_date)
			#print(string)
			self.__debug_str += string
		
		# Get the category of the item
		category = self.__item_categories[name]
		# Use the category to get delivery time
		delivery_time = int(self.__delivery_times[category])
		# Use delivery time to calculate expiry date
		added_date = order_date + timedelta(days=delivery_time)
		
		self.__add_queue.append([added_date, name, amount])
		
		# self.add(name, amount, added_date, order=True)
	
	def sell(self, name, amount, current_date, price=0, retry=False):
		"""
		Remove stock items from object.
		
		Requires item name, amount, current date,
		optional price (default 0) and optional retry (default False)
		
		The variable price is unused at the moment.
		
		The retry bool indicates whether or not we are attempting to sell
		stock from a different stock 'pile'. This is provides and easy method
		to obtain the demand for items.
		"""
		self.__check_expiry(current_date)  # Check for and remove expired items
		self.__check_orders(current_date)  # Check if items need to be ordered
		self.__check_added(current_date)  # Check if there are ordered items to add
		
		# Output for debugging
		if self.__db_sell:
			string = '\n[?] Attempting to sell {0} {1}(s) on {2}...' .format(amount, name, str(current_date))
			#print(string)
			self.__debug_str += string
		
		match = False  # Used to check if stock has been found
		
		# Increment the demand values
		if not retry:
			try:
				self.__demand[current_date][name] += amount
			except KeyError:
				try:
					self.__demand[current_date][name] = amount
				except KeyError:
					self.__demand[current_date] = {name: amount}
			finally:
				self.__demand[current_date][name] = round(self.__demand[current_date][name], ROUND)
		
		# Look through stocks and find item
		# Don't get the item if it has already been found
		for item in self.__current_stocks:
			added_date = item[2]
			expiry_date = item[3]
			
			# Does it have the same name and has there not been a match?
			# Is it within the stock's added and expiry date?
			if item[0] == name \
					and match is False \
					and current_date >= added_date \
					and current_date < expiry_date:
				match = True  # Set to true to indicate a match has been found
				
				stock = item[1]
				stock -= amount  # Decrease the stock
				
				added_date = 0
				
				# If the remaining stock is less than 0, there isn't enough stock left
				## Get the remainder to try buy again for a different stock
				# Else if it is equal to zero, simply remove the item
				# Else reduce the stock
				if stock < 0:
					remainder = abs(stock)
					
					if self.__db_sell:
						string = ('\n[$] Successfully sold {0} {2}(s) from current batch!'
						+ ' Attempting to sell {1} {2}(s) from next batch...')
						string = string.format(amount-remainder, remainder, name)
						#print(string)
						self.__debug_str += string
					
					self.__current_stocks.remove(item)
					self.sell(name, remainder, current_date, price, True)
					
					self.__deplete_items_from_daily_stocks(name, amount-remainder, current_date)
					
				elif stock == 0:
					if self.__db_sell:
						string = '\n[$] Successfully sold {0} {1}(s)!'.format(amount, name)
						#print(string)
						self.__debug_str += string
						
					self.__current_stocks.remove(item)
					self.__deplete_items_from_daily_stocks(name, amount, current_date)
				
				else:
					item[1] = stock  # Assign the stocks to the proper value
					if self.__db_sell:
						string = '\n[$] Successfully sold {0} {1}(s)!'.format(amount, name)
						#print(string)
						self.__debug_str += string
					
					self.__deplete_items_from_daily_stocks(name, amount, current_date)
		
		# If no match is found, there is no stock available
		if match is False:
			if self.__db_sell:
				string = '\n[x] Out of stock, cannot sell {0} {1}(s).'.format(amount, name)
				#print(string)
				self.__debug_str += string
			
			self.__deplete_items_from_daily_stocks(name, 0, current_date)
			self.__determine_order(name, amount, current_date)
			return amount
		
		self.__check_expiry(current_date)  # Check for and remove expired items
	
	def estimate_sales(self, days):
		demand_average = self.__get_demand_average()
		date = list(self.__daily_stocks.keys())[-1]
		
		if self.__debug:
			string = '\n\n******** Estimating future sales for {} day(s) ********'.format(days)
			#print(string)
			self.__debug_str += string
		
		for i in range(days):
			date = date + timedelta(days=1)
			
			for name in demand_average:
				amount = round(demand_average[name], ROUND)
				self.sell(name, amount, date)
	
	def get_daily_stocks(self):
		""" Returns self.__daily_stocks. """
		return self.__daily_stocks
	
	def get_orders(self):
		""" Returns self.__orders """
		return self.__orders
	
	def get_restart_counter(self):
		""" Returns self.__restart_counter """
		return self.__restart_counter
	
	def get_debug(self):
		""" Return a string of debug statements """
		return self.__debug_str

# Locally testing
if __name__ == '__main__':
	start_date = date(2019, 5, 19)
	sale_date_1 = date(2019, 5, 20)
	sale_date_2 = date(2019, 5, 21)
	
	stocks = StocksQueue('+-$>')
	
	stocks.add('apple', 10, date(2019, 5, 14))
	stocks.add('potato', 2, date(2019, 5, 15))
	stocks.add('sweet potato', 43, date(2019, 5, 16))
	stocks.add('celery', 12, date(2019, 5, 17))
	stocks.add('pear', 21, date(2019, 5, 18))
	
	stocks.add('carrot', 30, start_date)
	stocks.add('potato', 100, start_date)
	stocks.add('carrot', 50, start_date)
	stocks.add('apple', 50, start_date)
	
	stocks.sell('carrot', 81, sale_date_1)
	stocks.sell('carrot', 50, sale_date_1)
	stocks.sell('apple', 20, sale_date_2)
	stocks.sell('potato', 1.2, sale_date_2)
	
	stocks.estimate_sales(3)

	print(stocks.get_debug())

'''
~~~~~~~~ PSUEDO CODE ~~~~~~~~

stocks = StocksQueue()

# add(name, amount, expiry_date)
stocks.add('carrots', 30.0, datetime.date(2019, 5, 25))
stocks.add('biscuits_sweet', 50.0, datetime.date(2019, 6, 3))
stocks.add('carrots', 10.0, 180, datetime.date(2019, 05, 30))

# buy(name, amount, price)
stocks.buy('carrots', 1, 3)

stocks.check_expiry()
# for name in stocks:
	if name.expiry_date == today:
		stocks.buy(name, 1, 0)
'''
