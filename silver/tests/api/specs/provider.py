from rest_framework.reverse import reverse

from django.utils.six import text_type

from silver.tests.api.utils.path import absolute_url


def spec_provider_url(provider):
    return absolute_url(reverse("provider-detail", args=[provider.id]))


def spec_archived_provider(provider):
    return {
        'company': text_type(provider.company),
        'email': text_type(provider.email),
        'address_1': text_type(provider.address_1),
        'address_2': text_type(provider.address_2),
        'city': text_type(provider.city),
        'country': text_type(provider.country),
        'state': text_type(provider.state),
        'zip_code': text_type(provider.zip_code),
        'extra': text_type(provider.extra),
        'meta': provider.meta,
        'name': text_type(provider.name),
    }
