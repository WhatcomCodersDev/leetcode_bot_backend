# leetcode_manager.py
import uuid
from app.databases.firestore.firestore_base import FirestoreBase
from datetime import datetime
from typing import List
from constants import UUID_COLLECTION
from google.cloud.firestore_v1.base_query import FieldFilter

'''
Handles interaction with uuid_mappings collection

Collection: uuid_mappings

Description: Stores discord to uuid mappings
Document ID: discord_id (string)
Fields:
    - uuid (string): The uuid used for the website
'''


class FirestoreUserCollectionWrapper(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.uuid_collection = UUID_COLLECTION if environment == "production" else UUID_COLLECTION

    def get_uuid_from_discord_id(self, discord_id: str):
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, discord_id)
        try:
            doc = doc_ref.get()
            if not doc.exists:
                new_uuid = str(uuid.uuid4())
                doc_ref.set({"uuid": new_uuid})
                print(f"Added uuid {uuid} to discord#{discord_id} successfully to the db")
                print(f"Added uuid {uuid} to discord#{discord_id} successfully to the db")
                return doc_ref.get().to_dict()['uuid']
            else:
                user_data = doc.to_dict()
                return user_data['uuid']
    
        except Exception as e:
            print(f"Error in get_uuid_from_discord_id for user #{discord_id}: {e}")
            raise e

    def get_discord_id_from_uuid(self, uuid: str):
        collection_ref = self.get_collection(self.uuid_collection)
        try:
            query = collection_ref.where(filter=FieldFilter("uuid", "==", uuid))
            doc = query.get()

            return doc[0].id
    
        except Exception as e:
            print(f"Error in get_discord_id_from_uuid for user #{uuid}: {e}")
            raise e


