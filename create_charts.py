import json
import matplotlib.pyplot as plt
import os

# Load the prepared data
with open('prepared_data.json') as f:
    prepared_data = json.load(f)


# Preprocess the data: Replace `None` with `Infinity` for upper bounds
def replace_none_with_infinity(obj):
    if isinstance(obj, list):
        return [replace_none_with_infinity(item) for item in obj]
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'income_upper_bound' and value is None:
                obj[key] = float('inf')
            else:
                obj[key] = replace_none_with_infinity(value)
    return obj


prepared_data = replace_none_with_infinity(prepared_data)


# Function to create and save bar charts
def create_bar_charts(data):
    os.makedirs('charts/census_income_ranges', exist_ok=True)
    os.makedirs('charts/hcd_income_ranges', exist_ok=True)

    for county in data:
        jurisdiction = county['jurisdiction']
        safe_jurisdiction_name = jurisdiction.replace(",", "").replace(" ", "_")

        # Census Income Ranges
        census_income_ranges = county['census_income_ranges']
        census_labels = []
        for item in census_income_ranges:
            lower_bound = item['income_lower_bound']
            upper_bound = item['income_upper_bound']
            if lower_bound == 0:
                label = f"Less than ${int(upper_bound):,}"
            elif upper_bound == float('inf'):
                label = f"${int(lower_bound):,} or more"
            else:
                label = f"${int(lower_bound):,} - ${int(upper_bound):,}"
            census_labels.append(label)
        
        census_values = [item['upper_percentile'] - item['lower_percentile'] for item in census_income_ranges]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(census_labels, census_values)
        plt.xlabel('Income Range')
        plt.ylabel('Percentage of Households (%)')
        plt.title(f'Census Income Ranges - {jurisdiction}')
        plt.xticks(rotation=45, ha='right')
        
        # Adding percentage labels on top of each bar
        for bar, value in zip(bars, census_values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(f'charts/census_income_ranges/{safe_jurisdiction_name}.png')
        plt.close()

        # HCD Income Ranges
        hcd_income_ranges = county['hcd_income_ranges']
        hcd_labels = [item['label'] for item in hcd_income_ranges]
        hcd_values = [item['upper_percentile'] - item['lower_percentile'] for item in hcd_income_ranges]

        plt.figure(figsize=(12, 6))
        bars = plt.bar(hcd_labels, hcd_values)
        plt.xlabel('Income Range')
        plt.ylabel('Percentage of Households (%)')
        plt.title(f'HCD Income Ranges - {jurisdiction}')
        
        # Adding percentage labels on top of each bar
        for bar, value in zip(bars, hcd_values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{value:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(f'charts/hcd_income_ranges/{safe_jurisdiction_name}.png')
        plt.close()

# Create and save the bar charts
create_bar_charts(prepared_data)
