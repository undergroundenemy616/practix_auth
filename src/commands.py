import click
from accounts import accounts
from pprint import pprint
from utils import register_user


@accounts.cli.command("createsuperuser")
@click.argument("login")
@click.argument("password")
def create_user(login, password):
    result = register_user(login, password, superuser=True)
    pprint(result[0])