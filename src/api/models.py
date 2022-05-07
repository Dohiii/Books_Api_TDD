from src import db


# model
class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    external_id = db.Column(db.String(128), nullable=True)

    authors = db.Column(db.Text(), nullable=True)
    title = db.Column(db.Text, nullable=False)
    published_year = db.Column(db.String(128), default=None)
    acquired = db.Column(db.Boolean(), default=False, nullable=False)
    thumbnail = db.Column(db.Text(), nullable=True)

    def __init__(
        self, title, authors, published_year="N/A", external_id=None, thumbnail=None
    ):
        self.title = title
        self.authors = authors
        self.published_year = published_year
        self.external_id = external_id
        self.thumbnail = thumbnail
