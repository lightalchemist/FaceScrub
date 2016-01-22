#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is released under a Creative Commons Attribution-NonCommercial 4.0 International Public License.
To view a copy of this license, visit <http://creativecommons.org/licenses/by-nc/4.0/legalcode>

File: python3_download_facescrub.py
Author: Hong-Wei Ng
Email: lightalchemist@gmail.com
Github: https://github.com/lightalchemist
Description: Script to download FaceScrub dataset

Tested on Ubuntu 14.04, Python 2.7.

# Requirements:
pip install requests

# Interchangeable with PIL. Can be ignored if you already have PIL installed
pip install Pillow

# Optional, but good to have, for detecting file type. May not work on Windows
pip install python-magic

# Steps to download FaceScrub dataset
1. First, obtain the FaceScrub files containing links to the images from http://vintage.winklerbros.net/facescrub.html
2. Next, set MY_USER_AGENT_STRING below. You can obtain it by visiting a site such as https://www.whatismybrowser.com/detect/what-is-my-user-agent
3. Finally, run download_facescrub.py to download the dataset.

# Example to download actors images.

Note: actors_users_normal_bbox.txt is obtained from the above link.

>>> # To download and save full size images only
>>> python python3_download_facescrub.py actors_users_normal_bbox.txt actors/

>>> # To download and save full size images along with cropped faces
>>> python python3_download_facescrub.py actors_users_normal_bbox.txt actors/ --crop_face

>>> # Additional (optional) arguments to set log file name and time out to 10 seconds
>>> python python3_download_facescrub.py actors_users_normal_bbox.txt actors/ --crop_face --logfile=download.log --timeout=10

The above code will save full size images to the directory actors/images and faces (if required) to actors/faces

