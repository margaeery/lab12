import pytest
from fastapi import status

VALID_ROOM = {
    "room_number": "101",
    "room_type": "standard",
    "price_per_night": 2500.0,
    "floor": 1,
    "capacity": 2,
}

VALID_ROOM_2 = {
    "room_number": "102",
    "room_type": "suite",
    "price_per_night": 5000.0,
    "floor": 2,
    "capacity": 4,
}


def test_create_room(client):
    response = client.post("/rooms", json=VALID_ROOM)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["room_number"] == VALID_ROOM["room_number"]
    assert data["room_type"] == VALID_ROOM["room_type"]
    assert data["price_per_night"] == VALID_ROOM["price_per_night"]
    assert data["floor"] == VALID_ROOM["floor"]
    assert data["capacity"] == VALID_ROOM["capacity"]
    assert "id" in data


def test_create_room_duplicate_number(client):
    client.post("/rooms", json=VALID_ROOM)
    response = client.post("/rooms", json=VALID_ROOM)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {**VALID_ROOM, "price_per_night": -100},
        {**VALID_ROOM, "price_per_night": 0},
        {**VALID_ROOM, "capacity": 0},
        {**VALID_ROOM, "capacity": -1},
        {**VALID_ROOM, "room_number": ""},
        {**VALID_ROOM, "room_type": "invalid_type"},
        {"room_number": "103", "room_type": "family"},
    ],
)
def test_create_room_invalid_data(client, payload):
    response = client.post("/rooms", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_rooms_empty(client):
    response = client.get("/rooms")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_rooms(client):
    client.post("/rooms", json=VALID_ROOM)
    client.post("/rooms", json=VALID_ROOM_2)
    response = client.get("/rooms")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["room_number"] == VALID_ROOM["room_number"]
    assert data[1]["room_number"] == VALID_ROOM_2["room_number"]


def test_get_room(client):
    create_response = client.post("/rooms", json=VALID_ROOM)
    room_id = create_response.json()["id"]
    response = client.get(f"/rooms/{room_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == room_id
    assert data["room_number"] == VALID_ROOM["room_number"]


def test_get_room_not_found(client):
    response = client.get("/rooms/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_get_room_invalid_id(client):
    response = client.get("/rooms/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_room(client):
    create_response = client.post("/rooms", json=VALID_ROOM)
    room_id = create_response.json()["id"]
    update_data = {"price_per_night": 3000.0, "capacity": 3}
    response = client.put(f"/rooms/{room_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["price_per_night"] == 3000.0
    assert data["capacity"] == 3
    assert data["room_number"] == VALID_ROOM["room_number"]


def test_update_room_not_found(client):
    response = client.put("/rooms/9999", json={"price_per_night": 1000.0})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_update_room_duplicate_number(client):
    client.post("/rooms", json=VALID_ROOM)
    create_response = client.post("/rooms", json=VALID_ROOM_2)
    room_id = create_response.json()["id"]
    response = client.put(f"/rooms/{room_id}", json={"room_number": VALID_ROOM["room_number"]})
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"price_per_night": -10},
        {"price_per_night": 0},
        {"capacity": 0},
        {"capacity": -5},
        {"room_number": ""},
        {"room_type": "unknown"},
    ],
)
def test_update_room_invalid_data(client, payload):
    create_response = client.post("/rooms", json=VALID_ROOM)
    room_id = create_response.json()["id"]
    response = client.put(f"/rooms/{room_id}", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_room_no_body(client):
    create_response = client.post("/rooms", json=VALID_ROOM)
    room_id = create_response.json()["id"]
    response = client.put(f"/rooms/{room_id}", json={})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["room_number"] == VALID_ROOM["room_number"]


def test_delete_room(client):
    create_response = client.post("/rooms", json=VALID_ROOM)
    room_id = create_response.json()["id"]
    response = client.delete(f"/rooms/{room_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    get_response = client.get(f"/rooms/{room_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_room_not_found(client):
    response = client.delete("/rooms/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_delete_room_invalid_id(client):
    response = client.delete("/rooms/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_update_room_invalid_id(client):
    response = client.put("/rooms/abc", json={"price_per_night": 1000.0})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY