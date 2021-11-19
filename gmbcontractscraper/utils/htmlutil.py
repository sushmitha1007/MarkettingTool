from urllib.parse import urlparse


def get_home_page(url):
    url = url.strip()  ## spaces at beginning/end cause isssue.
    parsed = urlparse(url)
    return (parsed.scheme + "://" + parsed.netloc)


def is_home_page(url):
    # print("checking homepage")
    parsed = urlparse(url)
    hostname = parsed.hostname
    leaf_node = leaf_node_extractor(url)
    if (leaf_node == hostname):
        return True
    else:
        return False


def leaf_node_extractor(url):
    leaf_list = str(url).split('?')
    leaf_list = str(leaf_list[0]).rsplit('/')
    leaf_list = list(filter(None, leaf_list))
    leaf_node = leaf_list[len(leaf_list) - 1]
    return (leaf_node)
