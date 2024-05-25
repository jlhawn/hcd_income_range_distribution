import json

hcd_income_range_multiples_of_median = [
    (0, 0.3, 'Extremely Low Income'),
    (0.3, 0.5, 'Very Low Income'),
    (0.5, 0.8, 'Low Income'),
    (0.8, 1.2, 'Moderate Income'),
    (1.2, float('inf'), 'Above Moderate Income'),
]

def linear_interpolate(a, a_min, a_max, b_min, b_max):
    """
    Interpolates a value 'a' within the range [a_min, a_max]
    to a value 'b' within the range [b_min, b_max].
    
    Parameters:
    - a (float): The input value to interpolate.
    - a_min (float): The minimum value of the input range.
    - a_max (float): The maximum value of the input range.
    - b_min (float): The minimum value of the output range.
    - b_max (float): The maximum value of the output range.
    
    Returns:
    - float: The interpolated value in the range [b_min, b_max].
    """
    # Calculate the relative position of 'a' within [a_min, a_max]
    relative_position = (a - a_min) / (a_max - a_min)
    
    # Map the relative position to the output range [b_min, b_max]
    b = b_min + relative_position * (b_max - b_min)
    
    return b


with open('group.json') as f:
    group = json.load(f)
    variables = group['variables']

with open('data.json') as f:
    raw_data = json.load(f)

assert len(raw_data) > 0

label_indices = {}
census_income_range_bounds = []

# The first entry in raw data contains labels for the following entries.
for i, label_id in enumerate(raw_data[0]):
    label_indices[label_id] = i

    if not (label_id.startswith('B19001_') and label_id.endswith('E')):
        continue # Only interested in estimates.

    # This label actually provides an estimated data point as opposed to
    # an annotation or margin of error for a data point.

    raw_label = variables[label_id]['label']
    # The raw label is a concatenation of whether it's an estimate or
    # margin of error followed by the actual label using '!!'.
    label = raw_label.split('!!')[-1]

    if label == 'Total:':
        label_indices['total_households'] = i
        continue
    
    if label.startswith('Less than $'):
        lower_bound = 0
        upper_bound = int(label.replace('Less than $', '').replace(',', ''))
    elif label.endswith(' or more'):
        lower_bound = int(label.replace(' or more', '').replace('$', '').replace(',', ''))
        upper_bound = float('inf')
    else:
        lower_bound, upper_bound = [
            int(s.lstrip('$').replace(',', '')) for s in label.split(' to ')
        ]

    census_income_range_bounds.append((lower_bound, upper_bound, label_id))

census_income_range_bounds.sort()

prepared_data = []

for county_data in raw_data[1:]:
    county = county_data[label_indices['NAME']]
    census_income_ranges = []
    county_total_households = int(county_data[label_indices['total_households']])
    cumulative_total = 0
    cumulative_percentile = 0

    median_income = None

    for lower_bound_income, upper_bound_income, label_id in census_income_range_bounds:
        range_total_households = int(county_data[label_indices[label_id]])
        range_percentage = range_total_households / county_total_households * 100

        lower_percentile = cumulative_percentile
        cumulative_percentile += range_percentage
        upper_percentile = cumulative_percentile

        if lower_percentile <= 50 <= upper_percentile:
            median_income = linear_interpolate(
                50, lower_percentile, upper_percentile,
                lower_bound_income, upper_bound_income,
            )

        census_income_ranges.append({
            'households': range_total_households,
            'income_lower_bound': lower_bound_income,
            'income_upper_bound': upper_bound_income,
            'lower_percentile': lower_percentile,
            'upper_percentile': upper_percentile,
        })

    assert median_income is not None, "Median income calculation failed. Check input data."

    hcd_income_range_gen = (
        (median_income*lower_bound_multiple, median_income*upper_bound_multiple, label)
        for (lower_bound_multiple, upper_bound_multiple, label)
        in hcd_income_range_multiples_of_median
    )

    hcd_income_ranges = []

    hcd_income_range_lower_bound, hcd_income_range_upper_bound, hcd_income_range_label = next(hcd_income_range_gen)
    hcd_income_range_households = 0
    cumulative_percentile = 0


    def capture_hcd_income_range(census_income_lower_bound, census_income_upper_bound, census_range_households):
        global hcd_income_range_lower_bound
        global hcd_income_range_upper_bound
        global hcd_income_range_label
        global hcd_income_range_gen
        global cumulative_percentile
        global hcd_income_range_households
        global hcd_income_ranges

        if hcd_income_range_upper_bound == float('inf'):
            # capturing the last range. Assume the last census income range
            # was already added to the cumulative total of households in this
            # last hcd range.
            households_to_hcd_range = 0
            households_in_next_hcd_range = 0
        else:
            # Need to interpolate how many households belong in this range.
            households_to_hcd_range = linear_interpolate(
                hcd_income_range_upper_bound,
                census_income_lower_bound,
                census_income_upper_bound,
                0,
                census_range_households
            )

            households_in_next_hcd_range = census_range_households - households_to_hcd_range
            hcd_income_range_households += households_to_hcd_range

        range_percentage = hcd_income_range_households / county_total_households * 100
        lower_percentile = cumulative_percentile
        cumulative_percentile += range_percentage
        upper_percentile = cumulative_percentile

        hcd_income_ranges.append({
            'label': hcd_income_range_label,
            'households': hcd_income_range_households,
            'income_lower_bound': hcd_income_range_lower_bound,
            'income_upper_bound': hcd_income_range_upper_bound,
            'lower_percentile': lower_percentile,
            'upper_percentile': upper_percentile,
        })

        hcd_income_range_households = households_in_next_hcd_range


    for census_range_data in census_income_ranges:
        census_income_lower_bound = census_range_data['income_lower_bound']
        census_income_upper_bound = census_range_data['income_upper_bound']
        census_range_households = census_range_data['households']

        if hcd_income_range_upper_bound >= census_income_upper_bound:
            hcd_income_range_households += census_range_households
        else:
            # Reached end of an hcd income range.
            capture_hcd_income_range(census_income_lower_bound, census_income_upper_bound, census_range_households)
            # This should not raise a StopIteration exception because the last
            # range has an upper bound of infinity which is handled by the
            # first if case above always being True.
            hcd_income_range_lower_bound, hcd_income_range_upper_bound, hcd_income_range_label = next(hcd_income_range_gen)
    
    # Capture the last hcd range.
    capture_hcd_income_range(census_income_lower_bound, census_income_upper_bound, census_range_households)

    prepared_data.append({
        'jurisdiction': county,
        'total_households': county_total_households,
        'census_income_ranges': census_income_ranges,
        'hcd_income_ranges': hcd_income_ranges,
    })


# Preprocess the data: Replace `Infinity` with `None`
def replace_infinity(obj):
    if isinstance(obj, list):
        return [replace_infinity(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: replace_infinity(value) for key, value in obj.items()}
    elif obj == float('inf'):
        return None  # You can use a large number instead, e.g., float('1e308')
    else:
        return obj


with open('prepared_data.json', 'w') as f:
    json.dump(replace_infinity(prepared_data), f, indent=4)

