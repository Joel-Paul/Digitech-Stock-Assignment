# Digitech-Stock-Assignment
A program I created for my Digital Technologies assignment in 2019.
It determines the most cost effective way of restocking produce based on their initial stock, expiry and delivery times, and sales.

`stocks_dict.py` convers all the .csv files from the `data/` folder into dictionaries, so they are easier to access, modify, and use.

`stocks_queue.py` then uses this information to store the number of stock currently available and handles ordering/selling/expiring produce.
It uses a First In First Out queue so that older batches of produce are sold before newer batches.
It will first run a simulation using the selling data and initial stock of produce.
If an item cannot be sold because it is out of stock, the script will calculate the date at which the item must be ordered so it arrives before being sold,
and restarts the simulation. The script completes when the simulation is able to successfully sell produce without going out of stock.
If desired, future sales can be estimated and simulated for a specified number of days, based on the average number of items bought.

`stocks_text.py` uses both these scripts to obtain the list of what items should be ordered when, so that none of the produce goes out of stock.
This is outputted to the screen.

This program was originally made using Pythonista 3 for iOS (https://apps.apple.com/us/app/pythonista-3/id1085978097).

## Running
* Run `python stock_text.py` in command prompt.

**Note:** `stock_ui.py` requires the `ui` module, which is provided by [Pythonista](https://apps.apple.com/us/app/pythonista-3/id1085978097).
If you are using Pythonista, you also have the option to use this script instead.
