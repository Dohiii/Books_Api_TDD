import json

import requests
from flask import request
from flask_restx import Resource

from src import db
from src.api.models import Book

from .helpers import is_external_id_in_collection

response_object = {}


# Import books by author
class ImportBooks(Resource):
    def post(self):
        post_data = request.get_json()
        author = post_data.get("author")
        # Set type to only Books + Maximum Search results are 40 ( maximal possible for Google books api)
        api_url = f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{author}&printType=books&maxResults=40"
        a = requests.get(api_url).text
        a_info = json.loads(a)
        books = a_info["items"]
        # variable imported is here to collect how many books will be imported
        imported = 0

        # looping through books and populating database
        for i, book in enumerate(books):
            author = books[i]["volumeInfo"]["authors"]
            title = book["volumeInfo"]["title"]
            external_id = book["id"]
            thumbnail = book["volumeInfo"]["previewLink"]
            published_year = book["volumeInfo"]["publishedDate"][0:4]
            # Check if book with same external id is already exist
            collection = Book.query.filter_by(external_id=external_id).first()
            if is_external_id_in_collection(collection, external_id):
                response_object[
                    "message"
                ] = "Sorry book with same external Id already exists"
                return response_object, 400

            imported += 1
            book_object = Book(
                title=title,
                authors=author,
                published_year=published_year,
                external_id=external_id,
                thumbnail=thumbnail,
            )
            db.session.add(book_object)
            db.session.commit()

        response_object["imported"] = imported

        return response_object, 201
