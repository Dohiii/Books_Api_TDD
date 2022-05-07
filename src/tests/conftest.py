import pytest

from src import create_app, db
from src.api.models import Book


@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config.from_object("src.config.TestingConfig")
    with app.app_context():
        yield app  # testing happens here


@pytest.fixture(scope="module")
def test_database():
    # all code before the yield statement serves as setup
    db.create_all()
    yield db  # testing happens here
    # while everything after serves as the teardown
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="function")
def add_book():
    def _add_book(title, authors, published_year):
        book = Book(title=title, authors=authors, published_year=published_year)
        db.session.add(book)
        db.session.commit()
        return book

    return _add_book
