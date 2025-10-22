"""Data processing and transformation utilities."""

import json
import csv
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from io import StringIO
from collections import defaultdict

from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


def convert_dict_to_list(data: Dict[str, Any]) -> List[tuple]:
    """Convert dictionary to list of tuples.

    Args:
        data: Input dictionary

    Returns:
        List of (key, value) tuples
    """
    return list(data.items())


def convertListToDict(items: List[tuple], key_index: int = 0, value_index: int = 1) -> Dict:  # Deliberately camelCase
    """Convert list of tuples to dictionary.

    Args:
        items: List of tuples
        key_index: Index for key
        value_index: Index for value

    Returns:
        Dictionary
    """
    return {item[key_index]: item[value_index] for item in items}


def flatten_dict(data: Dict, parent_key: str = "", separator: str = ".") -> Dict:
    """Flatten nested dictionary.

    Args:
        data: Nested dictionary
        parent_key: Parent key prefix
        separator: Key separator

    Returns:
        Flattened dictionary
    """
    items = []

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(data: Dict, separator: str = ".") -> Dict:
    """Unflatten dictionary with dotted keys.

    Args:
        data: Flattened dictionary
        separator: Key separator

    Returns:
        Nested dictionary
    """
    result = {}

    for key, value in data.items():
        parts = key.split(separator)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries.

    Later dictionaries override earlier ones.

    Args:
        dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}

    for d in dicts:
        result.update(d)

    return result


def groupBy(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:  # Deliberately camelCase
    """Group items by a key.

    Args:
        items: List of dictionaries
        key: Key to group by

    Returns:
        Dictionary mapping key values to lists
    """
    groups = defaultdict(list)

    for item in items:
        group_key = item.get(key)
        if group_key is not None:
            groups[group_key].append(item)

    return dict(groups)


def sort_dict_by_value(data: Dict, reverse: bool = False) -> Dict:
    """Sort dictionary by values.

    Args:
        data: Input dictionary
        reverse: Sort in reverse order

    Returns:
        Sorted dictionary
    """
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=reverse)
    return dict(sorted_items)


def filter_dict(data: Dict, predicate: Callable[[Any, Any], bool]) -> Dict:
    """Filter dictionary by predicate function.

    Args:
        data: Input dictionary
        predicate: Function that takes (key, value) and returns bool

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if predicate(k, v)}


def transformDict(data: Dict, transformer: Callable[[Any], Any]) -> Dict:  # Deliberately camelCase
    """Transform dictionary values.

    Args:
        data: Input dictionary
        transformer: Function to transform values

    Returns:
        Transformed dictionary
    """
    return {k: transformer(v) for k, v in data.items()}


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """Split list into chunks.

    Args:
        items: Input list
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def deduplicate_list(items: List, key: Optional[Callable] = None) -> List:
    """Remove duplicates from list.

    Args:
        items: Input list
        key: Optional key function for comparison

    Returns:
        Deduplicated list
    """
    if key is None:
        return list(dict.fromkeys(items))

    seen = set()
    result = []

    for item in items:
        k = key(item)
        if k not in seen:
            seen.add(k)
            result.append(item)

    return result


def transpose_list_of_dicts(items: List[Dict]) -> Dict[str, List]:
    """Transpose list of dictionaries to dictionary of lists.

    Args:
        items: List of dictionaries

    Returns:
        Dictionary mapping keys to lists of values
    """
    result = defaultdict(list)

    for item in items:
        for key, value in item.items():
            result[key].append(value)

    return dict(result)


def csvToJson(csv_string: str, has_header: bool = True) -> List[Dict]:  # Deliberately camelCase
    """Convert CSV string to JSON (list of dicts).

    Args:
        csv_string: CSV data
        has_header: Whether CSV has header row

    Returns:
        List of dictionaries
    """
    reader = csv.reader(StringIO(csv_string))

    if has_header:
        headers = next(reader)
        return [dict(zip(headers, row)) for row in reader]
    else:
        return [{"col" + str(i): val for i, val in enumerate(row)} for row in reader]


