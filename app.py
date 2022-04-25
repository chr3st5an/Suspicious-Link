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
import re
import os

from pymongo.collection import Collection
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

MONGO_URL    = os.getenv("MongoURL")
SHADY_DOMAIN = os.getenv("ShadyDomain")


app     = Flask(__name__)
mongodb = pymongo.MongoClient(MONGO_URL)["suspicious-link"]


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


@app.route("/post/create-link", methods=["GET", "POST"])
def create_link_page() -> str:
    """Represents the directory which processes incoming form data
    """

    if request.method != "POST":
        return redirect("/")

    url: Optional[str] = request.form.get("url")

    valid, error = check_url_validity(url)

    if not valid:
        return render_template('index.html', title="index", error=error), 400

    aliases_collection = mongodb["link-aliases"]
    url_alias, path    = generate_link(aliases_collection)

    entry = {
        "_id": path,
        "alias": url,
        "created_at": datetime.now(),
    }

    aliases_collection.insert_one(entry)

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

    aliases_collection = mongodb["link-aliases"]

    #> URL request parameters
    args = list(request.args.items())

    if len(args) != 2:
        return redirect(rick_roll, 303)

    #> Adding the request parameters to the subpath
    subpath = f"{subpath}?{args[0]}={args[1]}"

    entry = aliases_collection.find_one({"_id" : subpath})

    if entry is None:
        return redirect(rick_roll, 303)

    return redirect(entry["alias"])


@app.errorhandler(405)
def method_not_allowed(err) -> str:
    """Handles the 405 error
    """

    return render_template("method_not_allowed.html"), 405


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
        error = 'No URL received, please try again'
    elif url not in re.findall(r"https?:\/\/(?:[a-z]+?\.)?.+?\.[a-z]{2,}(?::\d{1,5})?(?:(?=\/).*)?", url):
        error = 'Please match the required URL format'
    elif SHADY_DOMAIN in url:
        error = "Cannot link to another alias"

    return (False if error else True), error


def generate_link(collection: Collection) -> Tuple[str, str]:
    """Generates a suspicious link

    Parameters
    ----------
    collection : pymongo.collection.Collection
        Used to check if the link already exists

    Returns
    -------
    Tuple[str, str]
        The first str represents the entire URL linking
        to the alias. The second str represent the
        generated subpath.
    """

    subpath = choice(["", "-", "_"]).join(choices(DATA["words"], k=3)) + "?" + choice(DATA["parameters"])

    #> Check if the link is already in the database
    if collection.find_one({"_id": subpath}):
        return generate_link(collection)

    return f"http://{SHADY_DOMAIN}/{subpath}", subpath


if __name__ == '__main__':
    #> Only logs errors
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    app.run()
