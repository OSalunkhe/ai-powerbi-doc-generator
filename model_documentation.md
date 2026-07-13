# Power BI Model Documentation

_Auto-generated with Claude - review before treating as final._


## Table: Analysis DAX

### Net Sales

```dax
CALCULATE(SUM(Sales[Amount]),Sales[Status]="Sold")
```

1. **Plain English:** This measure calculates the total sales revenue from only those transactions marked as "Sold" status.

2. **Risk Note:** The status value "Sold" is hardcoded—confirm this matches your actual data values exactly (case-sensitive) and consider whether other statuses like "Pending" or "Cancelled" should be included or excluded.

---

## Table: Design DAX

### Product Top N

```dax

SWITCH(
    TRUE(),
    ISINSCOPE('Product'[Product]),
    RANKX(ALL('Product'[Product]),[Net Sales],,DESC),
    ISINSCOPE('Product'[Segment]),
    RANKX(ALL('Product'[Segment]),[Net Sales],,DESC),
    RANKX(ALL('Product'[Category]),[Net Sales],,DESC)
)
```

**Plain English:** This measure ranks items by sales—products when viewing product details, segments when viewing by segment, or categories by default.

**Risk Note:** The measure assumes [Net Sales] exists and is in scope; it will fail silently if the measure is missing or if an unexpected grouping level is encountered in a visual.

---
### Product Sales Top 3

```dax
IF([Product Top N]<4,[Net Sales],0)
```

**Plain-English Description:**
This measure shows sales revenue only for the top 3 products, hiding sales for all others.

**Risk Note:**
The hardcoded value "4" assumes [Product Top N] is a ranking measure where top 3 = values 1-3. Verify this ranking logic is correct and that [Product Top N] is properly defined elsewhere in the model.

---
### Product Sales Other

```dax
IF([Product Top N]>3,[Net Sales],0)
```

**Plain-English Description:**
This measure shows net sales only for products ranked 4th or lower in your top performers list, hiding sales for your top 3 products.

**Technical Note:**
The hardcoded value "3" assumes a [Product Top N] measure exists and returns numeric rankings. Verify this dependency exists and that the ranking logic aligns with business intent.

---

## Table: Analysis DAX

### Net Sales PM

```dax
CALCULATE([Net Sales],PREVIOUSMONTH('Calendar'[Date]))
```

**Plain-English Description:**
This measure shows your net sales from the previous month, allowing you to compare current month performance against the prior month.

**Risk Note:**
Verify that the 'Calendar' table is properly marked as a date table in Power BI settings; otherwise, PREVIOUSMONTH may not function correctly.

---
### Last 2 Months Net Sales

```dax
[Net Sales]+[Net Sales PM]
```

**Plain-English Description:**
This measure adds together the net sales from the current period and the previous month to show a combined two-month sales total.

**Risk Note:**
Verify that [Net Sales PM] reliably calculates the prior month—if context filters or date logic are incorrect upstream, this could produce misleading totals.

---

## Table: Design DAX

### Store Top N

```dax
RANKX(ALL('Store'[Store]),[Net Sales],,DESC)
```

**Plain English:** This measure ranks each store by its net sales in descending order, showing which store ranks highest.

**Risk Note:** Missing context filter—this ranks across ALL stores regardless of report filters (date, region, etc.), which may cause unexpected behavior if users expect context-aware rankings. Consider whether ALL() is intentional here.

---
### Store Sales Other

```dax
IF([Store Top N]>3,[Net Sales],0)
```

**Plain-English Description:**
This measure shows sales revenue only for stores ranked 4th and beyond, hiding sales from the top 3 stores.

**Risk Note:**
The hardcoded value "3" assumes a specific ranking threshold; verify this aligns with business requirements and confirm that [Store Top N] is always populated to avoid unexpected zeros.

---
### Store Sales Top 3

```dax
IF([Store Top N]<4,[Net Sales],0)
```

**Plain-English Description:**
This measure shows sales revenue only for the top 3 stores by some ranking, and returns zero for all other stores.

**Risk Note:**
The hardcoded value of 4 is unclear—verify this logic matches the intended "top 3" definition, and confirm that [Store Top N] is properly calculated elsewhere in the model.

---

## Table: Analysis DAX

### Net Sales Variance

