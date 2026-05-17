"""
Utility module containing common functions for data transformation, 
serialization, and hashing.
"""

def deep_make_hashable(obj):
    """Recursively converts unhashable dictionaries and lists into frozensets 
    and tuples.

    Args:
        obj (Any): The object to be made hashable.

    Returns:
        Any: A hashable version of the input object (frozenset for dicts, 
            tuple for lists).
    """
    if isinstance(obj, dict):
        return frozenset((k, deep_make_hashable(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return tuple(deep_make_hashable(i) for i in obj)
    return obj

def deep_make_dict(obj):
    """Recursively converts frozensets and tuples back into dictionaries and lists.

    Args:
        obj (Any): The hashable object to convert back to standard collections.

    Returns:
        Any: The reconstructed dictionary or list structure.
    """
    if isinstance(obj, frozenset):
        return {k: deep_make_dict(v) for k, v in obj}
    if isinstance(obj, tuple):
        # Distinguish between actual tuples and converted lists if necessary; 
        # for configs, converting all to lists is generally safe.
        return [deep_make_dict(i) for i in obj]
    return obj