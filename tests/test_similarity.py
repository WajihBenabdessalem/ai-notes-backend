from notes_backend.similarity import cosine_similarity, rank_by_similarity


def test_cosine_similarity_identical_vectors_is_one():
    assert cosine_similarity([1, 0, 0], [1, 0, 0]) == 1.0


def test_cosine_similarity_orthogonal_vectors_is_zero():
    assert cosine_similarity([1, 0], [0, 1]) == 0.0


def test_cosine_similarity_handles_empty_or_mismatched_vectors():
    assert cosine_similarity([], [1, 2]) == 0.0
    assert cosine_similarity([1, 2], [1, 2, 3]) == 0.0


def test_rank_by_similarity_orders_descending_and_respects_top_k():
    query = [1, 0]
    candidates = [("a", [0, 1]), ("b", [1, 0]), ("c", [0.7, 0.7])]

    ranked = rank_by_similarity(query, candidates, top_k=2)

    assert [item_id for item_id, _ in ranked] == ["b", "c"]
