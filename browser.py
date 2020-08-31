import sys
import os
from collections import deque
import requests
from bs4 import BeautifulSoup
import colorama
colorama.init()


# bloomberg = '''
# The Space Race: From Apollo 11 to Elon Musk
#
# It's 50 years since the world was gripped by historic images
#  of Apollo 11, and Neil Armstrong -- the first man to walk
#  on the moon. It was the height of the Cold War, and the charts
#  were filled with David Bowie's Space Oddity, and Creedence's
#  Bad Moon Rising. The world is a very different place than
#  it was 5 decades ago. But how has the space race changed since
#  the summer of '69? (Source: Bloomberg)
#
#
# Twitter CEO Jack Dorsey Gives Talk at Apple Headquarters
#
# Twitter and Square Chief Executive Officer Jack Dorsey
#  addressed Apple Inc. employees at the iPhone maker’s headquarters
#  Tuesday, a signal of the strong ties between the Silicon Valley giants.
# '''
#
# nytimes = '''
# This New Liquid Is Magnetic, and Mesmerizing
#
# Scientists have created “soft” magnets that can flow
# and change shape, and that could be a boon to medicine
# and robotics. (Source: New York Times)
#
#
# Most Wikipedia Profiles Are of Men. This Scientist Is Changing That.
#
# Jessica Wade has added nearly 700 Wikipedia biographies for
#  important female and minority scientists in less than two
#  years.
#
# '''
#
# CONTENT = {
#     'bloomberg': bloomberg,
#     'nytimes': nytimes
# }


def create_folder(name):
    """
    Creates a folder in the current directory (unless it already exists).
    """
    try:
        os.mkdir(name)
        print(f'Folder {name} created')
    except FileExistsError:
        print(f'Folder {name} already exists')


def is_command(text, command_list):
    """
    Checks if the user input is on a list of valid commands.
    """
    return text in command_list


def is_valid_url(url):
    """
    Checks to see if the url contains at least one dot '.'
    """
    return '.' in url


def add_protocol_to_url(url):
    """
    If the URL is valid (as per function is_valid_url), adds HTTPS prefix to
    the beginning if necessary.
    """
    if is_valid_url(url) and not url.startswith("http"):
        return f'https://{url}'
    else:
        return url


def remove_prefix_from_url(url):
    """Removes http:// or https:// and/or www. prefix from url if necessary."""
    clean_url = url
    if url.startswith("http://"):
        clean_url = url[7:]
    elif url.startswith("https://"):
        clean_url = url[8:]

    if clean_url.startswith("www."):
        return clean_url[4:]
    else:
        return clean_url


def get_page_name_from_url(url):
    """
    Removes the last '.' and everything that follows from the end of a url.
    Also removes the http(s) prefix as per remove_protocol_from_url.
    """
    url_ = remove_prefix_from_url(url)
    if '.' in url_:
        url_pieces = url_.split('.')
        del url_pieces[len(url_pieces) - 1]
        return '.'.join(url_pieces)
    else:
        return url_


def mark_links_blue(plain_soup):
    """Takes a BeautifulSoup object and colors links blue."""
    html_tag = plain_soup.html
    for child in html_tag.descendants:
        if child.name == u'a':
            child.string = colorama.Fore.BLUE + str(child.string) + colorama.Fore.WHITE

    return plain_soup


def remove_script(plain_soup):
    """Removes <script> tags from a BeautifulSoup object."""



if __name__ == "__main__":
    # constants
    COMMAND_LIST = ['exit', 'back']

    # get command line arguments
    args = sys.argv
    tab_folder_name = args[1]

    # create folder for saved tabs and stack for browsing history
    create_folder(tab_folder_name)
    history = deque()
    page_name = ''

    # browse
    while True:
        URL = input()
        URL = add_protocol_to_url(URL)

        if is_command(URL, COMMAND_LIST):
            if URL == 'exit':
                break
            elif URL == 'back' and history:
                with open(f'{tab_folder_name}/{history.pop()}', 'r', encoding='utf-8') as f:
                    print(f.read())

        else:
            # handle invalid URLs and re-reading pages (nytimes.com -> nytimes)
            page_exists = os.path.exists(f'{tab_folder_name}/{URL}')
            if not is_valid_url(URL) and not page_exists:
                print(f'Error: {URL} is not a valid URL.')
                continue

            # add previous page to history stack
            if page_name:
                history.append(page_name)
            page_name = get_page_name_from_url(URL)

            # save web page to a file in the saved tabs folder and print content
            if page_exists:
                with open(f'{tab_folder_name}/{page_name}', 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                with open(f'{tab_folder_name}/{page_name}', 'w+', encoding='utf-8') as f:
                    r = requests.get(URL)
                    soup = BeautifulSoup(r.content, 'html.parser')
                    soup = mark_links_blue(soup)
                    page_text = soup.get_text('\n', strip=True)
                    f.write(page_text)
                    print(page_text)
