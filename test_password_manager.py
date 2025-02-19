import unittest
from bot import PasswordManager
import os
import json

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.pm = PasswordManager()
        self.test_user = "test_user"
        self.test_service = "test_service"
        self.test_password = "test_password123"

    def tearDown(self):
        # Clean up test data
        if os.path.exists('passwords.json'):
            os.remove('passwords.json')

    def test_add_password(self):
        self.assertTrue(self.pm.add_password(self.test_user, self.test_service, self.test_password))
        self.assertIn(self.test_user, self.pm.passwords)
        self.assertIn(self.test_service, self.pm.passwords[self.test_user])

    def test_get_password(self):
        self.pm.add_password(self.test_user, self.test_service, self.test_password)
        retrieved_password = self.pm.get_password(self.test_user, self.test_service)
        self.assertEqual(retrieved_password, self.test_password)

    def test_delete_password(self):
        self.pm.add_password(self.test_user, self.test_service, self.test_password)
        self.assertTrue(self.pm.delete_password(self.test_user, self.test_service))
        self.assertIsNone(self.pm.get_password(self.test_user, self.test_service))

    def test_list_services(self):
        self.pm.add_password(self.test_user, self.test_service, self.test_password)
        services = self.pm.list_services(self.test_user)
        self.assertIn(self.test_service, services)

    def test_encryption_decryption(self):
        # Test that encryption and decryption work correctly
        encrypted = self.pm.encrypt(self.test_password)
        decrypted = self.pm.decrypt(encrypted)
        self.assertEqual(decrypted, self.test_password)
        self.assertNotEqual(encrypted, self.test_password)

if __name__ == '__main__':
    unittest.main()