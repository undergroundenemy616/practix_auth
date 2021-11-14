import hashlib


def get_expected_hash(index, query, page_size, page_number):
    params = f'{query}{page_size}{page_number}'
    hash_string = hashlib.md5(params.encode()).hexdigest()
    return f'elastic_cache::{index}::{hash_string}'
