# Helper Functions
# function to check if book with this id is already in the collection
def is_external_id_in_collection(book, current_id):
    if book and book.external_id is not None and book.external_id == current_id:
        return True
