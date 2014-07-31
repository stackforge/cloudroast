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

from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudroast.compute.fixtures import ComputeAdminFixture


class PauseServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(PauseServerTests, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()

        if not response.ok:
            raise Exception(
                "Failed to create server: "
                "{code} - {reason}".format(code=response.status_code,
                                           reason=response.reason))

        if response.entity is None:
            raise Exception(
                "Response entity not set. "
                "Response was: {0}".format(response.content))

        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def test_pause_unpause_server(self):
        response = self.admin_servers_client.pause_server(self.server.id)

        if not response.ok:
            raise Exception(
                "Failed to pause server: "
                "{code} - {reason}".format(code=response.status_code,
                                           reason=response.reason))

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

        self.assertFalse(self._can_connect_to_server(),
                         'Should not be able to connect to a paused server')

        self.admin_servers_client.unpause_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        self.assertTrue(self._can_connect_to_server(),
                        "Unable to connect to active server after unpausing")

    @classmethod
    def _can_connect_to_server(cls):
        remote_client = cls.server_behaviors.get_remote_instance_client(
            cls.server, cls.servers_config, key=cls.key.private_key)
        return remote_client.can_authenticate()
