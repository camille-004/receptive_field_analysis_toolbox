import numpy as np
import pytest

from rfa_toolbox.architectures.resnet import resnet18, resnet101
from rfa_toolbox.architectures.vgg import vgg16
from rfa_toolbox.graphs import EnrichedNetworkNode, LayerDefinition
from rfa_toolbox.utils.graph_utils import (
    obtain_all_critical_layers,
    obtain_all_nodes,
    obtain_border_layers,
)


@pytest.fixture()
def single_node():
    node0 = EnrichedNetworkNode(
        name="Layer0",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[],
    )
    return node0


@pytest.fixture()
def sequential_network():
    node0 = EnrichedNetworkNode(
        name="Layer0",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[],
    )
    node1 = EnrichedNetworkNode(
        name="Layer1",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node0],
    )
    node2 = EnrichedNetworkNode(
        name="Layer2",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node1],
    )
    node3 = EnrichedNetworkNode(
        name="Layer3",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node2],
    )
    node4 = EnrichedNetworkNode(
        name="Layer4",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node3],
    )
    node5 = EnrichedNetworkNode(
        name="Layer5",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node4],
    )
    node6 = EnrichedNetworkNode(
        name="Layer6",
        layer_info=LayerDefinition(name="Softmax", kernel_size=1, stride_size=1),
        predecessors=[node5],
    )
    return node6


@pytest.fixture()
def nonsequential_network():
    node0 = EnrichedNetworkNode(
        name="Layer0",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[],
    )
    node1 = EnrichedNetworkNode(
        name="Layer1",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node0],
    )
    node2 = EnrichedNetworkNode(
        name="Layer2",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node1],
    )
    node3 = EnrichedNetworkNode(
        name="Layer3",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node2],
    )
    node4 = EnrichedNetworkNode(
        name="Layer4",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node2],
    )
    node5 = EnrichedNetworkNode(
        name="Layer5",
        layer_info=LayerDefinition(name="Conv3x3", kernel_size=3, stride_size=1),
        predecessors=[node4, node3],
    )
    node6 = EnrichedNetworkNode(
        name="Layer6",
        layer_info=LayerDefinition(name="Softmax", kernel_size=1, stride_size=1),
        predecessors=[node5],
    )
    return node6


class TestObtainAllNodes:
    def test_obtain_node_in_single_graph_network(self, single_node):
        node = obtain_all_nodes(single_node)
        assert node == [single_node]

    def test_obtain_node_from_non_output_node(self, sequential_network):
        nodes = obtain_all_nodes(sequential_network.predecessors[0].predecessors[0])
        assert len(nodes) == 7
        for i, node in enumerate(nodes):
            assert node.name == f"Layer{i}"

    def test_for_sequential_architecture(self, sequential_network):
        nodes = obtain_all_nodes(sequential_network)
        assert len(nodes) == 7
        for i, node in enumerate(nodes):
            assert node.name == f"Layer{i}"

    def test_for_non_sequential_architecture(self, nonsequential_network):
        nodes = obtain_all_nodes(nonsequential_network)
        assert len(nodes) == 7
        names = {f"Layer{6 - i}" for i in range(7)}
        actual_names = {node.name for node in nodes}
        assert names == actual_names


@pytest.fixture()
def vgg16_model():
    return vgg16()


@pytest.fixture()
def resnet18_model():
    return resnet18()


@pytest.fixture()
def resnet101_model():
    return resnet101()


class TestObtainAllCriticalLayers:
    def test_obtain_all_ciritcal_layers(self, vgg16_model):
        ciritical_layers = obtain_all_critical_layers(vgg16_model, 32, False)
        all_layers = obtain_all_nodes(vgg16_model)
        print(ciritical_layers)
        assert len(ciritical_layers) == 13
        for layer in all_layers:
            if layer.is_in(ciritical_layers):
                assert layer.receptive_field_min > 32
            else:
                assert layer.receptive_field_min <= 32

    def test_obtaining_critical_layers_with_filter_of_dense_layers(self, vgg16_model):
        ciritical_layers = obtain_all_critical_layers(vgg16_model, 32, True)
        all_layers = obtain_all_nodes(vgg16_model)
        print(ciritical_layers)
        assert len(ciritical_layers) == 10
        for layer in all_layers:
            if layer.is_in(ciritical_layers) and layer.kernel_size != np.inf:
                assert layer.receptive_field_min > 32
            else:
                assert (
                    layer.receptive_field_min <= 32
                    or layer.receptive_field_min == np.inf
                )

    def test_obtaining_ciritcal_layers_for_multipath_architecturs(self, resnet18_model):
        ciritical_layers = obtain_all_critical_layers(resnet18_model, 32, True)
        all_layers = obtain_all_nodes(resnet18_model)
        print(ciritical_layers)
        assert len(ciritical_layers) == 9
        for layer in all_layers:
            if layer.is_in(ciritical_layers) and layer.kernel_size != np.inf:
                assert layer.receptive_field_min > 32
            else:
                assert (
                    layer.receptive_field_min <= 32
                    or layer.receptive_field_min == np.inf
                )


class TestObtainBorderLayers:
    def test_obtaining_border_layer_if_there_is_none(self, vgg16_model):
        input_res = 42000
        borders = obtain_border_layers(
            vgg16_model, input_resolution=input_res, filter_dense=True
        )
        assert len(borders) == 0
        for border in borders:
            assert border.receptive_field_min >= input_res
            for pred in border.predecessors:
                assert pred.receptive_field_min >= input_res

    def test_obtaining_border_layer_without_filter(self, vgg16_model):
        input_res = 42000
        borders = obtain_border_layers(
            vgg16_model, input_resolution=input_res, filter_dense=False
        )
        assert len(borders) == 2
        for border in borders:
            assert border.receptive_field_min >= input_res
            for pred in border.predecessors:
                assert pred.receptive_field_min >= input_res

    def test_obtaining_border_layer_on_in_a_sequential_architecture(self, vgg16_model):
        input_res = 32
        borders = obtain_border_layers(
            vgg16_model, input_resolution=input_res, filter_dense=True
        )
        assert len(borders) == 10
        for border in borders:
            assert border.receptive_field_min >= input_res
            for pred in border.predecessors:
                assert pred.receptive_field_min >= input_res

    def test_obtaining_border_layer_if_there_are_many(self, resnet18_model):
        input_res = 32
        borders = obtain_border_layers(
            resnet18_model, input_resolution=input_res, filter_dense=True
        )
        assert len(borders) == 3
        for border in borders:
            assert border.receptive_field_min >= input_res
            for pred in border.predecessors:
                assert pred.receptive_field_min >= input_res

    def test_obtaining_border_layer_in_very_large_architecture(self, resnet101_model):
        input_res = 32
        borders = obtain_border_layers(
            resnet101_model, input_resolution=input_res, filter_dense=True
        )
        assert len(borders) == 26
        for border in borders:
            assert border.receptive_field_min >= input_res
            for pred in border.predecessors:
                assert pred.receptive_field_min >= input_res