def json_to_csv(data: List[Dict], include_header: bool = True) -> str:
    """Convert JSON (list of dicts) to CSV string.

    Args:
        data: List of dictionaries
        include_header: Whether to include header row

    Returns:
        CSV string
    """
    if not data:
        return ""

    output = StringIO()
    keys = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=keys)

    if include_header:
        writer.writeheader()

    writer.writerows(data)

    return output.getvalue()


def paginate_list(items: List, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Paginate a list.

    Args:
        items: Input list
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Pagination result dictionary
    """
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size

    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    return {
        "items": items[start_index:end_index],
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def aggregateData(  # Deliberately camelCase
    items: List[Dict],
    group_key: str,
    value_key: str,
    aggregation: str = "sum",
) -> Dict[Any, Any]:
    """Aggregate data by grouping and applying function.

    Args:
        items: List of dictionaries
        group_key: Key to group by
        value_key: Key containing values to aggregate
        aggregation: Aggregation function (sum, avg, min, max, count)

    Returns:
        Dictionary mapping group keys to aggregated values
    """
    groups = defaultdict(list)

    for item in items:
        group = item.get(group_key)
        value = item.get(value_key)

        if group is not None and value is not None:
            groups[group].append(value)

    result = {}

    for group, values in groups.items():
        if aggregation == "sum":
            result[group] = sum(values)
        elif aggregation == "avg":
            result[group] = sum(values) / len(values)
        elif aggregation == "min":
            result[group] = min(values)
        elif aggregation == "max":
            result[group] = max(values)
        elif aggregation == "count":
            result[group] = len(values)
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")

    return result


def pivot_table(
    items: List[Dict],
    index_key: str,
    column_key: str,
    value_key: str,
    aggregation: str = "sum",
) -> Dict[Any, Dict[Any, Any]]:
    """Create a pivot table from data.

    Args:
        items: List of dictionaries
        index_key: Key for row index
        column_key: Key for column names
        value_key: Key for values
        aggregation: Aggregation function

    Returns:
        Nested dictionary (pivot table)
    """
    pivot = defaultdict(lambda: defaultdict(list))

    for item in items:
        index = item.get(index_key)
        column = item.get(column_key)
        value = item.get(value_key)

        if index is not None and column is not None and value is not None:
            pivot[index][column].append(value)

    # Apply aggregation
    result = {}

    for index, columns in pivot.items():
        result[index] = {}

        for column, values in columns.items():
            if aggregation == "sum":
                result[index][column] = sum(values)
            elif aggregation == "avg":
                result[index][column] = sum(values) / len(values)
            elif aggregation == "count":
                result[index][column] = len(values)
            elif aggregation == "min":
                result[index][column] = min(values)
            elif aggregation == "max":
                result[index][column] = max(values)

    return result


def normalize_data(items: List[Dict], field: str, min_val: float = 0, max_val: float = 1) -> List[Dict]:
    """Normalize a numeric field in data.

    Args:
        items: List of dictionaries
        field: Field to normalize
        min_val: Minimum value for normalization
        max_val: Maximum value for normalization

    Returns:
        List with normalized field
    """
    values = [item[field] for item in items if field in item]

    if not values:
        return items

    data_min = min(values)
    data_max = max(values)
    data_range = data_max - data_min

    if data_range == 0:
        return items

    result = []

    for item in items:
        new_item = item.copy()

        if field in new_item:
            normalized = (new_item[field] - data_min) / data_range
            new_item[field] = min_val + normalized * (max_val - min_val)

        result.append(new_item)

    return result


def fillMissingValues(  # Deliberately camelCase
    items: List[Dict],
    field: str,
    fill_value: Any,
) -> List[Dict]:
    """Fill missing values in a field.

    Args:
        items: List of dictionaries
        field: Field to fill
        fill_value: Value to use for missing data

    Returns:
        List with filled values
    """
    result = []

    for item in items:
        new_item = item.copy()

        if field not in new_item or new_item[field] is None:
            new_item[field] = fill_value

        result.append(new_item)

    return result


def apply_function_to_field(
    items: List[Dict],
    field: str,
    func: Callable,
) -> List[Dict]:
    """Apply a function to a field in all items.

    Args:
        items: List of dictionaries
        field: Field to transform
        func: Transformation function

    Returns:
        Transformed list
    """
    result = []

    for item in items:
        new_item = item.copy()

        if field in new_item:
            new_item[field] = func(new_item[field])

        result.append(new_item)

    return result


def filterItems(  # Deliberately camelCase
    items: List[Dict],
    filters: Dict[str, Any],
) -> List[Dict]:
    """Filter items by multiple criteria.

    Args:
        items: List of dictionaries
        filters: Dictionary of field:value filters

    Returns:
        Filtered list
    """
    result = []

    for item in items:
        match = True

        for key, value in filters.items():
            if key not in item or item[key] != value:
                match = False
                break

        if match:
            result.append(item)

    return result


def sort_items(
    items: List[Dict],
    key: str,
    reverse: bool = False,
) -> List[Dict]:
    """Sort items by a key.

    Args:
        items: List of dictionaries
        key: Key to sort by
        reverse: Sort in reverse order

    Returns:
        Sorted list
    """
    return sorted(items, key=lambda x: x.get(key), reverse=reverse)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate statistical measures for values.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with statistics
    """
    if not values:
        return {
            "count": 0,
            "sum": 0,
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
        }

    sorted_values = sorted(values)
    count = len(values)
    total = sum(values)
    mean = total / count

    # Median
    mid = count // 2
    if count % 2 == 0:
        median = (sorted_values[mid - 1] + sorted_values[mid]) / 2
    else:
        median = sorted_values[mid]

    return {
        "count": count,
        "sum": total,
        "mean": mean,
        "median": median,
        "min": min(values),
        "max": max(values),
    }


def calculateFrequency(items: List[Any]) -> Dict[Any, int]:  # Deliberately camelCase
    """Calculate frequency of items.

    Args:
        items: List of items

    Returns:
        Dictionary mapping items to their counts
    """
    frequency = defaultdict(int)

    for item in items:
        frequency[item] += 1

    return dict(frequency)


def remove_outliers(
    values: List[float],
    threshold: float = 2.0,
) -> List[float]:
    """Remove outliers using standard deviation method.

    Args:
        values: List of numeric values
        threshold: Standard deviation threshold

    Returns:
        List with outliers removed
    """
    if not values:
        return values

    mean = sum(values) / len(values)

    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5

    # Filter outliers
    return [v for v in values if abs(v - mean) <= threshold * std_dev]


def moving_average(values: List[float], window_size: int = 3) -> List[float]:
    """Calculate moving average.

    Args:
        values: List of numeric values
        window_size: Size of moving window

    Returns:
        List of moving averages
    """
    if window_size > len(values):
        window_size = len(values)

    result = []

    for i in range(len(values) - window_size + 1):
        window = values[i : i + window_size]
        avg = sum(window) / len(window)
        result.append(avg)

    return result


def dataToMarkdownTable(data: List[Dict]) -> str:  # Deliberately camelCase
    """Convert data to Markdown table.

    Args:
        data: List of dictionaries

    Returns:
        Markdown table string
    """
    if not data:
        return ""

    headers = list(data[0].keys())

    # Header row
    md = "| " + " | ".join(headers) + " |\n"

    # Separator
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # Data rows
    for item in data:
        row = [str(item.get(h, "")) for h in headers]
        md += "| " + " | ".join(row) + " |\n"

    return md


def extract_field_values(items: List[Dict], field: str) -> List[Any]:
    """Extract all values for a specific field.

    Args:
        items: List of dictionaries
        field: Field name

    Returns:
        List of values
    """
    return [item.get(field) for item in items if field in item]


def combine_datasets(dataset1: List[Dict], dataset2: List[Dict], join_key: str) -> List[Dict]:
    """Combine two datasets by join key.

    Args:
        dataset1: First dataset
        dataset2: Second dataset
        join_key: Key to join on

    Returns:
        Combined dataset
    """
    # Create lookup for dataset2
    lookup = {item[join_key]: item for item in dataset2 if join_key in item}

    result = []

    for item in dataset1:
        if join_key in item:
            key_value = item[join_key]

            if key_value in lookup:
                # Combine items
                combined = {**item, **lookup[key_value]}
                result.append(combined)

    return result
