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

import calendar
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestTaskStates(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_import_task_states(self):
        """
        @summary: Import task states - pending, processing, success

        1) Create import task
        2) Verify that the response code is 201
        3) Verify that the status is 'pending'
        4) Get task, verify that the status changes from 'pending' to
        'processing'
        5) Get task, verify that the status changes from 'processing' to
        'success'
        6) Verify that the task's properties appear correctly
        7) Verify that a result property with image_id is returned
        8) Verify that a message property is not returned
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        self.assertEqual(task.status, TaskStatus.PENDING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.PROCESSING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.SUCCESS)

        get_expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if get_expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                get_expires_at_delta))
        if self.id_regex.match(task.result.image_id) is None:
            errors.append(self.error_msg.format(
                'image_id', 'not None',
                self.id_regex.match(task.result.image_id)))
        if task.message is not None:
            errors.append(self.error_msg.format(
                'message', None, task.message))

        self.assertListEqual(errors, [])

    @tags(type='positive', regression='true')
    def test_export_task_states(self):
        """
        @summary: Export task states - pending, processing, success

        1) Create new image
        2) Create export task
        2) Verify that the response code is 201
        3) Verify that the status is 'pending'
        4) Get task, verify that the status changes from 'pending' to
        'processing'
        5) Get task, verify that the status changes from 'processing' to
        'success'
        6) Verify that the task's properties appear correctly
        7) Verify that a result property with export location is returned
        8) Verify that a message property is not returned
        """

        image = self.images_behavior.create_new_image()
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}
        expected_location = '{0}/{1}'.format(self.export_to, image.id_)

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        self.assertEqual(task.status, TaskStatus.PENDING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.PROCESSING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.SUCCESS)

        get_expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if get_expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                get_expires_at_delta))
        if task.result.export_location != expected_location:
            errors.append(self.error_msg.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.message is not None:
            errors.append(self.error_msg.format(
                'message', None, task.message))

        self.assertListEqual(errors, [])

    @tags(type='negative', regression='true', test='test')
    def test_import_task_states_fail(self):
        """
        @summary: Import task states - pending, processing, failing

        1) Create import task
        2) Verify that the response code is 201
        3) Verify that the status is 'pending'
        4) Get task, verify that the status changes from 'pending' to
        'processing'
        5) Delete the file being imported
        5) Get task, verify that the status changes from 'processing' to
        'failure'
        6) Verify that the task's properties appear correctly
        7) Verify that a result property with image_id is returned
        8) Verify that a message property is not returned
        """

        container_name = rand_name('container')
        object_name = rand_name('object')
        self.object_storage_behaviors.create_container(
            container_name=container_name)
        self.object_storage_behaviors.create_object(
            container_name=container_name, object_name=object_name,
            data=self.object_data)

        import_from = '{0}/{1}'.format(container_name, object_name)
        input_ = {'image_properties': {},
                  'import_from': import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        self.assertEqual(task.status, TaskStatus.PENDING)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.PROCESSING)
        response = self.object_storage_client.delete_object(
            container_name=container_name, object_name=object_name)
        self.assertEqual(response.status_code, 204)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.FAILURE)

        get_expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if get_expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                get_expires_at_delta))
        if self.id_regex.match(task.result.image_id) is None:
            errors.append(self.error_msg.format(
                'image_id', 'not None',
                self.id_regex.match(task.result.image_id)))
        if task.message is not None:
            errors.append(self.error_msg.format(
                'message', None, task.message))

        self.assertListEqual(errors, [])
