from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, fields

from src import db
from src.api.models import Book

from .helpers import is_external_id_in_collection
from .import_books import ImportBooks

books_blueprints = Blueprint("books", __name__)
api = Api(books_blueprints)

response_object = {}

book_model = api.model(
    "Book",
    {
        "id": fields.Integer(readOnly=True),
        "external_id": fields.String(required=False),
        "title": fields.String(required=True),
        "authors": fields.String(required=False),
        "published_year": fields.String(required=False),
        "acquired": fields.Boolean(required=False),
        "thumbnail": fields.String(required=False),
    },
)


class BookList(Resource):
    @api.expect(book_model, validate=True)
    def post(self):
        post_data = request.get_json()
        title = post_data.get("title")
        published_year = post_data.get("published_year")
        external_id = post_data.get("external_id")
        authors = post_data.get("authors")

        book = Book.query.filter_by(external_id=external_id).first()
        if is_external_id_in_collection(book, external_id):
            response_object[
                "message"
            ] = "Sorry book with same external Id already exists"
            return response_object, 400

        db.session.add(
            Book(
                title=title,
                authors=authors,
                published_year=published_year,
                external_id=external_id,
            )
        )
        db.session.commit()

        response_object["message"] = f"New book {title} was added to library!"
        return response_object, 201

    # Get all books
    @api.marshal_with(book_model, as_list=True)
    def get(self):
        return Book.query.all(), 200


# Get book by id
class Books(Resource):
    @api.marshal_with(book_model)
    def get(self, book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            api.abort(404, f"Book {book_id} does not exist")
        return book, 200

    def delete(self, book_id):
        response_object = {}
        book = Book.query.filter_by(id=book_id).first()

        if not book:
            api.abort(404, f'Book {book_id} does not exist')

        db.session.delete(book)
        db.session.commit()
        response_object["message"] = f'{book.title} was removed!'
        return response_object, 200

    def put(self, book_id):
        post_data = request.get_json()
        title = post_data.get("title")
        published_year = post_data.get("published_year")
        authors = post_data.get("authors")
        response_object = {}

        book = Book.query.filter_by(id=book_id).first()
        if not book:
            api.abort(404, f'Book {book_id} does not exist')
        book.title = title
        book.published_year = published_year
        book.authors = authors
        db.session.commit()

        response_object["message"] = f"{book.title} was updated!"
        return response_object, 200


@books_blueprints.route("/search", methods=["GET"])
def search():
    books_list = []
    book_author = request.args.get("author")
    book_acquired = request.args.get("acquired")
    book_published_from = request.args.get("from")
    book_published_to = request.args.get("to")
    books = (
        db.session.query(Book)
        .filter(
            Book.authors.like(f"%{book_author}%"),
            Book.acquired == book_acquired,
            Book.published_year.between(book_published_from, book_published_to),
        )
        .all()
    )

    for book in books:
        if book:
            books_dict = {
                "title": book.title,
                "external_id": book.external_id,
                "author": book.authors,
                "published_year": book.published_year,
                "acquired": book.acquired,
            }
            books_list.append(books_dict)

    return jsonify(books_list), 200


api.add_resource(BookList, "/books")
api.add_resource(Books, "/book/<int:book_id>")
api.add_resource(ImportBooks, "/import")