"""

import os
import shutil
import mimetypes
import logging
import urllib.parse
import hashlib
import argparse

import imghdr
try:
    import magic
    has_magic_lib = True
except ImportError as e:
    has_magic_lib = False

from PIL import Image
import requests
from requests import ConnectionError
from requests import TooManyRedirects
from requests import Timeout
from requests import HTTPError
from requests import RequestException


# Visit website and copy user agent string as single line https://www.whatismybrowser.com/detect/what-is-my-user-agent
MY_USER_AGENT_STRING="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/47.0.2526.106 Chrome/47.0.2526.106 Safari/537.36"


def create_logger(logfilename):
    """Create logger for logging to screen and file."""

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logfilename)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s\n%(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Also print log messages to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)


def hashfile(afile, hasher=None, blocksize=65536):
    """Returns sha256 hash of file"""

    if not hasher:
        hasher = hashlib.sha256()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def hashbinary(raw_bytes, hasher=None):
    """Returns sha256 hash of raw bytes"""

    if not hasher:
        hasher = hashlib.sha256()
    hasher.update(raw_bytes)
    return hasher.hexdigest()


def get_referer(url):
    """Returns a made up a referer from the given url"""

    parsed_uri = urllib.parse.urlparse(url)
    netloc = parsed_uri.netloc
    scheme = parsed_uri.scheme
    if netloc.startswith("fansshare"):  # Hack for fansshare.
        netloc = "www." + netloc

    domain = '{}://{}'.format(scheme, netloc)
    return domain


def generate_headers(url):
    """Returns dict for header of requests"""

    user_agent = MY_USER_AGENT_STRING
    referer = get_referer(url)
    headers = {"Referer":referer, "User-agent":user_agent}
    return headers


def download_image(counter, url, sha256, timeout=60):
    """Download image from url.
    Returns response object if successful else return None
    """

    logger = logging.getLogger("logger")
    try:
        headers = generate_headers(url)
        response = requests.get(url, headers=headers, timeout=timeout)

        if response.status_code != requests.codes.OK:  # Status 200
            logger.error("Line {number}: Bad status code {status}: {url}".format(number=counter,
                                                                                 status=response.status_code,
                                                                                 url=url))
            return None

        # Check if returned image
        if has_magic_lib:
            # This returns byte string
            content_type = magic.from_buffer(response.content, mime=True)
            # Convert to unicode
            content_type = content_type.decode("utf-8")
        else:
            content_type = response.headers["content-type"]  # Sometimes this is missing, raising KeyError

        if (content_type is None) or not content_type.startswith("image"):
            logger.error("Line {number}: Invalid content-type {content_type}: {url}".format(number=counter,
                                                                                            content_type=content_type,
                                                                                            url=url))
            return None

        if hashbinary(response.content) != sha256:
            logger.error("Line {number}: SHA 256 hash different: {url}".format(number=counter, url=url))
            return None

        return response

    except KeyError as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None
    except ConnectionError as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None
    except HTTPError as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None
    except Timeout as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None
    except TooManyRedirects as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None
    except RequestException as e:
        logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
        return None


def parse_line(line):
    """Parse a line in FaceScrub data file"""

    parts = line.rstrip().split('\t')  # Split on tabs

    name = parts[0]
    image_id = int(parts[1])
    face_id = int(parts[2])
    url = parts[3]
    bbox = list(map(int, parts[4].split(',')))  # This is a list of int
    sha256 = parts[5]

    return name, image_id, face_id, url, bbox, sha256


def ensure_dir_exists(dirpath):
    """Create directory specified by dirpath if it does not exists"""
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def save_image(counter, response, datasetpath, name, image_id, face_id, bbox, save_face=False):
    """Save image

    Full images saved to datasetpath/images/name_image_id.ext
    Face images saved to datasetpath/faces/name_image_id_face_id.ext

    Returns True if successful else False

    """

    logger = logging.getLogger("logger")

    url = response.url

    # Output dir for images is datasetpath/images/name
    output_dir = os.path.join(datasetpath, "images", name)
    ensure_dir_exists(output_dir)

    # Filename without extension
    filename = "{name}_{image_id}".format(name=name,
                                          image_id=image_id)
    outpath = os.path.join(output_dir, filename)

    # Save file without file extension
    with open(outpath, 'wb') as outfile:
        outfile.write(response.content)

    filetype = imghdr.what(outpath)

    # Cannot determine filetype.
    if filetype is None and not has_magic_lib:
        os.remove(outpath)
        logger.error("Line {number}: Cannot determine file type: {url}".format(number=counter, url=url))
        return False

    # Get filetype using lib magic
    elif filetype is None and has_magic_lib:
        mimetype = magic.from_buffer(response.content, mime=True)
        if mimetype is None:
            logger.error("Line {number}: Cannot determine file type: {url}".format(number=counter, url=url))
            return False

        ext = mimetypes.guess_extension(mimetype).lstrip('.')
        if ext is None:
            logger.error("Line {number}: Cannot determine file type: {url}".format(number=counter, url=url))
            return False
        elif ext == "jpe":
            filetype = "jpeg"

    # Rename file to have extension
    newpath = "{}.{}".format(outpath, filetype)
    shutil.move(outpath, newpath)

    # If user wants face images
    if save_face:
        try:
            I = Image.open(newpath)
            output_dir = os.path.join(datasetpath, "faces", name)
            ensure_dir_exists(output_dir)
            filename = "{name}_{image_id}_{face_id}.{ext}".format(name=name,
                                                                  image_id=image_id,
                                                                  face_id=face_id,
                                                                  ext=filetype)
            I.crop(bbox).save(os.path.join(output_dir, filename))
        except IOError as e:
            logger.error("Line {number}: {error}: {url}".format(number=counter, error=e, url=url))
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Script to download images for FaceScrub dataset")
    parser.add_argument("inputfile", help="FaceScrub data file. E.g., actors_users_normal_bbox.txt", type=str)
    parser.add_argument("datasetpath", help="Directory to save images", type=str)
    parser.add_argument("--crop_face", help="Whether to crop and save face images", dest="crop_face", action="store_true", default=False)
    parser.add_argument('-t', '--timeout', type=float, help="Number of seconds (float) to wait before requests timeout", action="store", required=False, dest="timeout", default=60)
    parser.add_argument('-l', '--logfile', type=str, help="File to log operations", action="store", required=False, dest="logfile", default="download.log")
    args = parser.parse_args()

    create_logger(args.logfile)
    logger = logging.getLogger("logger")

    try:
        with open(args.inputfile) as infile:
            infile.readline()  # Discard header
            for counter, line in enumerate(infile, 1):
                name, image_id, face_id, url, bbox, sha256 = parse_line(line)
                logger.info("Downloading {}".format(url))
                response = download_image(counter, url, sha256, args.timeout)
                if response is None:
                    continue

                save_image(counter, response, args.datasetpath, name.replace(' ', '_'), image_id, face_id, bbox, save_face=args.crop_face)
    except EnvironmentError as e:
        logger.error("{}".format(e))


if __name__ == "__main__":
    main()
