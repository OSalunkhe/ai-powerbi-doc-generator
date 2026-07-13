from pbixray import PBIXRay

def get_schema_context(pbix_path="model.pbix"):
    model = PBIXRay(pbix_path)
    schema = model.schema  # columns: TableName, ColumnName, PandasDataType

    lines = []
    for table_name in schema["TableName"].unique():
        safe_name = table_name.replace(" ", "_")
        cols = schema[schema["TableName"] == table_name]
        col_list = ", ".join(
            f"{row['ColumnName']} ({row['PandasDataType']})"
            for _, row in cols.iterrows()
        )
        lines.append(f"Table: {safe_name}\n  Columns: {col_list}")

    relationships = model.relationships
    if len(relationships) > 0:
        lines.append("\nRelationships (for JOINs):")
        for _, row in relationships.iterrows():
            from_t = row["FromTableName"].replace(" ", "_")
            to_t = row["ToTableName"].replace(" ", "_")
            lines.append(f"  {from_t}.{row['FromColumnName']} -> {to_t}.{row['ToColumnName']}")

    return "\n".join(lines)

if __name__ == "__main__":
    # Run this file directly to sanity-check what Claude will see
    print(get_schema_context())