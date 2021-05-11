import random
import uuid
from datetime import datetime

from app import config, helpers

def test_cache():
    """
    Asserts api call to data source works and
    request caching improves subsequent url calls speed
    """
    test_tag = "tech"
    t0 = datetime.now()
    helpers.Source().get_data(tag=test_tag)
    dur1 = datetime.now() - t0
    t0 = datetime.now()
    helpers.Source().get_data(tag=test_tag)
    dur2 = datetime.now() - t0
    assert dur2 < dur1


def test_param_validation():
    """
    Test /api/posts parameter validation
    """
    has_error, error = helpers.param_validation(
        "", config.DEFAULT_SORT, config.DEFAULT_DIRECTION
    )
    assert has_error
    assert "tag" in error.lower()
    has_error, error = helpers.param_validation(
        "tech", "BAD SORT FIELD", config.DEFAULT_DIRECTION
    )
    assert has_error
    assert "sort" in error.lower()
    has_error, error = helpers.param_validation(
        "tech", config.DEFAULT_SORT, config.DEFAULT_DIRECTION
    )
    assert not has_error


def fake_posts(num_posts=100):
    """
    Fake Post Data for test_filter_posts
    """

    def post():
        return {
            "id": random.randint(1, int(num_posts * 1.10)),
            "reads": random.randint(0, 35),
            "uuid": uuid.uuid4(),  # for debug
        }

    posts = [post() for i in range(0, num_posts)]
    return posts


def test_filter_posts():
    """
    Test sorting and duplicate removal of posts returned by api calls
    """
    test_data = [fake_posts() for _ in range(0, 5)]
    num_posts = len(test_data[0])
    filtered = helpers._filter_posts(test_data, "reads", "desc")
    # Duplicates are removed
    assert len(filtered) <= int(num_posts * 1.10)
    ordered = True
    for i in range(1, len(filtered)):
        if filtered[i - 1]["reads"] < filtered[i]["reads"]:
            ordered = False
            break
    # Properly sorted
    assert ordered
