import factory
import factory.fuzzy

from accounts.models import Account


class AccountFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_staff = False
    is_active = True

    class Meta:
        model = Account
