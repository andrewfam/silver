from datetime import date

from decimal import Decimal


unaltered = lambda input_value: input_value
# required is True by default, (a default must be specified otherwise)
# read_only is False by default,
# write_only is False by default,
document_entry_definition = {
    'id': {
        'read_only': True,
        'output': lambda entry: int(entry.id),
    },
    'description': {
        'expected_input_types': str,
        'output': unaltered,
        'required': False,
        'default': None
    },
    'unit': {
        'expected_input_types': str,
        'output': unaltered,
        'required': False,
        'default': None
    },
    'unit_price':  {
        'expected_input_types': (int, float, str, Decimal),
        'output': lambda input_value: "%.4f" % Decimal(input_value)
    },
    'quantity': {
        'expected_input_types': (int, float, str, Decimal),
        'output': lambda input_value: "%.4f" % Decimal(input_value)
    },
    'total_before_tax': {
        'read_only': True,
        'output': lambda entry: "%.2f" % (entry.unit_price * entry.quantity)
    },
    'total': {
        'read_only': True,
        'output': lambda entry: "%.2f" % (
            entry.total_before_tax * Decimal(1 + entry.document.sales_tax_percent / 100)
        )
    },
    'start_date': {
        'expected_input_types': date,
        'output': unaltered,
        'required': False,
        'default': None
    },
    'end_date': {
        'expected_input_types': date,
        'output': unaltered,
        'required': False,
        'default': None
    },
    'prorated': {
        'expected_input_types': bool,
        'output': unaltered,
        'required': False,
        'default': False
    },
    'product_code': {
        'expected_input_types': str,
        'output': unaltered,
        'required': False,
        'default': None
    }
}


field_defaults = {
    field: spec['default'] for field, spec in document_entry_definition.items() if 'default' in spec
}


def spec_document_entry(entry):
    """
    Returns JSON response based on DocumentEntry object
    """
    representation = {}
    for field, field_spec in document_entry_definition.items():
        output = field_spec['output']

        if field_spec.get('read_only'):
            representation[field] = output(entry)
        else:
            representation[field] = output(getattr(entry, field))
    return representation


def check_document_entry_response(request_data, entry, response_data):
    # check input field types are according to spec
    for field, value in request_data.items():
        assert isinstance(value, document_entry_definition[field]['expected_input_types'])

    # check overall output from DB object is according to spec
    assert response_data == spec_document_entry(entry)

    # check output defaults are according to spec
    for field, default in field_defaults.items():
        if field not in request_data:
            assert response_data[field] == default

    # check input values are outputted according to spec
    for field in request_data:
        field_definition = document_entry_definition[field]
        assert response_data[field] == field_definition['output'](request_data[field])
