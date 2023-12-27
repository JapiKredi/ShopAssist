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
print(filtered_laptops[['Brand', 'Model Name', 'Price', 'Currency']])

#These lines create a copy of the laptop_df DataFrame and assign it to filtered_laptops.
    #They then modify the 'Price' column in filtered_laptops by removing commas and converting the values to integers.
    #Finally, they filter filtered_laptops to include only rows where the 'Price' is less than or equal to the budget.

mappings = {
        'low': 0,
        'medium': 1,
        'high': 2
    }
# Create 'Score' column in the DataFrame and initialize to 0
filtered_laptops['Score'] = 0
for index, row in filtered_laptops.iterrows():
    user_product_match_str = row['laptop_feature']
    laptop_values = extract_dictionary_from_string(user_product_match_str)
    score = 0

    for key, user_value in user_requirements.items():
        if key.lower() == 'budget':
            continue  # Skip budget comparison
        laptop_value = laptop_values.get(key, None)
        laptop_mapping = mappings.get(laptop_value.lower(), -1)
        user_mapping = mappings.get(user_value.lower(), -1)
        if laptop_mapping >= user_mapping:
            ### If the laptop value is greater than or equal to the user value the score is incremented by 1
            score += 1

    filtered_laptops.loc[index, 'Score'] = score

# Sort the laptops by score in descending order and return the top 5 products
top_laptops = filtered_laptops.drop('laptop_feature', axis=1)
top_laptops = top_laptops.sort_values('Score', ascending=False).head(3)

return top_laptops.to_json(orient='records')




