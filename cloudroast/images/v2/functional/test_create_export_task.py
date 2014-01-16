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
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestCreateExportTask(ObjectStorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestCreateExportTask, cls).setUpClass()
        cls.images = cls.images_behavior.create_new_images(count=3)

    @tags(type='smoke')
    def test_create_export_task(self):
        """
        @summary: Create export task

        1) Given a previously created image, create export task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the task properties are returned correctly
        """

        image = self.images.pop()
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)
        self._validate_specific_task_properties(
            image.id_, task, task_creation_time_in_sec)
        self.assertListEqual(errors, [])

    @tags(type='negative', regression='true')
    def test_attempt_duplicate_export_task(self):
        """
        @summary: Attempt to create a duplicate of the same export task

        1) Given a previous created image, create export task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create another export task with the same input properties
        5) Verify that the response code is 201
        6) Wait for the task to fail
        7) Verify that the failed task contains the correct message
        8) List files in the user's container
        9) Verify that the response code is 200
        10) Verify that only one image with the image name exists
        """

        image = self.images.pop()
        statuses = [TaskStatus.SUCCESS, TaskStatus.FAILURE]
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}
        exported_images = []

        for status in statuses:
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.EXPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            task = self.images_behavior.wait_for_task_status(task_id, status)
            if status == TaskStatus.FAILURE:
                self.assertEqual(
                    task.message, 'Swift already has an object with id '
                    '\'{0}.vhd\' in container \'{1}\''.
                    format(image.id_, self.export_to))

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        for obj in objects:
            if obj.name == '{0}.vhd'.format(image.id_):
                exported_images.append(obj)
        self.assertEqual(len(exported_images), 1)

    @tags(type='positive', regression='true')
    def test_export_same_image_two_different_containers(self):
        """
        @summary: Export the same image to two different containers

        1) Given a previous created image, create export task for container A
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create another export task for container B using the same image
        5) Verify that the response code is 201
        6) Wait for the task to complete successfully
        7) List files in the user container A
        8) Verify that the response code is 200
        9) Verify that only one image with the image name exists
        10) List files in the user container B
        11) Verify that the response code is 200
        12) Verify that only one image with the image name exists
        """

        image = self.images.pop()
        containers = [self.export_to, self.images_config.alt_export_to]
        exported_images = []

        for container in containers:
            input_ = {'image_uuid': image.id_,
                      'receiving_swift_container': container}
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.EXPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            self.images_behavior.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)

            response = self.object_storage_client.list_objects(self.export_to)
            self.assertEqual(response.status_code, 200)
            objects = response.entity

            for obj in objects:
                if obj.name == '{0}.vhd'.format(image.id_):
                    exported_images.append(obj)
            self.assertEqual(len(exported_images), 1)
            exported_images = []

    @tags(type='negative', regression='true')
    def test_attempt_to_export_base_image(self):
        """
        @summary: Attempt to export a base image

        1) Attempt to export a base image
        2) Verify that the task fails
        3) Verify that the image does not appear in the user's container
        """

        image_id = self.images_config.primary_image
        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(
            task.message, 'An image may only be exported by the image owner.')

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertNotIn('{0}.vhd'.format(image_id), exported_image_names)

    @tags(type='negative', regression='true')
    def test_attempt_to_export_windows_image(self):
        """
        @summary: Attempt to export a windows image

        1) Create a server using a windows image
        2) Create a snapshot of the server
        3) Attempt to export the windows snapshot
        4) Verify that the task fails
        5) Verify that the image does not appear in the user's container
        """

        image_id = self.images_config.windows_image
        flavor = self.images_config.windows_flavor

        response = self.server_behaviors.create_active_server(
            image_ref=image_id, flavor_ref=flavor)
        server = response.entity

        response = self.compute_image_behaviors.create_active_image(server.id)
        snapshot = response.entity

        input_ = {'image_uuid': snapshot.id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(
            task.message, 'The export of Windows based images is not allowed. '
            'Distribution of Windows code is not allowed in the Service '
            'Provider License Agreement.')

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertNotIn('{0}.vhd'.format(snapshot.id), exported_image_names)

    @unittest.skip('Bug, Redmine #5105')
    @tags(type='negative', regression='true')
    def test_export_coalesced_snapshot(self):
        """
        @summary: Export a snapshot that has multiple files and verify a single
        export file is created for it

        1) Create a server
        2) Modify something on the server
        3) Create a snapshot
        4) Export the snapshot
        5) Verify that the task is successful
        6) Verify that the image appears in the user's container as a single
        vhd file
        """

        image_id = self.images_config.primary_image

        response = self.server_behaviors.create_active_server(
            image_ref=image_id)
        server = response.entity

        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config)

        disks = remote_client.get_all_disks()
        for disk in disks:
            mount_point = '/mnt/{name}'.format(name=rand_name('disk'))
            self._mount_disk(remote_client=remote_client, disk=disk,
                             mount_point=mount_point)
            test_directory = '{mount}/test'.format(mount=mount_point)
            remote_client.create_directory(test_directory)

        response = self.compute_image_behaviors.create_active_image(server.id)
        snapshot = response.entity

        input_ = {'image_uuid': snapshot.id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)
        errors = self.images_behavior.validate_task(task)
        self.assertListEqual(errors, [])

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertEqual(len(exported_image_names), 1)
        self.assertIn('{0}.vhd'.format(snapshot.id), exported_image_names)

    def _validate_specific_task_properties(self, image_id, task,
                                           task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []

        get_created_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.created_at)
        get_updated_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.updated_at)
        get_expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)
        expected_location = '{0}/{1}.vhd'.format(self.export_to, image_id)

        if task.status != TaskStatus.SUCCESS:
            errors.append(self.error_msg.format(
                'status', TaskStatus.SUCCESS, task.status))
        if get_created_at_delta > self.max_created_at_delta:
            errors.append(self.error_msg.format(
                'created_at delta', self.max_created_at_delta,
                get_created_at_delta))
        if get_expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                get_expires_at_delta))
        if task.input_.image_uuid != image_id:
            errors.append(self.error_msg.format(
                'image_uuid', image_id, task.input_.image_uuid))
        if task.input_.receiving_swift_container != self.export_to:
            errors.append(self.error_msg.format(
                'receiving_swift_container', self.export_to,
                task.input_.receiving_swift_container))
        if get_updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                get_updated_at_delta))
        if task.type_ != TaskTypes.EXPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.EXPORT, task.type_))
        if task.result is None:
            errors.append(self.error_msg.format('result', None, task.result))
        if task.result.export_location != expected_location:
            errors.append(self.error_msg.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.owner != self.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.tenant_id, task.owner))

        self.assertListEqual(errors, [])
