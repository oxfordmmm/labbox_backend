import math
from typing import Any, Dict, List


def is_none_or_nan(value):
    return value is None or (isinstance(value, float) and math.isnan(value))


# use this instead of pandas merge, as pandas is a heavy dependency
def merge_lists(
    list1: List[Dict[str, Any]], list2: List[Dict[str, Any]], key1: str, key2: str
) -> List[Dict[str, Any]]:
    # Create a mapping dictionary for quick lookup from list2
    mapping_dict = {item[key2]: item for item in list2 if key2 in item}

    # Merge the two lists
    merged_list = []
    for item1 in list1:
        key_value = item1.get(key1)
        if key_value in mapping_dict:
            merged_item = {**item1, **mapping_dict[key_value]}
            merged_list.append(merged_item)

    return merged_list
