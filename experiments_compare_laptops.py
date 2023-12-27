


laptop_df= pd.read_csv('updated_laptop.csv')
user_requirements = extract_dictionary_from_string(user_req_string)
print(currency_conversion_rate)
budget = int(user_requirements.get('budget', '0').replace(',', '').split()[0])
    
#This line retrieves the value associated with the key 'budget' from the user_requirements dictionary.
#If the key is not found, the default value '0' is used.
#The value is then processed to remove commas, split it into a list of strings, and take the first element of the list.
#Finally, the resulting value is converted to an integer and assigned to the variable budget.


filtered_laptops = laptop_df.copy()
filtered_laptops['Price'] = filtered_laptops['Price'].str.replace(',','').astype(int)
filtered_laptops['Price'] = filtered_laptops['Price'] * currency_conversion_rate
filtered_laptops = filtered_laptops[filtered_laptops['Price'] <= budget].copy()
print(filtered_laptops)
