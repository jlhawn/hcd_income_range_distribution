# US Census and California HCD Income Ranges

## Overview

This project aims to visualize the distribution of household incomes across various jurisdictions in California using data from the US Census. By applying the California Department of Housing and Community Development (HCD) income range definitions, we can categorize households into extremely low, very low, low, moderate, and above moderate income groups. This approach allows us to see how many households in each county fall into these categories based on the actual income distribution from the Census data.

## Motivation

The HCD defines income ranges based on percentages of the median income, which does not directly convey the number of households in each category. This project bridges that gap by using US Census data to show the actual percentage of households in each county that fall into these HCD-defined income ranges. This information is crucial for addressing issues related to housing affordability, economic development, and social equity in California. By visualizing this data, we aim to provide insights that can inform policy decisions and community planning.

### Visualizations

- `charts/`: This directory contains subdirectories for the generated charts:
  - `census_income_ranges/`: Contains bar charts showing the percentage of households in various income ranges as defined by the US Census for each jurisdiction.
  - `hcd_income_ranges/`: Contains bar charts showing the percentage of households in various income ranges as defined by the HCD income categories for each jurisdiction.

### Example Charts

To find the generated chart images, navigate to the `charts` directory. Here you will find:
- `census_income_ranges/`: Bar charts illustrating the income distribution based on US Census data.
- `hcd_income_ranges/`: Bar charts illustrating the income distribution based on California Department of Housing and Community Development (HCD) income range definitions.

Each chart is named after the respective jurisdiction, making it easy to locate and analyze the data for specific regions.
