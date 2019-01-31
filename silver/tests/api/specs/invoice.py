from datetime import date, timedelta
from decimal import Decimal
from pprint import pprint

from silver.tests.api.specs.customer import spec_customer_url, spec_archived_customer
from silver.tests.api.specs.document_entry import spec_document_entry
from silver.tests.api.specs.provider import spec_provider_url, spec_archived_provider
from silver.tests.api.specs.transaction import spec_transaction


unaltered = lambda input_value: input_value
# required is True by default, (a default must be specified otherwise)
# read_only is False by default,
# write_only is False by default,
invoice_definition = {
    'id': {
        'read_only': True,
        'output': lambda invoice: int(invoice.id),
    },
    'archived_provider': {
        'read_only': True,
        'output': lambda invoice: spec_archived_provider(invoice.customer),
    },
    'archived_customer': {
        'read_only': True,
        'output': lambda invoice: spec_archived_customer(invoice.customer),
    },
    'customer':  {
        'expected_input_types': str,
        'output': unaltered,
        'assertions': [
            lambda input, invoice, output: input == output == spec_customer_url(invoice.customer)
        ]
    },
    'provider': {
        'expected_input_types': str,
        'output': unaltered,
        'assertions': [
            lambda input, invoice, output: input == output == spec_provider_url(invoice.provider)
        ]
    },
    'series': {
        'required': False,
        'expected_input_types': str,
        'output': unaltered,
        'default': lambda invoice: invoice.provider.invoice_series
    },
    'number': {
        'required': False,
        'expected_input_types': int,
        'output': unaltered,
        'default': lambda invoice: invoice.provider.invoice_number
    },
    'currency': {
        'expected_input_types': str,
        'output': unaltered,
    },
    'transaction_currency': {
        'required': False,
        'expected_input_types': str,
        'output': unaltered,
        'default': lambda invoice: invoice.currency
    },
    'transaction_xe_date': {
        'required': False,
        'expected_input_types': date,
        'output': unaltered,
        'default': lambda invoice:
            None if invoice.state == 'draft'
            else invoice.issue_date - timedelta(days=1)
    },
    'transaction_xe_rate': {
        'required': False,
        'expected_input_types': (int, float, str, Decimal),
        'output': lambda input_value: "%.4f" % Decimal(input_value),
        'default': lambda invoice:
            None if invoice.state == 'draft'
            else str(invoice.transaction_xe_rate)  # based on transaction_xe_date
    },
    'state': {
        'read_only': True,
        'output': lambda invoice: str(invoice.state),
        'assertions': [
            lambda output, **kw: output in ['draft', 'issued', 'canceled', 'paid']
        ]
    },
    'total': {
        'read_only': True,
        'output': lambda invoice: "%.2f" % (
            sum([entry.total for entry in invoice.entries])
        )
    },
    'total_in_transaction_currency': {
        'read_only': True,
        'output': lambda invoice:
            None if invoice.state == 'draft'
            else "%.2f" % (
                sum([entry.total_in_transaction_currency for entry in invoice.entries])
            )
    },
    'issue_date': {
        'required': False,
        'expected_input_types': date,
        'output': unaltered,
        'default': lambda invoice:
            None if invoice.state == 'draft'
            else invoice.issue_date
    },
    'paid_date': {
        'required': False,
        'expected_input_types': date,
        'output': unaltered,
        'default': lambda invoice:
            None if invoice.state != 'paid'
            else invoice.paid_date
    },
    'cancel_date': {
        'required': False,
        'expected_input_types': date,
        'output': unaltered,
        'default': lambda invoice:
            None if invoice.state != 'canceled'
            else invoice.cancel_date
    },
    'sales_tax_percent': {
        'expected_input_types': (int, float, str, Decimal),
        'output': lambda input_value: "%.2f" % Decimal(input_value),
        'required': False,
        'default': None
    },
    'sales_tax_name': {
        'expected_input_types': str,
        'output': unaltered,
        'required': False,
        'default': 'VAT'
    },
    'transactions': {
        'read_only': True,
        'output': lambda invoice: [
            spec_transaction(t) for t in invoice.transactions
        ]
    },
    'invoice_entries': {
        'read_only': True,
        'output': lambda invoice: [
            spec_document_entry(entry) for entry in invoice.entries
        ]
    },
    'pdf_url': {
        'read_only': True,
        'output': lambda invoice: invoice.pdf.url if invoice.pdf else None,
    }
}


field_defaults = {
    field: spec['default'] for field, spec in invoice_definition.items() if 'default' in spec
}


def spec_invoice(invoice):
    """
    Returns JSON response based on Invoice object
    """
    representation = {}
    for field, field_spec in invoice_definition.items():
        field_output = field_spec['output']
        if 'read_only' in field_spec:
            representation[field] = field_output(invoice)
        else:
            representation[field] = field_output(getattr(invoice, field))
    return representation


def check_invoice_response(invoice, response_data, request_data=None):
    if request_data:
        # check input field types are according to spec
        for field, value in request_data.items():
            assert isinstance(value, invoice_definition[field]['expected_input_types'])

        # check output defaults are according to spec
        for field, default in field_defaults.items():
            if callable(default):
                default = default(invoice)

            if field not in request_data:
                assert response_data[field] == default

        # check input values are outputted according to spec
        for field in request_data:
            field_definition = invoice_definition[field]
            assert response_data[field] == field_definition['output'](request_data[field])

    # check overall output from DB object is according to spec
    print(response_data)
    print(spec_invoice(invoice))
    assert response_data == spec_invoice(invoice)
