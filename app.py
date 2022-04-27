"""Suspicious Link

Suspicious Link is lightweight web application written
with Flask which serves the purpose to generate
suspicious link aliases

Visit: http://4xk0.xyz/
"""

from typing import Tuple, Optional
from random import choice, choices
from datetime import datetime
import logging
import json
import re
import os

from dotenv import load_dotenv
from flask import (
    render_template,
    redirect,
    request,
    Flask,
)
import pymongo

try:
    from src import *
except ModuleNotFoundError:
    from .src import *


__author__  = "chr3st5an"
__version__ = "1.0.0"


load_dotenv()

MONGO_URL       = os.getenv("MongoURL")
DATABASE_NAME   = os.getenv("DatabaseName")
COLLECTION_NAME = os.getenv("CollectionName")


app     = Flask(__name__)
mongodb = pymongo.MongoClient(MONGO_URL)[DATABASE_NAME]


@app.route("/")
def index() -> str:
    """Represents the index page
    """

    return render_template("index.html", title="index")


@app.route("/post")
def post() -> str:
    """Redirects everyone tyring to access this directory
    """

    return redirect("/")


@app.route("/api", methods=["GET", "POST"])
def api_create_link() -> str:
    """Represents an API to which POST request can be made

    Example
    -------
    >>> from requests import post

    >>> print(post("http://.../api", data={"url": "https://..."}))
    """

    if request.method != "POST":
        return render_template("api_info.html", title="API"), 200

    response = {
        "alias": None,
        "error": None,
        "code" : 201
    }

    request_is_invalid = not all([
        request.form,
        request.form.get("url"),
        check_url_validity(request.form.get("url", ""))[0]
    ])

    if request_is_invalid:
        response["code"]  = 400
        response["error"] = "Hmmm, something is suspicious with the request"

        return json.dumps(response), 400

    url_alias, subpath = generate_link()

    create_collection_entry(subpath, request.form["url"])

    response["alias"] = url_alias

    return json.dumps(response), 201


@app.route("/post/create-link", methods=["GET", "POST"])
def create_link_page() -> str:
    """Represents the directory which processes incoming form data
    """

    if request.method != "POST":
        return redirect("/")

    submitted_url: Optional[str] = request.form.get("url")

    valid, error = check_url_validity(submitted_url)

    if not valid:
        return render_template('index.html', title="index", error=error), 400

    url_alias, subpath = generate_link()

    create_collection_entry(subpath, submitted_url)

    return render_template("index.html", title="index", alias_link=url_alias), 201


@app.route("/<path:subpath>")
def redirect_suspicious_link(subpath: str) -> str:
    """Redirects an incoming suspicious link request to its alias

    This is done by using the subpath of the suspicious link
    as key which is searched in the database. If the link
    is invalid, the user is redirected to a rick roll.

    Parameters
    ----------
    subpath : str
        The path thats tried to be accessed
    """

    rick_roll = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    if request.method != "GET":
        return redirect(rick_roll, 303)

    try:
        url_args = list(*request.args.items())
    except Exception:
        return redirect(rick_roll, 303)

    if len(url_args) != 2:
        return redirect(rick_roll, 303)

    #> Adding the request parameters to the subpath
    subpath = f"{subpath}?{url_args[0]}={url_args[1]}"

    link_collection = mongodb[COLLECTION_NAME]

    entry = link_collection.find_one({"_id" : subpath})

    if entry is None:
        return redirect(rick_roll, 303)

    return redirect(entry["alias"])


@app.errorhandler(405)
def method_not_allowed(err) -> str:
    """Handles the 405 error
    """

    return render_template("errors/method_not_allowed.html"), 405


def create_collection_entry(subpath: str, alias_for: str) -> None:
    """Creates an entry in the link-collection

    Parameters
    ----------
    subpath : str
        The subpath that will later be used to retrieve
        the alias
    alias_for : str
        The alias URL for the given subpath
    """

    link_collection = mongodb[COLLECTION_NAME]

    link_collection.insert_one({
        "_id": subpath,
        "alias": alias_for,
        "created_at": datetime.now()
    })

    return None


def check_url_validity(url: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Checks if the given URL is ready to be further processed

    Parameters
    ----------
    url : Optional[str]
        The URL to check

    Returns
    -------
    Tuple[bool, Optional[str]]
        A bool representing if the URL is valid or not. A str
        representing the issue with the URL if it is not valid.
    """

    error: Optional[str] = None

    if url is None:
        error = "No URL received, please try again"
    elif len(url) > 128:
        error = "URL can't be longer than 128 characters"
    elif url not in re.findall(r"https?:\/\/(?:[a-z]+?\.)?.+?\.[a-z]{2,}(?::\d{1,5})?(?:(?=\/).*)?", url):
        error = "Please match the required URL format"
    elif request.host in url:
        error = "Cannot link to another alias"

    return (False if error else True), error


def generate_link() -> Tuple[str, str]:
    """Generates a suspicious link

    Returns
    -------
    Tuple[str, str]
        The first str represents the entire URL linking
        to the alias. The second str represent the
        generated subpath.
    """

    link_collection = mongodb[COLLECTION_NAME]

    subpath = choice(["", "-", "_"]).join(choices(DATA["words"], k=3)) + "?" + choice(DATA["parameters"])

    #> Check if the link is already in the database
    if link_collection.find_one({"_id": subpath}):
        return generate_link()

    return f"{request.host_url}{subpath}", subpath


if __name__ == '__main__':
    #> Only logs errors
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    app.run()
