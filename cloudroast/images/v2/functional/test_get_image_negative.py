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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudroast.images.fixtures import ImagesFixture


class TestGetImageNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_get_image_as_non_member_of_private_image(self):
        """
        @summary: Get image as alternate tenant that is not a member of an
        image

         1) Create image
         2) Get image using alternate tenant who has not been added as a
         member of the image
         3) Verify that the response code is 404
        """

        image = self.images_behavior.create_new_image()
        response = self.alt_images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_get_image_for_deleted_image(self):
        """
        @summary: Get image for deleted image

         1) Create image
         2) Delete image
         3) Verify that the response code is 204
         4) Get image
         5) Verify that the response code is 404
        """

        image = self.images_behavior.create_new_image()
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 404)

    @unittest.skip('Bug, Redmine #4445')
    @tags(type='negative', regression='true')
    def test_get_image_using_blank_image_id(self):
        """
        @summary: Get image using blank image id

         1) Get image using blank image id
         2) Verify that the response code is 404
        """

        image_id = ''
        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_get_image_using_invalid_image_id(self):
        """
        @summary: Get image using invalid image id

         1) Get image using invalid image id
         2) Verify that the response code is 404
        """

        image_id = 'invalid'
        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 404)
