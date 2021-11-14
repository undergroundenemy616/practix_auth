INDEX_FILM_NAME = "filmwork"

INDEX_FILM_BODY = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "rating": {
                "type": "float"
            },
            "type": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "genres_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "directors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "writers_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "genres": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "directors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            }
        }
    }
}

TEST_DATA = [
    {"index": {"_index": "filmwork", "_id": "319df05f-c5d9-4389-a84a-a43e695bf000"}},
    {
        "id": "319df05f-c5d9-4389-a84a-a43e695bf000",
        "rating": 6.9,
        "type": "movie",
        "title": "Bright Star",
        "description": "It's 1818 in Hampstead Village on the outskirts of London.",
        "genres_names": [
            "Biography",
            "Drama",
            "Romance"
        ],
        "directors_names": [
            "Jane Campion"
        ],
        "actors_names": [
            "Abbie Cornish",
            "Ben Whishaw",
            "Kerry Fox",
            "Paul Schneider"
        ],
        "writers_names": [
            "Andrew Motion",
            "Jane Campion"
        ],
        "genres": [
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90001",
                "name": "Drama"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90002",
                "name": "Romance"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90003",
                "name": "Biography"
            }
        ],
        "directors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0004",
                "name": "Jane Campion"
            }
        ],
        "actors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0005",
                "name": "Paul Schneider"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0006",
                "name": "Kerry Fox"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0007",
                "name": "Abbie Cornish"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0008",
                "name": "Ben Whishaw"
            }
        ],
        "writers": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0009",
                "name": "Jane Campion"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0010",
                "name": "Andrew Motion"
            }
        ]
    },
    {"index": {"_index": "filmwork", "_id": "319df05f-c5d9-4389-a84a-a43e695bf001"}},
    {
        "id": "319df05f-c5d9-4389-a84a-a43e695bf001",
        "rating": 7.0,
        "type": "movie",
        "title": "Trek V: The Final Frontier",
        "description": None,
        "genres_names": [
            "Sci-Fi"
        ],
        "directors_names": None,
        "actors_names": None,
        "writers_names": [
            "John Doe",
            "Gene Roddenberry",
            "Harve Bennett",
            "William Shatner"
        ],
        "genres": [
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90004",
                "name": "Sci-Fi"
            }
        ],
        "directors": [],
        "actors": [],
        "writers": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0011",
                "name": "David Loughery"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0012",
                "name": "Harve Bennett"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0013",
                "name": "Gene Roddenberry"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0014",
                "name": "William Shatner"
            }
        ]
    },
    {"index": {"_index": "filmwork", "_id": "319df05f-c5d9-4389-a84a-a43e695bf002"}},
    {
        "id": "319df05f-c5d9-4389-a84a-a43e695bf002",
        "rating": 7.5,
        "type": "movie",
        "title": "Enterprise",
        "description": "The year is 2151.",
        "genres_names": [
            "Action",
            "Adventure",
            "Drama",
            "Sci-Fi"
        ],
        "directors_names": None,
        "actors_names": [
            "Dominic Keating",
            "John Billingsley",
            "Jolene Blalock",
            "Scott Bakula"
        ],
        "writers_names": [
            "Brannon Braga",
            "Rick Berman"
        ],
        "genres": [
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90005",
                "name": "Adventure"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90001",
                "name": "Drama"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90006",
                "name": "Action"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90004",
                "name": "Sci-Fi"
            }
        ],
        "directors": [],
        "actors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0015",
                "name": "Scott Bakula"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0016",
                "name": "John Billingsley"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0017",
                "name": "Dominic Keating"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0018",
                "name": "Jolene Blalock"
            }
        ],
        "writers": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0019",
                "name": "Rick Berman"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0020",
                "name": "Brannon Braga"
            }
        ]
    },
    {"index": {"_index": "filmwork", "_id": "319df05f-c5d9-4389-a84a-a43e695bf003"}},
    {
        "id": "319df05f-c5d9-4389-a84a-a43e695bf003",
        "rating": 6.3,
        "type": "movie",
        "title": "Rock Star",
        "description": "Chris Cole was born to rock.",
        "genres_names": [
            "Drama",
            "Music"
        ],
        "directors_names": [
            "Stephen Herek"
        ],
        "actors_names": [
            "Dominic West",
            "Jason Bonham",
            "Jennifer Aniston",
            "Mark Wahlberg"
        ],
        "writers_names": [
            "John Stockwell"
        ],
        "genres": [
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90001",
                "name": "Drama"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90007",
                "name": "Music"
            }
        ],
        "directors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0021",
                "name": "Stephen Herek"
            }
        ],
        "actors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0022",
                "name": "Mark Wahlberg"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0022",
                "name": "Jennifer Aniston"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0023",
                "name": "Jason Bonham"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0024",
                "name": "Dominic West"
            }
        ],
        "writers": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0025",
                "name": "John Stockwell"
            }
        ]
    },
    {"index": {"_index": "filmwork", "_id": "319df05f-c5d9-4389-a84a-a43e695bf004"}},
    {
        "id": "319df05f-c5d9-4389-a84a-a43e695bf004",
        "rating": 6.3,
        "type": "movie",
        "title": "Dark Star",
        "description": "Low-budget story of four astronauts in deep space.",
        "genres_names": [
            "Comedy",
            "Sci-Fi"
        ],
        "directors_names": [
            "John Carpenter"
        ],
        "actors_names": [
            "Brian Narelle",
            "Cal Kuniholm",
            "Dan O'Bannon",
            "Dre Pahich"
        ],
        "writers_names": [
            "Dan O'Bannon",
            "John Carpenter"
        ],
        "genres": [
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90008",
                "name": "Comedy"
            },
            {
                "id": "6c162475-c7ed-4461-9184-001ef3d90004",
                "name": "Sci-Fi"
            }
        ],
        "directors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0026",
                "name": "John Carpenter"
            }
        ],
        "actors": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0027",
                "name": "Dre Pahich"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0028",
                "name": "Cal Kuniholm"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0029",
                "name": "Dan O'Bannon"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0030",
                "name": "Brian Narelle"
            }
        ],
        "writers": [
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0031",
                "name": "John Carpenter"
            },
            {
                "id": "5a8bad1b-586d-4283-a11c-af232bfd0032",
                "name": "Dan O'Bannon"
            }
        ]
    }
]

