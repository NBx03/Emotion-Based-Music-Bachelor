from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_upload_image_returns_prompt_and_analysis():
    response = client.post(
        "/api/upload",
        files={"file": ("test.png", b"fake-image-bytes", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["emotion"] == "contentment"
    assert isinstance(body["request_id"], str) and body["request_id"]
    assert isinstance(body["prompt"], str) and body["prompt"]
