"""
Utility functions for universality metrics validation and computation.

This module provides reusable functions for:
- Extracting field names and metadata from configuration
- Checking field completeness
- Validating fields against their definitions
- Computing completeness and validity metrics
"""

from typing import Dict, List, Optional, Union


def extract_field_names(fields: List[Union[str, Dict]]) -> List[str]:
    """
    Extract field names from config. Supports both old format (list of strings) 
    and new format (list of objects with 'name' key).
    
    Parameters
    ----------
    fields : list
        List of either strings (old format) or dicts with 'name' key (new format)
        
    Returns
    -------
    list
        List of field names
    """
    field_names = []
    for field in fields:
        if isinstance(field, str):
            # Old format: just a string
            field_names.append(field)
        elif isinstance(field, dict) and 'name' in field:
            # New format: dict with 'name' key
            field_names.append(field['name'])
    return field_names


def extract_field_metadata(fields: List[Union[str, Dict]]) -> Dict[str, Dict]:
    """
    Extract field metadata from config. Returns empty dict for old format.
    
    Parameters
    ----------
    fields : list
        List of either strings (old format) or dicts (new format)
        
    Returns
    -------
    dict
        Dictionary mapping field names to their metadata
    """
    metadata = {}
    for field in fields:
        if isinstance(field, dict) and 'name' in field:
            field_name = field['name']
            metadata[field_name] = {
                'data_type': field.get('data_type'),
                'min': field.get('min'),
                'max': field.get('max'),
                'possible_values': field.get('possible_values'),
                'required': field.get('required', True),
                'description': field.get('description', ''),
                'item_type': field.get('item_type'),
                'min_items': field.get('min_items')
            }
    return metadata


def check_completeness(
    field_value: Union[str, int, float, List[str], Dict, None]
) -> bool:
    """
    Check if a field is present (completeness check).
    
    Parameters
    ----------
    field_value : Union[str, int, float, List[str], Dict, None]
        The value to check
        
    Returns
    -------
    bool
        True if the field is present (not None), False otherwise
    """
    return field_value is not None


def check_validity(
    field_name: str,
    field_value: Union[str, int, float, List[str], Dict, None],
    metadata: Optional[Dict] = None
) -> bool:
    """
    Validate a field value based on its metadata definition.
    
    Parameters
    ----------
    field_name : str
        Name of the field being validated
    field_value : Union[str, int, float, List[str], Dict, None]
        The value to validate
    metadata : dict, optional
        Field metadata from config. If None, falls back to basic validation.
        
    Returns
    -------
    bool
        True if the field is valid according to its definition, False otherwise
    """
    if field_value is None:
        return False
    
    # If metadata is available, use it for validation
    if metadata:
        data_type = metadata.get('data_type')
        
        # Check data type
        if data_type == 'string':
            if not isinstance(field_value, str):
                return False
            # Check if non-empty after strip
            if len(field_value.strip()) == 0:
                return False
            # Check possible values if specified
            possible_values = metadata.get('possible_values')
            if possible_values:
                return field_value.lower() in [v.lower() for v in possible_values]
            return True
        
        elif data_type == 'number':
            if not isinstance(field_value, (int, float)):
                return False
            # Check min constraint (value must be > min, not >=)
            min_val = metadata.get('min')
            if min_val is not None:
                if field_value <= min_val:
                    return False
            # Check max constraint (value must be < max, not <=)
            max_val = metadata.get('max')
            if max_val is not None:
                if field_value >= max_val:
                    return False
            return True
        
        elif data_type == 'list':
            if not isinstance(field_value, (list, tuple)):
                return False
            # Check min_items constraint
            min_items = metadata.get('min_items')
            if min_items is not None and len(field_value) < min_items:
                return False
            # Check item_type if specified
            item_type = metadata.get('item_type')
            if item_type == 'string':
                return all(
                    isinstance(item, str) and len(item.strip()) > 0 
                    for item in field_value
                )
            return len(field_value) > 0
        
        elif data_type == 'string_or_list':
            # Can be either string or list
            if isinstance(field_value, str):
                return len(field_value.strip()) > 0
            elif isinstance(field_value, (list, tuple)):
                min_items = metadata.get('min_items')
                if min_items is not None and len(field_value) < min_items:
                    return False
                item_type = metadata.get('item_type')
                if item_type == 'string':
                    return all(
                        isinstance(item, str) and len(item.strip()) > 0 
                        for item in field_value
                    )
                return len(field_value) > 0
            return False
        
        elif data_type == 'dict_or_list':
            # Can be either dict or list
            if isinstance(field_value, dict):
                return len(field_value) > 0
            elif isinstance(field_value, (list, tuple)):
                return len(field_value) > 0
            return False
        
        elif data_type == 'dict':
            if not isinstance(field_value, dict):
                return False
            return len(field_value) > 0
    
    # Fallback to basic validation if no metadata
    # This maintains backward compatibility
    if isinstance(field_value, str):
        return len(field_value.strip()) > 0
    if isinstance(field_value, (list, tuple)):
        return len(field_value) > 0
    if isinstance(field_value, dict):
        return len(field_value) > 0
    return True


def compute_metrics(
    field_names: List[str],
    metadata: Dict[str, Dict],
    input_data: Dict[str, Union[str, int, float, List[str], Dict, None]]
) -> Dict[str, Union[float, Dict[str, bool], List[str]]]:
    """
    Generic function to compute completeness and validity metrics for a set of fields.
    
    Parameters
    ----------
    field_names : list
        List of field names to check
    metadata : dict
        Dictionary mapping field names to their metadata definitions
    input_data : dict
        Dictionary containing the input data to validate
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'completeness_score' (float): Score for field presence (0.0 to 1.0)
        - 'validity_score' (float): Score for field validity according to definitions (0.0 to 1.0)
        - 'completeness_details' (dict): Boolean flags for each field's presence
        - 'validity_details' (dict): Boolean flags for each field's validity
        - 'missing' (list): List of missing field names
        - 'invalid' (list): List of invalid field names
    """
    completeness_details = {}
    validity_details = {}
    missing = []
    invalid = []
    
    for field_name in field_names:
        field_value = input_data.get(field_name)
        field_metadata = metadata.get(field_name)
        
        # Check completeness (field present)
        is_complete = check_completeness(field_value)
        completeness_details[field_name] = is_complete
        if not is_complete:
            missing.append(field_name)
        
        # Check validity (field meets definition)
        is_valid = check_validity(field_name, field_value, field_metadata)
        validity_details[field_name] = is_valid
        if not is_valid:
            invalid.append(field_name)
    
    # Calculate scores
    completeness_score = (
        sum(completeness_details.values()) / len(field_names) 
        if field_names else 0.0
    )
    validity_score = (
        sum(validity_details.values()) / len(field_names) 
        if field_names else 0.0
    )
    
    return {
        'completeness_score': completeness_score,
        'validity_score': validity_score,
        'completeness_details': completeness_details,
        'validity_details': validity_details,
        'missing': missing,
        'invalid': invalid
    }

