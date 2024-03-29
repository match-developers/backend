import factory
import factory.fuzzy

from accounts.models import Account


class AccountFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    following = factory.RelatedFactoryList(
        "accounts.tests.factories.AccountFactory",
        factory_related_name="followers",
        size=0,
    )
    is_staff = False
    is_active = True

    class Meta:
        model = Account
        django_get_or_create = (
            "username",
            "email",
            "first_name",
            "last_name",
        )
