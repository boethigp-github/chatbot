import asyncio
import os
import requests
from server.app.config.settings import Settings
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.tests.test_abstract import TestAbstract
from server.app.services import gripsbox_service
import json

class TestGripsbox(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Synchronous setup, but manually run async initialization."""
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_STORAGE = cls.settings.get("default").get("APP_STORAGE")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")
        cls.TEST_FILE = "test_file.txt"

        # Manually run async initialization using asyncio.run()
        asyncio.run(cls.async_init())

        # Create the test file
        cls.create_test_file()

    @classmethod
    def create_test_file(cls):
        """Helper method to create a test file."""
        with open(cls.TEST_FILE, "wb") as f:
            f.write(b"test file content")

    @classmethod
    async def asyncTearDownClass(cls):
        """Cleanup test files."""
        gripsbox_path = os.path.join(cls.APP_STORAGE, "gripsbox")
        test_file_path = os.path.join(gripsbox_path, cls.TEST_FILE)

        # Remove the specific test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

        # Optionally, remove other files in gripsbox_path if needed
        for file_name in os.listdir(gripsbox_path):
            file_path = os.path.join(gripsbox_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def test_create_and_delete_gripsbox(self):
        """Run the async test inside a synchronous test function."""
        asyncio.run(self.async_test_create_and_delete_gripsbox())

    async def async_test_create_and_delete_gripsbox(self):
        """Test creating a new gripsbox and deleting it."""
        new_id, user_uuid = await self.create_test_gripsbox()

        # Delete the gripsbox after creating
        await self.delete_gripsbox(new_id)

        # Delete the user's gripsbox folder
        await gripsbox_service.delete_user_gripsbox_folder(user_uuid)

    async def create_test_gripsbox(self):
        """Create a test gripsbox using the model and return its UUID."""
        gripsbox_data = GripsboxPostRequestModel(
            name="Test Grip",
            size=5,
            type="Type Y",
            active=True,
            tags=["tag1", "tag2"],
            models=["gpt-3.5-turbo"]
        )

        # Convert the Pydantic model to a dictionary for form data
        payload_dict = gripsbox_data.model_dump()

        # Convert tags and models to JSON strings (expected by the API)
        payload_dict['tags'] = json.dumps(payload_dict['tags'])
        payload_dict['models'] = json.dumps(payload_dict['models'])

        # Use requests to send the API key as a query parameter and send the form data and file together
        with open(self.TEST_FILE, "rb") as f:
            response = requests.post(
                f"{self.BASE_URL}/gripsbox?api_key={self.api_key}",
                files={"file": (self.TEST_FILE, f, "text/plain")},
                data=payload_dict  # Send the model data as form fields
            )
        assert response.status_code == 201

        # Parse response to extract the UUIDs
        response_data = response.json()
        new_id = response_data.get('id')
        user_uuid = response_data.get('user')

        return new_id, user_uuid

    async def delete_gripsbox(self, gripsbox_id):
        """Delete the given gripsbox by UUID."""
        # Use requests to delete the gripsbox using the API key as a query parameter
        response = requests.delete(f"{self.BASE_URL}/gripsbox/{gripsbox_id}?api_key={self.api_key}")
        assert response.status_code == 200

    def test_update_gripsbox_active_status(self):
        """Run the async test to update the gripsbox active status."""
        asyncio.run(self.async_test_update_gripsbox_active_status())

    async def async_test_update_gripsbox_active_status(self):
        """Test updating the active status of a gripsbox."""
        # Create a test gripsbox
        new_id, _ = await self.create_test_gripsbox()

        # Update the active status to false
        response = requests.patch(
            f"{self.BASE_URL}/gripsbox/{new_id}/active?api_key={self.api_key}",
            json={"active": False}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Active status updated successfully"