```dax
[Net Sales]-[Net Sales PM]
```

**Plain English Description:**
This measure shows the difference between current period net sales and the previous month's net sales, indicating whether sales increased or decreased.

**Technical Note:**
No obvious issues. However, verify that [Net Sales PM] correctly references previous month data through your date table relationship, as the logic depends entirely on proper time intelligence setup.

---
### Net Sales Variance %

```dax
DIVIDE([Net Sales],[Net Sales PM],0)-1
```

**Plain English Description:**
This measure shows the percentage change in net sales compared to the previous month.

**Risk/Clarity Note:**
Verify that [Net Sales PM] correctly references previous month data—if the time intelligence logic is misconfigured, comparisons could be inaccurate. Also confirm the zero default is appropriate for your reporting context.

---

## Table: Design DAX

### Net Sales Indicator

```dax
CONCATENATE(IF([Net Sales Variance %]<=0,"","+"),FORMAT([Net Sales Variance %],"0.0%"))
```

**Plain-English Description:**
This measure displays the net sales variance as a percentage, prefixing positive values with a "+" sign for easy visual identification.

**Risk/Clarity Note:**
No obvious issues. The logic clearly distinguishes positive from non-positive variances, and the formatting is straightforward. Verify that [Net Sales Variance %] is already calculated as a decimal percentage to ensure FORMAT displays correctly.

---

## Table: Analysis DAX

### Units Sold

```dax
CALCULATE(SUM(Sales[Unit]),Sales[Status]="Sold")
```

**Plain English Description:**
This measure totals the quantity of units from all sales transactions that have a status of "Sold."

**Risk/Clarity Note:**
The status value "Sold" is hardcoded—verify this matches the actual values in the Sales[Status] column exactly (case-sensitive), and confirm this is the only relevant status to include.

---
### Units Sold PM

```dax
CALCULATE([Units Sold],PREVIOUSMONTH('Calendar'[Date]))
```

**Plain-English Description:**
This measure shows the total units sold during the previous month relative to whatever month is currently being viewed.

**Risk Note:**
Verify that the 'Calendar' table is properly marked as a date table in Power BI settings, otherwise PREVIOUSMONTH may not function correctly.

---
### Units Sold Variance %

```dax
DIVIDE([Units Sold],[Units Sold PM],0)-1
```

1. This measure shows the percentage change in units sold compared to the previous month.

2. Verify that [Units Sold PM] (previous month) is correctly calculated elsewhere in the model—if it's zero or missing, the result defaults to 0 rather than flagging an error, which could mask data issues.

---

## Table: Design DAX

### Units Sold Indicator

```dax
CONCATENATE(IF([Units Sold Variance %]<=0,"","+"),FORMAT([Units Sold Variance %],"0.0%"))
```

**Plain-English Description:**
This measure displays the percentage change in units sold, prefixing positive values with a "+" sign for clarity.

**Risk/Clarity Note:**
Verify that [Units Sold Variance %] is already calculated as a percentage (0-1 range vs. 0-100 range)—formatting inconsistency could produce misleading results like "+5000.0%" instead of "+5.0%".

---

## Table: Analysis DAX

### Returns

```dax
CALCULATE(SUM(Sales[Amount]),Sales[Status]="Returned")
```

**Plain English Description:**
This measure calculates the total sales amount for all transactions marked as "Returned" status.

**Risk Note:**
The status value "Returned" is hardcoded—if the actual values in the Sales table differ (e.g., "Return", "RETURNED"), this measure will return zero with no warning.

---
### Returns PM

```dax
CALCULATE([Returns],PREVIOUSMONTH('Calendar'[Date]))
```

**Plain English Description:**
This measure shows the total returns from the previous month relative to whatever month is currently selected.

**Risk Note:**
Verify that the Returns measure is defined correctly and that the Calendar table's Date column is properly marked as a date type—otherwise PREVIOUSMONTH may fail silently or produce unexpected results.

---
### Last 2 Months Returns

```dax
[Returns]+[Returns PM]
```

**Plain-English Description:**
This measure adds together the returns from the current month and the previous month.

**Risk/Clarity Note:**
Verify that [Returns PM] is correctly configured to always return the prior month—if filter context changes or the measure uses hard-coded dates, results could be incorrect.

