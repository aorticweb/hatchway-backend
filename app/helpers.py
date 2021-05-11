import itertools
from typing import List

import ray
import requests
import requests_cache

from app import config

if not ray.is_initialized():
    ray.init()

requests_cache.install_cache("hatchway_cache", backend="sqlite", expire_after=180)


class Source:
    """
    Wrapper around url calls to data source
    """
    def __init__(self, base: str = config.SOURCE_URL):
        self._session = requests.session()
        self.base = base

    def get_data(self, tag: str):
        """
        Perform url to get posts data
        """
        resp = self._session.get(self.base, params={"tag": tag})
        if resp.status_code == 400:
            # TODO:
            # Log error here
            return {}
        return resp.json()


@ray.remote
def get_post_by_tag(tag: str):
    """
    Ray remote function to get posts data for a tag
    """
    return Source().get_data(tag=tag).get("posts", [])


def param_validation(tags: str, sort_by: str, direction: str):
    """
    Validate tags, sortBy and direction url paramaters passed in request
    """
    if not len(tags):
        return True, "Tags parameter is required"
    if sort_by not in config.VALID_SORTS:
        return True, "sortBy parameter is invalid"
    # For Consistency
    if direction not in ["asc", "desc"]:
        return True, "direction parameter is invalid"
    return False, ""


ListOfListOfDict = List[List[dict]]


def _filter_posts(posts: ListOfListOfDict, sort: str, direction: str):
    """
    Concat lists of lists of posts from multiple api requests into a single list,
    remove duplicate posts from list and sort list according to sort field and direction
    """
    posts = list(itertools.chain.from_iterable(posts))
    # Unique posts
    seen = set()
    unique_posts = []
    for p in posts:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique_posts.append(p)
    # Sort posts
    reverse = direction == "desc"
    posts = sorted(unique_posts, key=lambda x: x.get(sort, ""), reverse=reverse)
    return posts

def _get_posts(tags :str):
    """
    Perform api calls (one per tag) concurently to get posts data
    """
    tags = tags.split(",")
    posts = [get_post_by_tag.remote(t) for t in tags]
    posts = ray.get(posts)
    return posts

def get_posts(tags :str, sort_by :str, direction :str):
    """
    get post and filter posts data
    """
    posts = _get_posts(tags)
    return _filter_posts(posts,  sort_by, direction)