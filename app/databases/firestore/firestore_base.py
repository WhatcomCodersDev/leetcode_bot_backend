# firestore_base.py
from google.cloud import firestore
from app.databases.firestore.firestore_client import FirestoreClient
from google.cloud.firestore import CollectionReference, DocumentReference

class FirestoreBase:
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        self.db = FirestoreClient.get_instance(project_name, database).client

    def get_collection(self, collection_name: str) -> CollectionReference:
        try:
            collection_ref = self.db.collection(collection_name)
        except Exception as e:
            print(f"Failed to get collection with name {collection_name} because: {e}")
            raise
        return collection_ref

    def get_doc_ref(self, collection_ref: CollectionReference, document_name: str) -> DocumentReference:
        try:
            doc_ref = collection_ref.document(str(document_name))
        except Exception as e:
            print(f"Failed to get document with name {document_name} because: {e}")
            raise
        return doc_ref
