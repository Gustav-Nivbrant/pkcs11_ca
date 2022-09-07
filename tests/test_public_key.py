"""
Test our public key creation
"""

from typing import Tuple
import unittest
import json

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from asn1crypto.keys import PublicKeyInfo
from asn1crypto import pem as asn1_pem

from .lib import create_jwt_header_str


def generate_keypair() -> Tuple[str, str]:
    """Generate a rsa keypair"""

    # Generate new key
    new_private_key = rsa.generate_private_key(
        key_size=2048,
        public_exponent=65537,
    )
    new_private_key_pem = new_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    new_public_key_pem = new_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return new_private_key_pem.decode("utf-8"), new_public_key_pem.decode("utf-8")


class TestPublicKey(unittest.TestCase):
    """
    Test our public keys
    """

    def public_key_load(self, pub_key: bytes, priv_key: bytes) -> None:
        """
        Test public keys loading
        """

        # Test loading public keys
        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(
            pub_key, priv_key, "http://localhost:8000/search/public_key"
        )

        req = requests.get("http://localhost:8000/search/public_key", headers=request_headers)
        self.assertTrue(req.status_code == 200)

        public_keys = json.loads(req.text)
        data = public_keys["public_keys"]
        self.assertTrue(isinstance(data, list))
        self.assertTrue(data)
        for pem_key in data:
            pem_key = pem_key.encode("utf-8")
            if asn1_pem.detect(pem_key):
                _, _, pem_key = asn1_pem.unarmor(pem_key)

            test_key = PublicKeyInfo.load(pem_key)
            self.assertTrue(isinstance(test_key, PublicKeyInfo))
            self.assertTrue(isinstance(test_key["public_key"].dump(), bytes))
            self.assertTrue(isinstance(test_key["public_key"].native["modulus"], int))

    def test_public_key(self) -> None:
        """
        Test public keys
        """

        with open("trusted_keys/privkey1.key", "rb") as f_data:
            priv_key = f_data.read()
        with open("trusted_keys/pubkey1.pem", "rb") as f_data:
            pub_key = f_data.read()

        self.public_key_load(pub_key, priv_key)

        # Create and post a key
        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(pub_key, priv_key, "http://localhost:8000/public_key")

        _, new_public_key = generate_keypair()
        data = json.loads('{"pem": ' + '"' + new_public_key.replace("\n", "\\n") + '"' + "}")
        req = requests.post("http://localhost:8000/public_key", headers=request_headers, json=data)
        self.assertTrue(req.status_code == 200)

        data = json.loads(req.text)["public_key"].encode("utf-8")
        if asn1_pem.detect(data):
            _, _, data = asn1_pem.unarmor(data)

        test_key = PublicKeyInfo.load(data)
        self.assertTrue(isinstance(test_key, PublicKeyInfo))
        self.assertTrue(isinstance(test_key["public_key"].dump(), bytes))
        self.assertTrue(isinstance(test_key["public_key"].native["modulus"], int))

    def test_public_key_admin(self) -> None:
        """
        Test public keys admin setting
        """

        with open("trusted_keys/privkey1.key", "rb") as f_data:
            priv_key = f_data.read()
        with open("trusted_keys/pubkey1.pem", "rb") as f_data:
            pub_key = f_data.read()

        # Create and post a non admin key
        new_private_key, new_public_key = generate_keypair()

        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(pub_key, priv_key, "http://localhost:8000/public_key")

        data = json.loads('{"pem": ' + '"' + new_public_key.replace("\n", "\\n") + '"' + "}")
        req = requests.post("http://localhost:8000/public_key", headers=request_headers, json=data)
        self.assertTrue(req.status_code == 200)

        # Test to ensure the create non admin key is truly not an admin key
        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(
            new_public_key.encode("utf-8"), new_private_key.encode("utf-8"), "http://localhost:8000/search/public_key"
        )
        req = requests.get("http://localhost:8000/search/public_key", headers=request_headers)
        self.assertTrue(req.status_code == 401)

        # Create and post an admin key
        new_private_key, new_public_key = generate_keypair()
        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(pub_key, priv_key, "http://localhost:8000/public_key")

        data = json.loads('{"pem": ' + '"' + new_public_key.replace("\n", "\\n") + '"' + ',"admin": 1' "}")
        req = requests.post("http://localhost:8000/public_key", headers=request_headers, json=data)
        self.assertTrue(req.status_code == 200)

        data = json.loads(req.text)["public_key"].encode("utf-8")
        if asn1_pem.detect(data):
            _, _, data = asn1_pem.unarmor(data)

        test_key = PublicKeyInfo.load(data)
        self.assertTrue(isinstance(test_key, PublicKeyInfo))
        self.assertTrue(isinstance(test_key["public_key"].dump(), bytes))
        self.assertTrue(isinstance(test_key["public_key"].native["modulus"], int))

        # Test to use the admin key
        request_headers = {}
        request_headers["Authorization"] = create_jwt_header_str(
            new_public_key.encode("utf-8"), new_private_key.encode("utf-8"), "http://localhost:8000/search/public_key"
        )
        req = requests.get("http://localhost:8000/search/public_key", headers=request_headers)
        self.assertTrue(req.status_code == 200)
