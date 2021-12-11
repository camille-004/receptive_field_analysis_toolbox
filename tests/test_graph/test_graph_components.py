import json

from rfa_toolbox.network_components import ModelGraph, NetworkNode, \
    EnrichedNetworkNode, LayerDefinition


class TestLayerDefinition:

    def test_can_initialize_from_dict(self):
        layer = LayerDefinition.from_dict(**{
            "name": "test",
            "kernel_size": 3,
            "stride_size": 1}
        )
        assert layer.name == "test"
        assert layer.kernel_size == 3
        assert layer.stride_size == 1

    def test_to_dict(self):
        layer = LayerDefinition("test", 3, 1)
        assert layer.to_dict() == {
            "name": "test",
            "kernel_size": 3,
            "stride_size": 1
        }

    def test_to_dict_can_be_jsonified(self):
        layer = LayerDefinition("test", 3, 1)
        jsonified = json.dumps(layer.to_dict())
        assert isinstance(jsonified, str)

    def test_to_dict_can_be_jsonified_and_reconstituted(self):
        layer = LayerDefinition("test", 3, 1)
        jsonified = json.dumps(layer.to_dict())
        reconstituted = LayerDefinition.from_dict(**json.loads(jsonified))
        assert layer == reconstituted


class TestNetworkNode:

    def test_can_initialize_from_dict_without_nodes_and_id(self):
        node = NetworkNode.from_dict(**{
            "name": "test",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": []
        })
        assert node.name == "test"
        assert node.layer_type.name == "test1"
        assert node.layer_type.kernel_size == 3
        assert node.layer_type.stride_size == 1
        assert node.predecessor_list == []

    def test_can_initialize_from_dict_without_nodes(self):
        node = NetworkNode.from_dict(**{
            "id": 123,
            "name": "test",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": []
        })
        assert node.name == "test"
        assert node.layer_type.name == "test1"
        assert node.layer_type.kernel_size == 3
        assert node.layer_type.stride_size == 1
        assert node.predecessor_list == []

    def test_can_initialize_from_dict(self):
        node1 = NetworkNode.from_dict(**{
            "id": 124,
            "name": "B",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": []
        })

        node2 = NetworkNode.from_dict(**{
            "id": 125,
            "name": "C",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": []
        })

        node = NetworkNode.from_dict(**{
            "id": 123,
            "name": "A",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": [node1, node2]
        })

        assert node.name == "A"
        assert node.layer_type.name == "test1"
        assert node.layer_type.kernel_size == 3
        assert node.layer_type.stride_size == 1
        assert node.predecessor_list == [node1, node2]

    def test_to_dict_without_predecessor(self):
        node = NetworkNode("test", LayerDefinition("test1", 3, 1))
        assert node.to_dict() == {
            "id": id(node),
            "name": "test",
            "layer_type": {
                "name": "test1",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": []
        }

    def test_to_dict_with_predecessor(self):
        node1 = NetworkNode("A", LayerDefinition("test1", 3, 1))
        node2 = NetworkNode("B", LayerDefinition("test2", 3, 1), [node1])

        assert node2.to_dict() == {
            "id": id(node2),
            "name": "B",
            "layer_type": {
                "name": "test2",
                "kernel_size": 3,
                "stride_size": 1
            },
            "predecessor_list": [id(node1)]
        }

    def test_to_dict_can_be_jsonified(self):
        node = NetworkNode("test", LayerDefinition("test1", 3, 1))
        jsonified = json.dumps(node.to_dict())
        assert isinstance(jsonified, str)


class TestEnrichedNetworkNode:
    ...


class TestModelGraph:
    ...
