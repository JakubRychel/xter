import numpy as np

from app.services.embeddings_service import UserEmbeddingService


def test_retrain_output_shape(monkeypatch):
    service = UserEmbeddingService()

    # --- fake post embeddings ---
    monkeypatch.setattr(
        service.qdrant,
        "get_post_embeddings",
        lambda ids: {
            1: np.random.rand(384).astype(np.float32),
            2: np.random.rand(384).astype(np.float32),
        },
    )

    # --- fake user embeddings ---
    monkeypatch.setattr(
        service.qdrant,
        "get_user_embeddings",
        lambda ids: {},
    )

    # --- fake qdrant upsert (CAPTURE DATA) ---
    captured = {}

    def fake_upsert(data):
        captured["data"] = data
        return None

    monkeypatch.setattr(
        service.qdrant,
        "upsert_user_embeddings",
        fake_upsert,
    )

    class Job:
        user_id = 123
        post_id = 1
        alpha = 0.5

    batch = [Job()]

    import asyncio
    asyncio.run(service.retrain(batch))

    # --- ASSERTS ---
    data = captured["data"]

    assert isinstance(data, dict)

    for uid, vec in data.items():
        print("USER ID:", uid)
        print("TYPE:", type(vec))
        print("LEN:", len(vec))
        print("ELEMENT TYPE:", type(vec[0]))
        print("FIRST 5:", vec[:5])

        assert isinstance(vec, list)
        assert isinstance(vec[0], float)
        assert len(vec) == 384