---
### Returns Variance

```dax
[Returns]-[Returns PM]
```

1. This measure shows the difference between current period returns and the previous month's returns.

2. Verify that [Returns PM] is correctly defined as prior month data—if the time intelligence logic is wrong, the variance will be meaningless. Also confirm both measures use consistent filtering/granularity.

---
### Returns Variance %

```dax
(DIVIDE([Returns],[Returns PM],0)-1)
```

**Description:**
This measure calculates the percentage change in returns compared to the previous month.

**Note:**
Verify that [Returns PM] (previous month) is correctly defined elsewhere in the model, as this measure depends entirely on its accuracy. The division safeguard (0) prevents errors but masks potential data issues.

---
### Units Returned

```dax
CALCULATE(SUM(Sales[Unit]),Sales[Status]="Returned")
```

**Plain English:** This measure sums the total quantity of units from sales transactions that have been marked with a "Returned" status.

**Risk Note:** The hardcoded "Returned" string is case-sensitive and brittle—if the actual status values differ (e.g., "RETURNED" or "Returned "), this measure will return zero silently. Verify the exact status values in the source data.

---
### Units Returned PM

```dax
CALCULATE([Units Returned],PREVIOUSMONTH('Calendar'[Date]))
```

1. This measure shows the total number of units returned during the previous month relative to whatever time period is currently selected.

2. Verify that 'Calendar'[Date] is a proper date column with no blanks, and confirm the base [Units Returned] measure handles edge cases (e.g., first month of data). PREVIOUSMONTH may return unexpected results with irregular date tables.

---
### Units Returned Variance %

```dax
DIVIDE([Units Returned],[Units Returned PM],0)-1
```

**Description:**
This measure shows the percentage change in units returned compared to the previous month.

**Risk Note:**
Verify that [Units Returned PM] correctly references prior month data—if the time intelligence setup is missing or incorrect, comparisons will be invalid.

---

## Table: Design DAX

### Returns Indicator

```dax
CONCATENATE(IF([Returns Variance %]<=0,"","+"),FORMAT([Returns Variance %],"0.0%"))
```

**Plain-English Description:**
This measure displays the returns variance as a percentage, prefixing positive values with a "+" sign for visual emphasis.

**Risk Note:**
The measure assumes [Returns Variance %] is already calculated and numeric; it lacks error handling for null/blank values, which could produce unexpected output or errors.

---
### ProductR Top N

```dax

SWITCH(
    TRUE(),
    ISINSCOPE('Product'[Product]),
    RANKX(ALL('Product'[Product]),[Returns],,DESC),
    ISINSCOPE('Product'[Segment]),
    RANKX(ALL('Product'[Segment]),[Returns],,DESC),
    RANKX(ALL('Product'[Category]),[Returns],,DESC)
)
```

**Plain English:** This measure ranks products by their returns performance, adjusting the ranking level depending on whether you're viewing individual products, segments, or categories.

**Risk Note:** The final RANKX (Category) lacks an explicit condition—it executes by default if Product and Segment aren't in scope. Verify this fallback behavior is intentional and test edge cases where multiple scope levels exist simultaneously.

---
### Product Returns Other

```dax
IF([ProductR Top N]>3,[Returns],0)
```

**Plain English Description:**
This measure shows product return amounts only for items ranked outside the top 3, grouping all other returns together.

**Note:**
The hardcoded value "3" lacks documentation—confirm whether this ranking threshold aligns with business requirements and whether it should be parameterized for flexibility.

---
### Product Returns Top 3

```dax
IF([ProductR Top N]<4,[Returns],0)
```

1. This measure shows the return count only for the top 3 products by returns, zeroing out all others.

2. The measure depends on an undefined [ProductR Top N] calculation—verify this helper measure exists and ranks products correctly. The hardcoded "4" threshold assumes top 3, but confirm the ranking logic matches business intent.

---
### StoreR Top N

```dax
RANKX(ALL('Store'[Store]),[Returns],,DESC)
```

**Plain-English Description:**
This measure ranks each store from highest to lowest based on its return volume.

**Risk Note:**
The measure references a [Returns] measure that isn't defined here—verify it exists and calculates correctly. Also confirm whether ranking should reset by report filters (slicer context) or always show global rankings.

---
### Store Returns Other

