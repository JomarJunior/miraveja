from src.Processing.Domain.Models import Embedding, ImageEmbedding
from src.Processing.Domain.Enums import DistanceMetricEnum
from torch import Tensor

def test_serialization_and_deserialization():
    original = ImageEmbedding.create(1, Tensor([1.0, 2.0, 3.0]))
    print(f"Original: {original}")
    serialized = original.to_dict()
    print(f"Serialized: {serialized}")
    deserialized = ImageEmbedding.from_dict(serialized)
    print(f"Deserialized: {deserialized}")

    assert original == deserialized

test_serialization_and_deserialization()