"""CSV utilities"""
import csv
import io


def escape_csv_field(field):
    """
    Escape CSV field (handle quotes and commas)
    
    Args:
        field: Field value to escape
    
    Returns:
        Escaped field string
    """
    if field is None:
        return ""
    
    str_field = str(field)
    # If field contains comma, quote, or newline, wrap in quotes and escape quotes
    if "," in str_field or '"' in str_field or "\n" in str_field:
        return f'"{str_field.replace('"', '""')}"'
    return str_field


def array_to_csv(data, headers):
    """
    Convert array of objects to CSV
    
    Args:
        data: List of dictionaries
        headers: List of header names
    
    Returns:
        CSV string
    """
    if not data:
        return ",".join(headers)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(headers)
    
    # Write data rows
    for row in data:
        values = [escape_csv_field(row.get(header, "")) for header in headers]
        writer.writerow(values)
    
    return output.getvalue()

