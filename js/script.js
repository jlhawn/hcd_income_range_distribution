document.addEventListener('DOMContentLoaded', function() {
    fetch('prepared_data.json')
        .then(response => response.json())
        .then(data => {
            const jurisdictionSelect = document.getElementById('jurisdictionSelect');
            data.forEach(county => {
                const option = document.createElement('option');
                option.value = county.jurisdiction;
                option.text = county.jurisdiction;
                jurisdictionSelect.appendChild(option);
            });

            function updateCharts(jurisdiction) {
                if (jurisdiction) {
                    const county = data.find(c => c.jurisdiction === jurisdiction);
                    const safeJurisdictionName = jurisdiction.replace(/,/g, '').replace(/ /g, '_');
                    document.getElementById('jurisdictionName').textContent = jurisdiction;
                    document.getElementById('medianIncome').textContent = `$${county.median_income.toLocaleString()}`;

                    // Update HCD income ranges
                    const hcdIncomeRanges = document.getElementById('hcdIncomeRanges');
                    hcdIncomeRanges.innerHTML = '';
                    county.hcd_income_ranges.forEach(range => {
                        const lowerBound = range.income_lower_bound;
                        const upperBound = range.income_upper_bound;
                        let label;
                        if (lowerBound === 0) {
                            label = `Less than $${upperBound.toLocaleString()}`;
                        } else if (upperBound === null) {
                            label = `$${lowerBound.toLocaleString()} or more`;
                        } else {
                            label = `$${lowerBound.toLocaleString()} - $${upperBound.toLocaleString()}`;
                        }
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `<b>${range.label}</b>: ${label}`;
                        hcdIncomeRanges.appendChild(listItem);
                    });

                    document.getElementById('censusChartTitle').textContent = `Census Income Ranges - ${jurisdiction}`;
                    document.getElementById('censusChart').src = `charts/census_income_ranges/${safeJurisdictionName}.png`;
                    document.getElementById('hcdChartTitle').textContent = `HCD Income Ranges - ${jurisdiction}`;
                    document.getElementById('hcdChart').src = `charts/hcd_income_ranges/${safeJurisdictionName}.png`;
                } else {
                    document.getElementById('jurisdictionName').textContent = '';
                    document.getElementById('medianIncome').textContent = '';
                    document.getElementById('hcdIncomeRanges').innerHTML = '';
                    document.getElementById('censusChartTitle').textContent = '';
                    document.getElementById('censusChart').src = '';
                    document.getElementById('hcdChartTitle').textContent = '';
                    document.getElementById('hcdChart').src = '';
                }
            }

            // Automatically select the first county and display its charts
            if (data.length > 0) {
                jurisdictionSelect.selectedIndex = 1; // The first county is at index 1 (index 0 is "--Select--")
                const firstJurisdiction = data[0].jurisdiction;
                updateCharts(firstJurisdiction);
            }

            jurisdictionSelect.addEventListener('change', function() {
                const selectedJurisdiction = this.value;
                updateCharts(selectedJurisdiction);
            });
        })
        .catch(error => console.error('Error loading prepared_data.json:', error));
});