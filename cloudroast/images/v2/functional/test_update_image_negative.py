"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import cStringIO as StringIO

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageStatus, ImageVisibility
from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImageNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImageNegative, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=4)
        cls.empty_image = cls.images_behavior.create_new_image()

    @tags(type='negative', regression='true')
    def test_update_image_replace_core_property(self):
        """
        @summary: Update image replace core property

        1) Given a previously created image, update image replacing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        updated_status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            image.id_, replace={'status': updated_status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_add_core_property(self):
        """
        @summary: Update image add core property

        1) Given a previously created image, update image adding the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            image.id_, add={"status": status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_remove_core_property(self):
        """
        @summary: Update image remove core property

        1) Given a previously created image, update image removing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        response = self.images_client.update_image(
            image.id_, remove={'status': ImageStatus.QUEUED})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using blank image id

        1) Update image using blank image id
        2) Verify that the response code is 404
        """

        self._validate_update_image_with_negative_value('')

    @tags(type='negative', regression='true')
    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        self._validate_update_image_with_negative_value('invalid')

    @tags(type='negative', regression='true')
    def test_ensure_location_of_active_image_cannot_be_updated(self):
        """
        @summary: Ensure location of active image cannot be updated

        1) Using a previously created image, store an image file
        2) Verify that the response code is 204
        3) Get the stored image
        4) Verify that the image is active
        5) Update image location
        6) Verify that the response code is 403
        7) Get the image
        8) Verify that image location has not changed
        """

        file_data = StringIO.StringIO("*" * 1024)

        image = self.empty_image
        updated_location = "/v2/images/{0}/new_file".format(image.id_)

        response = self.images_client.store_image_file(
            image_id=image.id_, file_data=file_data)
        self.assertEqual(response.status_code, 204)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        active_image = response.entity
        self.assertEqual(active_image.status, ImageStatus.ACTIVE)

        response = self.images_client.update_image(
            image_id=active_image.id_, replace={"location": updated_location})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.file_, image.file_)

    @tags(type='negative', regression='true')
    def test_attempt_to_update_image_setting_visibility_to_public(self):
        """
        @summary: Attempt to update an image setting the visibility property to
        public

        1) Given a previously created image, update image setting the
        visibility property to 'public'
        2) Verify that the response code is 403
        3) List images accounting for pagination passing the filter for
        visibility set to 'public'
        4) Verify that the image that was attempted to be created is not
        present in the list
        """

        image_names = []

        image = self.images.pop()
        response = self.images_client.update_image(
            image.id_, replace={'visibility': ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        images = self.images_behavior.list_images_pagination(
            visibility=ImageVisibility.PUBLIC)
        for listed_image in images:
            image_names.append(listed_image.name)
        self.assertNotIn(image.name, image_names)

    def _validate_update_image_with_negative_value(self, image_id):
        """@summary: Update negative image"""

        response = self.images_client.update_image(
            image_id, add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(response.status_code, 404)
