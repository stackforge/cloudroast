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
from cloudroast.images.v2.fixtures import ImagesV2Fixture
from cloudcafe.common.tools.datagen import rand_name


class PatchImageTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_update_image_name(self):
        """Update an image's name property.

        1. Create an image
        2. Verify response code is 201
        3. Update name of an image
        4. Verify response code is 204
        5. Verify response is an image with correct properties.
        """

        image_id = self.register_basic_image()
        updated_image_name = rand_name("updated_name_")
        response = self.api_client.update_image(
            image_id=image_id,
            replace={"name": updated_image_name})

        updated_image = response.entity

        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_image.name, updated_image_name)
        self.assertEqual(updated_image.id_, image_id)
