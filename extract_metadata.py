from pbixray import PBIXRay

# Load the Power BI file
model = PBIXRay("model.pbix")

# List all the tables in the model
print("TABLES IN THIS MODEL:")
print(model.tables)
print()

# dax_measures is a table (a pandas DataFrame) with one row per measure
measures = model.dax_measures
print(f"Found {len(measures)} DAX measures.\n")

# Print each measure's table, name, and DAX expression
for index, row in measures.iterrows():
    print(f"[{row['TableName']}] {row['Name']}")
    print(f"  DAX: {row['Expression']}")
    print()

# Save the relationships too - useful context later
relationships = model.relationships
print("RELATIONSHIPS:")
print(relationships)