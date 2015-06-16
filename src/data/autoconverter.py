# -*- coding: utf-8 -*-
"""
GeoMop model auto-conversion module

Ensures auto-conversion of data for specified format.

@author: Tomas Krizek
"""

from copy import deepcopy

from . import model


def autoconvert(node, its, path ='/'):
    """
    Performs recursive auto-correction on root node.

    Auto-correction:
        1. If Array is expected and scalar/record is found, encapsulate it
           in Array(s).
        2. If Record is expected and scalar/array is found, check
           reducible_to_key. If present, create the Record.
        3. If AbstractRecord is expected and scalar/array is found, check if
           default_descendant fits rule 2.
    """
    root = deepcopy(node)  # references are kept, but duplicated

    # TODO is try-except block needed?
    _autoconvert_crawl(root, its)

    return root


def _autoconvert_crawl(node, its, path):
    """
    Recursively crawls through the tree structure and tries to auto-convert
    values to the expected type.
    """
    if its.input_type == 'AbstractRecord':
        try:
            its_concrete = its.implementations[node['TYPE']]
        except:
            try:
                its_concrete = its.default_descendant
            except:
                return
        _autoconvert_crawl(node, its_concrete, path)
    elif its.input_type == 'Array':
        for child_path, child_node in model.children(node, path):
            autoconverted_node = _autoconvert_node(child_node, its.subtype)
            model.set(node, child_path, autoconverted_node)
            node.value[i] = _get_autoconverted(item, its.subtype)
            _autoconvert_crawl(node.value[i], its.subtype)
    elif its.input_type == 'Record':
        for key, value in node.value.items():
            try:
                child_its = its.keys[key]['type']
            except:
                continue
            else:
                node.value[key] = _get_autoconverted(value, child_its)
                _autoconvert_crawl(node.value[key], child_its)
    return


def _autoconvert_node(node, its):
    """
    Auto-conversion of array and record types.

    Arrays are expanded to the expected dimension.
    Records are initialized from the reducible_to_key value.
    """
    if its.input_type == 'Array' and not isinstance(node.value, list):
        dim = _get_expected_array_dimension(its)
        return _expand_value_to_array(node, dim)
    elif its.input_type.endswith('Record') and not isinstance(node.value, dict):
        return _expand_reducible_to_key(node, its)
    else:
        return node


def _get_expected_array_dimension(its):
    """Returns the expected dimension of the input array."""
    dim = 0
    while its.input_type == 'Array':
        dim = dim + 1
        its = its.subtype
    return dim


def _expand_value_to_array(node, dim):
    """Expands node value to specified dimension."""
    while dim > 0:
        node = [node]
        dim = dim - 1
    return node


def _expand_reducible_to_key(node, its):
    """Initializes a record from the reducible_to_key value."""
    try:
        key = its.default_descendant.reducible_to_key
    except AttributeError:
        key = its.reducible_to_key

    value = {}
    value[key] = node
    return value
