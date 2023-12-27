import pandas as pd

laptop_df= pd.read_csv('updated_laptop.csv')
budget = 1000
currency_conversion_rate = 0.012000385202430809
currency_symbol = 'USD"'

#This line retrieves the value associated with the key 'budget' from the user_requirements dictionary.
#If the key is not found, the default value '0' is used.
#The value is then processed to remove commas, split it into a list of strings, and take the first element of the list.
#Finally, the resulting value is converted to an integer and assigned to the variable budget.


filtered_laptops = laptop_df.copy()
filtered_laptops['Price'] = filtered_laptops['Price'].str.replace(',','').astype(int)
filtered_laptops['Price'] = filtered_laptops['Price'] * currency_conversion_rate
filtered_laptops['Currency'] = currency_symbol

filtered_laptops = filtered_laptops[filtered_laptops['Price'] <= budget].copy()
print(filtered_laptops['Brand', 'Model Name', 'Price', 'Currency'])
