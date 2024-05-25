import pandas as pd
import matplotlib.pyplot as plt

# Load the new CSV file without the total row
new_file_path_corrected = '/mnt/data/ACSDT1Y2022.B19001-2024-05-25T031552.csv'
new_data_corrected = pd.read_csv(new_file_path_corrected)

# Calculate the total number of households
total_households_corrected = new_data_corrected['Households'].str.replace(',', '').astype(int).sum()

# Ensure that 'Households' column is of integer type without any issues
new_data_corrected['Households'] = new_data_corrected['Households'].astype(int)

# Calculate cumulative household counts
new_data_corrected['Cumulative Households'] = new_data_corrected['Households'].cumsum()

# Calculate cumulative percentiles
new_data_corrected['Cumulative Percentile'] = new_data_corrected['Cumulative Households'] / total_households_corrected * 100

# Interpolate the median income
median_household_count = total_households_corrected / 2
median_row_index = new_data_corrected[new_data_corrected['Cumulative Percentile'] >= 50].index[0]
median_row = new_data_corrected.loc[median_row_index]
previous_row = new_data_corrected.iloc[median_row_index - 1]
lower_bound = int(median_row['Income Range'].split(' ')[0].replace('$', '').replace(',', ''))
upper_bound = int(median_row['Income Range'].split(' ')[-1].replace('$', '').replace(',', ''))
cumulative_households_before = previous_row['Cumulative Households']
interpolated_median_income = lower_bound + ((total_households_corrected / 2 - cumulative_households_before) / median_row['Households']) * (upper_bound - lower_bound)

# Define the income thresholds for 30%, 50%, 80%, and 120% of the median income
thresholds = {
    '30% of Median': 0.3 * interpolated_median_income,
    '50% of Median': 0.5 * interpolated_median_income,
    '80% of Median': 0.8 * interpolated_median_income,
    '120% of Median': 1.2 * interpolated_median_income
}

# Function to interpolate percentile for a given income threshold
def interpolate_percentile_for_income(income, data):
    for i in range(len(data) - 1):
        if data['Income Range'].iloc[i].startswith("Less than"):
            lower_income_bound = 0
            upper_income_bound = int(data['Income Range'].iloc[i].split(' ')[-1].replace('$', '').replace(',', ''))
        else:
            lower_income_bound = int(data['Income Range'].iloc[i].split(' ')[0].replace('$', '').replace(',', ''))
            upper_income_bound = int(data['Income Range'].iloc[i].split(' ')[-1].replace('$', '').replace(',', ''))
        
        if lower_income_bound <= income <= upper_income_bound:
            lower_percentile_bound = data['Cumulative Percentile'].iloc[i]
            upper_percentile_bound = data['Cumulative Percentile'].iloc[i + 1]
            interpolated_percentile = lower_percentile_bound + ((income - lower_income_bound) / (upper_income_bound - lower_income_bound)) * (upper_percentile_bound - lower_percentile_bound)
            return interpolated_percentile
    return None

# Calculate interpolated percentiles for each threshold
interpolated_percentiles = {key: interpolate_percentile_for_income(value, new_data_corrected) for key, value in thresholds.items()}

# Create a DataFrame to display the results
results = pd.DataFrame({
    'Income Threshold': thresholds.values(),
    'Percentile': interpolated_percentiles.values()
}, index=thresholds.keys())

# Define HUD income groups
hud_groups = {
    'Extremely Low': (0, thresholds['30% of Median']),
    'Very Low': (thresholds['30% of Median'], thresholds['50% of Median']),
    'Low': (thresholds['50% of Median'], thresholds['80% of Median']),
    'Moderate': (thresholds['80% of Median'], thresholds['120% of Median']),
    'Above Moderate': (thresholds['120% of Median'], float('inf'))
}

# Correct the function to format income ranges as requested
def calculate_percentage_of_households(income_range, data):
    lower_income, upper_income = income_range
    lower_percentile = interpolate_percentile_for_income(lower_income, data)
    upper_percentile = interpolate_percentile_for_income(upper_income, data) if upper_income != float('inf') else 100
    percentage = upper_percentile - lower_percentile
    if lower_income == 0:
        income_range_str = f"Less than ${int(upper_income):,}"
    elif upper_income == float('inf'):
        income_range_str = f"Above ${int(lower_income):,}"
    else:
        income_range_str = f"${int(lower_income):,} - ${int(upper_income):,}"
    return percentage, income_range_str

# Recalculate the percentage of households and income range for each HUD income group
hud_group_percentages = {group: calculate_percentage_of_households(income_range, new_data_corrected) for group, income_range in hud_groups.items()}

# Create a DataFrame to display the results
hud_group_df = pd.DataFrame.from_dict(hud_group_percentages, orient='index', columns=['Percentage of Households', 'Income Range'])
hud_group_df.reset_index(inplace=True)
hud_group_df.rename(columns={'index': 'HUD Income Group'}, inplace=True)

# Create the bar chart
plt.figure(figsize=(10, 6))
bars = plt.bar(hud_group_df['HUD Income Group'], hud_group_df['Percentage of Households'], color='skyblue')

# Add labels to each bar
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f"{height:.1f}%", ha='center', va='bottom')
    plt.text(bar.get_x() + bar.get_width() / 2, height / 2, hud_group_df['Income Range'].iloc[i], ha='center', va='center', fontsize=10, color='black', bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))

# Add title and labels
plt.title('Percentage of Households by HUD Income Level, City and County of San Francisco')
plt.xlabel('HUD Income Level')
plt.ylabel('Percentage of Households')
plt.ylim(0, 30)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the plot
plt.tight_layout()
plt.show()
