import pytest
from django.conf import settings as django_settings

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

from silver.models import Invoice
from silver.tests.factories import CustomerFactory, ProviderFactory, InvoiceFactory
from silver.utils.client import JSONApiClient


User = get_user_model()

triggered_processor = 'triggered'
manual_processor = 'manual'
failing_void_processor = 'failing_void'

PAYMENT_PROCESSORS = {
    triggered_processor: {
        'class': 'silver.tests.fixtures.TriggeredProcessor'
    },
    manual_processor: {
        'class': 'silver.tests.fixtures.ManualProcessor'
    },
    failing_void_processor: {
        'class': 'silver.tests.fixtures.FailingVoidTriggeredProcessor'
    }
}

PAYMENT_DUE_DAYS = 5
API_PAGE_SIZE = 5


@pytest.fixture(autouse=True, scope='session')
def settings_fixture():
    django_settings.REST_FRAMEWORK['PAGE_SIZE'] = API_PAGE_SIZE
    django_settings.PAYMENT_PROCESSORS = PAYMENT_PROCESSORS
    django_settings.SILVER_DEFAULT_DUE_DAYS = PAYMENT_DUE_DAYS


@pytest.fixture()
def settings():
    return django_settings


@pytest.fixture()
def user(db):
    return User.objects.create(username='user')


@pytest.fixture()
def anonymous_api_client():
    return JSONApiClient()


@pytest.fixture()
def authenticated_api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def authenticated_client(user):
    user.set_password("password")
    user.save()

    client = Client()
    client.login(username=user.username, password="password")

    return client

@pytest.fixture()
def customer(db):
    return CustomerFactory.create()


@pytest.fixture()
def provider(db):
    return ProviderFactory.create()


@pytest.fixture()
def invoice(db):
    return InvoiceFactory.create()


@pytest.fixture()
def issued_invoice(db):
    return InvoiceFactory.create(state=Invoice.STATES.ISSUED)


@pytest.fixture()
def two_pages_of_invoices(db):
    return InvoiceFactory.create_batch(API_PAGE_SIZE * 2)