```dax
IF([StoreR Top N]>3,[Returns],0)
```

**Plain-English Description:**
This measure shows store returns only when a store ranks outside the top 3 performers, otherwise it displays zero.

**Risk Note:**
The hardcoded threshold of 3 is inflexible; consider parameterizing it. Also verify that [StoreR Top N] is properly defined and handles all filtering contexts correctly.

---
### Returns Sales Top 3

```dax
IF([StoreR Top N]<4,[Returns],0)
```

1. This measure shows the return sales amount, but only for stores ranked in the top 3 by returns volume.

2. The hardcoded value "4" assumes [StoreR Top N] is a ranking metric—verify this dependency exists and that the ranking logic is correct. Also confirm what happens when [StoreR Top N] is blank.

---
### Units Returned Indicator

```dax
CONCATENATE(IF([Returns Variance %]<=0,"","+"),FORMAT([Returns Variance %],"0.0%"))
```

**Plain-English Description:**
This measure displays the percentage change in product returns, prefixing positive values with a "+" sign for clarity.

**Risk Note:**
The measure assumes [Returns Variance %] exists and is numeric; it will error if the source measure is missing or invalid. Consider adding error handling with IFERROR() for robustness.

---

## Table: Analysis DAX

### Return Rate

```dax
DIVIDE((ROUND(((DIVIDE([Returns],SUM(Sales[Amount]),0))*100),0)),100,0)
```

**1. Plain-English Description:**
This measure calculates the return rate as a percentage by dividing total returns by total sales and rounding to the nearest whole number.

**2. Risk Assessment:**
Risky: The measure rounds to 0 decimals then divides by 100, creating a percentage that displays as a decimal (e.g., 5% shows as 0.05). Consider formatting instead of dividing by 100 to avoid confusion.

---

## Table: % Return Rate

### % Return Rate Value

```dax
SELECTEDVALUE('% Return Rate'[% Return Rate])/100
```

**Description:**
This measure retrieves a return rate percentage value from a lookup table and converts it to decimal format (e.g., 25% becomes 0.25).

**Risk Note:**
SELECTEDVALUE() returns BLANK if multiple values exist or none match current filters—consider adding error handling or a default value to prevent unexpected blanks in calculations.

---

## Table: Analysis DAX

### WIF Units Returned

```dax
IF([Units Returned]-[WIF Units Returned Average]<0,0,[Units Returned]-[WIF Units Returned Average])
```

1. This measure calculates the number of returned units that exceed the average return rate, showing zero if returns fall below average.

2. Circular reference risk: This measure references [WIF Units Returned Average], which may reference this measure, creating a dependency loop. Verify the measure definition chain to ensure no circular calculations exist.

---
### WIF Units Returned Average

```dax
DIVIDE([WIF Units Returned Difference],CALCULATE(DISTINCTCOUNT('Calendar'[Date]), ALL('Calendar')),0)
```

**Plain English Description:**
This measure divides the total units returned difference by the total number of distinct dates in the calendar to show an average daily return rate.

**Risk Note:**
The DISTINCTCOUNT includes all calendar dates regardless of data availability—consider whether this inflates the denominator with dates containing no actual transactions, potentially understating the average.

---
### WIF Units Returned Difference

```dax
[WIF Units Returned_1]-[WIF Units Returned_2]
```

**Plain-English Description:**
This measure shows the difference in returned units between two time periods or comparison scenarios.

**Technical Note:**
The measure references two other measures without context on what distinguishes them (e.g., time periods, versions). Verify the naming convention is clear and confirm both source measures are correctly defined and up-to-date.

---
### WIF Units Returned_1

```dax
CALCULATE([Units Returned], ALLSELECTED('Calendar'[Date]))
```

**Plain-English Description:**
This measure shows the total units returned across all selected dates in the calendar, ignoring any date filters the user has applied.

**Risk Note:**
The naming convention ("WIF Units Returned_1") suggests a temporary or duplicate measure—confirm whether this is intentional or should be renamed/consolidated with other similar measures.

---
### WIF Units Returned_2

```dax
CALCULATE([WIF Adjusted Units Returned], ALLSELECTED('Calendar'[Date]))
```

1. This measure shows the total units returned, calculated across all selected dates in the calendar regardless of any date filters the user has applied.

