"""
Copyright 2014 Rackspace

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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ServerFromImageFixture


class ServerRHELActivationTests(object):

    @tags(type='smoke', net='yes')
    def test_check_rhel_activation(self):
        # Get an instance of the remote client
        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)

        self.assertTrue(
            remote_instance.check_rhel_activation(),
            "Red Hat activation on server with uuid: {server_id} "
            "failed".format(server_id=self.server.id))


class ServerFromImageRHELActivationTests(ServerFromImageFixture,
                                         ServerRHELActivationTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageRHELActivationTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
