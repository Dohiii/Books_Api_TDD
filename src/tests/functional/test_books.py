import json

# Test Posts
from src.api.models import Book


def test_add_book(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/books",
        data=json.dumps(
            {"title": "Dune", "published_year": "1984", "authors": "Frank Malfrank"}
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert "New book Dune was added to library!" in data["message"]


def test_add_book_invalid_json(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/books",
        data=json.dumps({}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_book_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/books",
        data=json.dumps({"published_year": "1975", "external_id": "jahwWShasS"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_book_duplicate_external_id(test_app, test_database):
    client = test_app.test_client()
    client.post(
        "/books",
        data=json.dumps(
            {"title": "Hobbit", "published_year": "1975", "external_id": "jahwWShasS"}
        ),
        content_type="application/json",
    )
    resp = client.post(
        "/books",
        data=json.dumps(
            {"title": "Dune", "published_year": "1984", "external_id": "jahwWShasS"}
        ),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Sorry book with same external Id already exists" in data["message"]


# Test Get Books
# Test Getters:
def test_single_user_incorrect_title(test_app, test_database):
    client = test_app.test_client()
    resp = client.get("/book/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "Book 999 does not exist" in data["message"]


def test_get_single_book(test_app, test_database, add_book):
    add_book("Halo", "Robert Mobert", "2001")
    client = test_app.test_client()
    resp = client.get("/book/3")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert "Halo" in data["title"]
    assert "2001" in data["published_year"]


def test_get_all_books(test_app, test_database, add_book):
    test_database.session.query(Book).delete()
    add_book("Dune", "Frank Mobert", "1977")
    add_book("Hobbit", "Tolkien", "1962")
    client = test_app.test_client()
    resp = client.get("/books")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2
    assert "Dune" in data[0]["title"]
    assert "1977" in data[0]["published_year"]
    assert "Hobbit" in data[1]["title"]
    assert "1962" in data[1]["published_year"]


def test_search_book(test_app, test_database, add_book):
    client = test_app.test_client()
    resp = client.get("/search?author=Tolkien&from=1960&to=2022&acquired=False")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 1
    assert "Tolkien" in data[0]["author"]
    assert "Hobbit" in data[0]["title"]


def test_search_fail_by_year(test_app, test_database, add_book):
    client = test_app.test_client()
    resp = client.get("/search?author=Tolkien&from=2020&to=2022&acquired=False")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 0


def test_import_books(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/import",
        data=json.dumps({"author": "Tolkien"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert len(data) == 1


def test_remove_book(test_app, test_database, add_book):
    test_database.session.query(Book).delete()
    book = add_book("Dune", "Frank Mobert", "1977")
    client = test_app.test_client()
    resp_one = client.get("/books")
    data = json.loads(resp_one.data.decode())
    assert resp_one.status_code == 200
    assert len(data) == 1

    resp_two = client.delete(f"/book/{book.id}")
    data = json.loads(resp_two.data.decode())
    assert resp_two.status_code == 200
    assert 'Dune was removed!' in data['message']

    resp_three = client.get("/books")
    data = json.loads(resp_three.data.decode())
    assert resp_three.status_code == 200
    assert len(data) == 0


def test_remove_book_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.delete("/book/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "Book 999 does not exist" in data["message"]

