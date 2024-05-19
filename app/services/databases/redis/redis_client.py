import redis
from typing  import Union, Dict
import json
from constants import REDIS_SOLVED_KEY, REDIS_ATTEMPTED_KEY, TTL

# from util import get_secrets
TTL = 300

class RedisClient:
    def __init__(self, host: str, port: int, password: str):
        """
        Initialize with a Redis client.
        The client is expected to be an instance of redis.Redis or compatible interface.
        """
        self.client = redis.Redis(
                host=host,
                port=port,
                password=password)
        

    def clear_cache(self) -> None:
        """Clears all keys and entries in redis cache"""
        self.client.flushdb()

    def get_decoded_value(self, key) -> Union[int, None]:
        encoded_value = self.get_value(key)
        if not encoded_value:
            return None
        try:
            decoded_value = int(encoded_value.decode('utf-8'))
            return decoded_value
        except Exception as e:
            print(f"Error retrieving and converting value encoded by Redis: {e}")
            raise

    def get_decoded_dict(self, key_to_dict: str) -> Dict:
        encoded_dict = self.get_value(key_to_dict)
        if not encoded_dict:
            return {}
        try:
            decoded_dict = json.loads(encoded_dict)
            return decoded_dict
        except Exception as e:
            print(f"Error retrieving and converting dictionary encoded by Redis: {e}")
            raise

    def set_dict(self, key_to_dict, dictionary: Dict, ttl=TTL):
        try:
            encoded_dict = json.dumps(dictionary)
            self.set_value(key_to_dict, encoded_dict, ttl)
        except Exception as e:
            print(f"Error loading dictionary object into Redis: {e}")
            raise

    def set_value(self, key, value, ttl=TTL):
        """
        Set a key-value pair.
        If TTL is provided, sets the expiration time for the key in seconds.
        """
        if ttl is not None:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def get_value(self, key):
        """
        Get a value by key.
        Returns None if the key does not exist.
        """
        return self.client.get(key)

    def check_ttl(self, key):
        """
        Check the TTL for a given key.
        Returns the TTL in seconds, -1 if the key has no expiration, or -2 if the key does not exist.
        """
        return self.client.ttl(key)


    def check_if_user_has_attempted_problem(self, user_id: str, difficulty: str):
        try:
            difficulty_map = self.get_decoded_dict(REDIS_SOLVED_KEY)
        except:
            raise Exception("Invalid key: submission_key has to be either REDIS_SOLVED_KEY constant")
        if difficulty_map and difficulty in difficulty_map and user_id in difficulty_map[difficulty]:
            return True
        return False
    
    def check_if_user_has_submitted_problem(self, user_id: str, difficulty: str):
        try:
            difficulty_map = self.get_decoded_dict(REDIS_SOLVED_KEY)
        except:
            raise Exception("Invalid key: attempt_key has to be REDIS_ATTEMPTED_KEY constant")
        if difficulty_map and difficulty in difficulty_map and user_id in difficulty_map[difficulty]:
            return True
        return False
