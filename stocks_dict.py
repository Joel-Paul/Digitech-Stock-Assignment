# Joel Paul, Term 2 2019
# Digital Technologies Stage 2


import csv
import datetime
from collections import OrderedDict


CSV_INITIAL_STOCK = 'data/Initial_Stock.csv'
CSV_ITEM_CATEGORIES = 'data/Item_categories.csv'
CSV_STOCK_CATEGORIES = 'data/Stock_categories.csv'

SALES = 'data/Sales.csv'


class StocksDict():
	def __init__(self):
		""" Initialise stock variables. """
		# Initial stock
		self.__initial_stock = self.__csv_to_dict(CSV_INITIAL_STOCK, '\ufeffItem name', 'Number')
		# Item categories
		self.__item_categories = self.__csv_to_dict(CSV_ITEM_CATEGORIES, '\ufeffItem name', 'Category')
		# Stock categories
		self.__holding_times = self.__csv_to_dict(CSV_STOCK_CATEGORIES, 'Category', 'Holding time (days)')
		# Delivery times
		self.__delivery_times = self.__csv_to_dict(CSV_STOCK_CATEGORIES, 'Category', 'Delivery times')
		# Sales
		self.__sales = self.__sales_to_dict(SALES)
	
	def __csv_to_dict(self, file, column1, column2):
		""" Return a dictionary of the CVS file. """
		dict = {}
		with open(file, encoding='utf-8') as csv_file:
			reader = csv.DictReader(csv_file) # Object to read CSV file
			
			for csv_dict in list(reader):
				# Turn number strings into a float
				# Don't turn letter strings into a float
				# Needed since this function is used to convert both categories and amounts
				try:
					dict[csv_dict[column1]] = float(csv_dict[column2])
				except ValueError:
					dict[csv_dict[column1]] = csv_dict[column2]
		
		#print(dict, '\n')
		return dict
	
	def __sales_to_dict(self, file):
		""" Return a list nested in an ordered dictionary of amount of items sold. """
		sales = OrderedDict()
		with open(file, encoding='utf-8') as csv_file:
			reader = csv.DictReader(csv_file) # Object to read CSV file
			
			for csv_dict in list(reader):
				# Get the values for each coloumn
				
				''' Convert dates from dd/mm/yy string to datetime object format '''
				date = csv_dict['\ufeffDate']
				date = date.split('/')  # Split into individual components
				
				day = int(date[0])
				month = int(date[1])
				# Add 2000 to the year as only the last two digits are given
				year = int(date[2]) + 2000
				
				date = datetime.date(year, month, day) # The datetime object
				''' ------------------------------------------------------------ '''
				
				item = csv_dict['Item_name']
				amount = float(csv_dict['Number'])
				
				# Append the sales to the dictionary list
				# or create a new one if it doesn't exist
				try:
					sales[date].append({item:amount})
				except KeyError:
					sales[date] = [{item:amount},]
		
		return sales
	
	def get_initial_stock(self):
		""" Return dictionary of initial stock """
		return self.__initial_stock
	
	def get_item_categories(self):
		""" Return dictionary of item categories """
		return self.__item_categories
	
	def get_holding_times(self):
		""" Return dictionary of stock categories """
		return self.__holding_times
	
	def get_delivery_times(self):
		""" Return dictionary of delivery times """
		return self.__delivery_times
	
	def get_sales(self):
		""" Return dictionary of sales """
		return self.__sales
	
	def get_sum_of_sales(self):
		""" Return dictinoary of sum of sales """
		sum_sales = {}  # Dict to hold sales
		
		# Add up the sales
		for date in self.__sales:
			items = self.__sales[date]
			
			for item in items:
				for name in item:
					
					amount = item[name]
					
					try:
						# Try to append to the item if it exists
						sum_sales[name] += amount
					except KeyError:
						# If the item does not exist, create it
						sum_sales[name] = amount
		
		return sum_sales
	
	def get_average_sales(self):
		""" Return dictionary of average sales """
		average_sales = {}
		
		sum_sales = self.get_sum_of_sales()
		days = len(self.__sales)
		
		for name in sum_sales:
			amount = sum_sales[name]
			rate = amount / days
			average_sales[name] = rate
		
		return average_sales

# Local testing
if __name__ == '__main__':
	stocks_dict = StocksDict()
	print(stocks_dict.get_average_sales())
