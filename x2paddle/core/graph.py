#   Copyright (c) 2019  PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections


class GraphNode(object):
    def __init__(self, layer, layer_name=None):
        self.inputs = list()
        self.outputs = list()
        self.layer = layer

        assert layer_name is not None, "layer_name for GraphNode should not be None"
        self.layer_name = layer_name

    def __hash__(self):
        return hash(self.layer.name)

    def __eq__(self, other):
        if self.layer.name == other.layer.name:
            return True
        return False


class Graph(object):
    def __init__(self, model):
        self.node_map = collections.OrderedDict()
        self.input_nodes = list()
        self.output_nodes = list()
        self.topo_sort = list()
        self.model = model

    def build(self):
        self._make_input_nodes()
        self._make_output_nodes()
        self._get_topo_sort()

    def _make_input_nodes(self):
        for name, node in self.node_map.items():
            if len(node.inputs) == 0:
                self.input_nodes.append(name)

    def _make_output_nodes(self):
        for name, node in self.node_map.items():
            if len(node.outputs) == 0:
                self.output_nodes.append(name)

    def _get_topo_sort(self):
        num_inputs = dict()
        for name, node in self.node_map.items():
            num_inputs[name] = len(node.inputs)

        self.topo_sort = self.input_nodes[:]
        for idx in range(len(self.topo_sort)):
            current_node = self.node_map[self.topo_sort[idx]]
            for node in current_node.outputs:
                num_inputs[node.layer_name] -= 1
                if num_inputs[node.layer_name] == 0:
                    self.topo_sort.append(node.layer_name)
        for i, tmp in enumerate(self.topo_sort):
            print(tmp)

    def get_node(self, name):
        if name not in self.node_map:
            raise Exception("Graph doesn't have node [%s]." % name)
        else:
            return self.node_map[name]

    def connect(self, src, dst):
        if dst not in self.node_map:
            raise Exception("node[{}] not in graph".format(dst))
        self.node_map[dst].inputs.append(src)