2. Verify that [WIF Adjusted Units Returned] is properly defined and that removing date context is the intended behavior—this could produce unexpectedly high totals if users expect date-filtered results.

---
### WIF Adjusted Units Returned

```dax
DIVIDE((SUM(Sales[Unit])*'% Return Rate'[% Return Rate Value]),1,0)
```

**Plain-English Description:**
This measure estimates the number of units expected to be returned by multiplying total sales units by the return rate percentage.

**Risk Note:**
The measure references an external table ('% Return Rate') without specifying which row's value is used—confirm the filter context and that this table contains only one value to avoid unexpected results.

---
### WIF Adjusted Net Sales

```dax
(SUM(Sales[Unit])*[WIF Price per Unit])-DIVIDE((SUM(Sales[Unit])*'% Return Rate'[% Return Rate Value]),1,0)*[WIF Price per Unit]
```

**Plain English:** This measure calculates total sales revenue after accounting for returned units, adjusted by a dynamic price factor.

**Risk Note:** The DIVIDE function's third parameter (1,0) appears redundant—clarify intent. Also verify the '% Return Rate' table relationship is correctly configured to avoid unexpected filtering behavior across contexts.

---
### WIF Price per Unit

```dax
DIVIDE([Net Sales],[Units Sold],0)
```

1. **Plain English:** This measure calculates the average revenue generated per unit sold.

2. **Note:** No obvious issues. The DIVIDE function safely handles division-by-zero scenarios by returning 0. Verify that [Net Sales] and [Units Sold] are correctly defined measures that exclude unwanted filters or calculations.

---
### WIF Profit

```dax
IF([WIF Same]=0,0,IF(ROUNDDOWN([WIF Adjusted Net Sales]-[Net Sales],0)<0,0,ROUNDDOWN([WIF Adjusted Net Sales]-[Net Sales],0)))
```

**Plain English Description:**
This measure calculates the profit gain from a specific adjustment by comparing adjusted and standard net sales, but only when a validation condition is met.

**Risk Note:**
The logic depends on [WIF Same] equaling exactly zero—verify this condition's purpose and whether it should use a threshold instead. Also confirm the rounding behavior is intentional.

---
### Profit Difference

```dax
DIVIDE([WIF Adjusted Sales],[Net Sales],0)-1
```

1. **Plain English:** This measure shows the percentage difference between adjusted sales and net sales, telling you how much the adjustment changes your sales figure.

2. **Note:** Verify that [WIF Adjusted Sales] and [Net Sales] are defined elsewhere in the model and that the 0 default handles division-by-zero appropriately for your use case.

---
### WIF Adjusted Sales

```dax
[WIF Units Returned_1]*[WIF Price per Unit]
```

**Plain English Description:**
This measure calculates the total sales value by multiplying the number of units returned by the price per unit.

**Risk Note:**
Verify that "WIF Units Returned_1" is the correct measure—the "_1" suffix suggests a possible duplicate or version control issue that should be clarified.

---
### WIF Sales

```dax
CALCULATE([Net Sales],ALL('Calendar'[Date].[Month]))
```

**Plain English:** This measure shows total net sales across all months, ignoring any month filtering applied elsewhere in the report.

**Risk Note:** Verify the intention—using ALL on the Month level may inadvertently bypass important date context filtering. Consider whether ALL('Calendar'[Date]) was intended instead, or if this should filter to a specific time period.

---
### WIF Same

```dax
IF([% Return Rate Value]>=CALCULATE([Return Rate],ALL(Store[Type]),ALL(Store[Store])),0,1)
```

**Plain English:** This measure returns 1 if a store's return rate is below the company-wide average, and 0 if it meets or exceeds that average.

**Risk Note:** The logic appears inverted—typically you'd flag stores *above* average as problematic (returning 1). Verify this matches business intent, as the naming suggests checking if performance is "same" rather than "below average."

---
### WIF Forecast

```dax
[Net Sales]+[WIF Profit]
```

**Plain-English Description:**
This measure adds together actual sales revenue and forecasted profit to estimate total financial performance.

**Risk Note:**
Verify that both [Net Sales] and [WIF Profit] are calculated consistently (same currency, same time periods, same business rules) to avoid misleading combined results.

---
### WIF Total Forecast

