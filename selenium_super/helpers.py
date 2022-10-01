def get_args_for_elements_by_selector(selector):
    selector_name = selector.get('selector_name', None)
    base_element = selector.get('base_element', None)
    multiple = selector.get('multiple', None)
    attribute = selector.get('attribute', None)
    filter = selector.get('filter', None)
    xpath = selector.get('xpath', None)
    wait = selector.get('wait', None)
    return [selector_name, base_element, multiple, attribute, filter, xpath, wait]