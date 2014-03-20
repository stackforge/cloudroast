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

from cafe.drivers.unittest.decorators import tags
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestDeleteImage(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImage, cls).setUpClass()
        server = cls.server_behaviors.create_active_server().entity
        image = cls.compute_image_behaviors.create_active_image(server.id)
        cls.image = cls.images_client.get_image(image.entity.id).entity

    @tags(type='smoke')
    def test_delete_image(self):
        """
        @summary: Delete image

        1) Given a previously created image, delete image
        2) Verify that the response code is 204
        3) Get deleted image
        4) Verify that the response code is 404
        """

        response = self.images_client.delete_image(self.image.id_)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(self.image.id_)
        self.assertEqual(response.status_code, 404)