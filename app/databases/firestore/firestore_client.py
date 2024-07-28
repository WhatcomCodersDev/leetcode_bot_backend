# Singleton class for Firestore client

from google.cloud import firestore

class FirestoreClient:
    _instance = None

    @staticmethod
    def get_instance(project_name: str, database: str = "github-commit-data"):
        if FirestoreClient._instance is None:
            FirestoreClient(project_name, database)
        return FirestoreClient._instance

    def __init__(self, project_name: str, database: str = "github-commit-data"):
        if FirestoreClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.client = firestore.Client(project=project_name, database=database)
            FirestoreClient._instance = self