```dax
CALCULATE([WIF Forecast],ALL('Calendar'[Date].[Month]))
```

**Plain English:** This measure shows the total workforce forecasted across all months, ignoring any month-level filtering the user might have applied.

**Risk Note:** Verify that [WIF Forecast] is properly defined and that removing month context won't cause unintended results in your reporting layout. The ALL function may override user selections unexpectedly.

---
### WIF Total Profit

```dax
CALCULATE([WIF Profit],ALL('Calendar'[Date].[Month]))
```

1. This measure calculates total profit across all months, ignoring any month-level filters that might be applied elsewhere in the report.

2. **Worth checking:** Verify that `[WIF Profit]` is correctly defined and that removing the Month filter is intentional—this could produce unexpected totals if users apply monthly filters expecting them to apply.

---

## Table: Design DAX

### Net Sales Label

```dax
CONCATENATE("",FORMAT([Net Sales],"$0,000"))
```

1. This measure displays the Net Sales value as a formatted currency string (e.g., "$1,000").

2. The leading empty string in CONCATENATE serves no purpose and should be removed. Consider using FORMAT alone instead. Also, verify that [Net Sales] is numeric and handles blank/null values appropriately.

---

## Table: Analysis DAX

### WIF Profit Difference

```dax
DIVIDE([WIF Forecast],[Net Sales],0)-1
```

**Plain-English Description:**
This measure shows how much higher (or lower) the WIF Forecast profit is compared to actual Net Sales, expressed as a percentage difference.

**Risk Note:**
Verify that [WIF Forecast] and [Net Sales] are in the same currency/scale and have appropriate filters applied at query time, as the formula lacks explicit context handling.

---

## Table: Design DAX

### Profit Indicator

```dax
CONCATENATE(IF([WIF Profit Difference]<=0,"","+"),FORMAT([WIF Profit Difference],"0.0%"))
```

1. This measure displays the profit difference as a percentage, adding a plus sign for positive values to make increases visually distinct from decreases.

2. The measure lacks error handling for null/blank values in [WIF Profit Difference], which could return unexpected results. Consider wrapping with IFERROR or adding a check for ISBLANK.

---

## Table: Analysis DAX

### Total Return Rate

```dax
CALCULATE([Return Rate],ALL('Calendar'[Date].[Month]))
```

1. This measure calculates the overall return rate by removing any filtering by month, so it shows the company-wide return rate regardless of which month is currently selected in reports.

2. Verify that [Return Rate] is properly defined and handles division-by-zero cases; also confirm whether ALL() on a month level truly matches the intended aggregation scope.

---

## Table: Design DAX

### Association

```dax
VALUE(CONCATENATE([Product Top N],(SUM(Association[Importance]))))
```

1. This measure combines a product name with its total importance score into a single text value.

2. **Risky:** The CONCATENATE directly joins text and a number without formatting or separators, which could produce unclear results (e.g., "Product A100"). Also, CONCATENATE with VALUE conversion may fail if [Product Top N] isn't numeric-convertible. Consider using a separator and error handling.

---

## Table: Details

### Info Tooltip

```dax
"https://imagizer.imageshack.com/img923/4052/lLHy3U.gif"
```

**Plain-English Description:**
This measure returns a URL link to an animated GIF image that displays as a tooltip in visualizations.

**Risk Assessment:**
Risky: Hardcoded external URL with no fallback if the link breaks or becomes unavailable. Consider storing the URL in a parameter table for easier maintenance and validation.

---

## Table: Design DAX

### Lift Label

```dax
CONCATENATE(FORMAT(SUM(Association[Importance]),"0.0"),"x")
```

**Plain English:** This measure sums up importance values from the Association table and displays the result with one decimal place followed by an "x" (for example, "3.5x").

**Risk Note:** No error handling if Association table is empty or filtered to zero rows—will return "0.0x". Consider whether this is the intended behavior.

---

## Table: Details

### Info Tooltip 2

```dax
"https://imagizer.imageshack.com/img921/2483/uMs9ZQ.gif"
```

1. This measure returns a fixed URL link to an external image file hosted on ImageShack.

2. **Risky:** This is a hardcoded external URL with no error handling. If the image is deleted or the domain goes down, the link breaks silently. Consider storing URLs in a reference table instead.

---
