import pytest
from fastapi import status
from datetime import date, timedelta

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


def _booking_payload(room_id, check_in=None, check_out=None, **overrides):
    if check_in is None:
        check_in = (date.today() + timedelta(days=1)).isoformat()
    if check_out is None:
        check_out = (date.today() + timedelta(days=5)).isoformat()
    payload = {
        "room_id": room_id,
        "guest_name": "Иван Иванов",
        "guest_email": "ivan@example.com",
        "guests_count": 2,
        "check_in": check_in,
        "check_out": check_out,
        "season": "normal",
        "extra_service": None,
    }
    payload.update(overrides)
    return payload


def test_create_booking(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    assert room_resp.status_code == status.HTTP_201_CREATED
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    response = client.post("/bookings", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["room_id"] == room_id
    assert data["guest_name"] == payload["guest_name"]
    assert data["guest_email"] == payload["guest_email"]
    assert data["guests_count"] == payload["guests_count"]
    assert data["status"] == "pending"
    assert "total_price" in data
    assert "id" in data
    assert "created_at" in data


def test_create_booking_room_not_found(client):
    payload = _booking_payload(room_id=9999)
    response = client.post("/bookings", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Room not found"


def test_create_booking_invalid_dates(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    today = date.today()
    payload = _booking_payload(room_id, check_in=today.isoformat(), check_out=today.isoformat())
    response = client.post("/bookings", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "check_out must be after check_in" in response.json()["detail"]

    payload = _booking_payload(
        room_id, check_in=(today + timedelta(days=5)).isoformat(), check_out=today.isoformat()
    )
    response = client.post("/bookings", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_booking_room_unavailable(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    today = date.today()
    payload1 = _booking_payload(
        room_id,
        check_in=(today + timedelta(days=1)).isoformat(),
        check_out=(today + timedelta(days=5)).isoformat(),
    )
    resp1 = client.post("/bookings", json=payload1)
    assert resp1.status_code == status.HTTP_201_CREATED

    payload2 = _booking_payload(
        room_id,
        check_in=(today + timedelta(days=2)).isoformat(),
        check_out=(today + timedelta(days=4)).isoformat(),
    )
    resp2 = client.post("/bookings", json=payload2)
    assert resp2.status_code == status.HTTP_409_CONFLICT
    assert "not available" in resp2.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        lambda rid: {**_booking_payload(rid), "guests_count": 0},
        lambda rid: {**_booking_payload(rid), "guests_count": -1},
        lambda rid: {**_booking_payload(rid), "guest_name": ""},
        lambda rid: {**_booking_payload(rid), "guest_email": ""},
        lambda rid: {**_booking_payload(rid), "room_id": 0},
        lambda rid: {**_booking_payload(rid), "season": "invalid_season"},
    ],
)
def test_create_booking_invalid_data(client, payload):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    response = client.post("/bookings", json=payload(room_id))
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_bookings_empty(client):
    response = client.get("/bookings")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_bookings(client):
    room_resp1 = client.post("/rooms", json=VALID_ROOM)
    room_id1 = room_resp1.json()["id"]
    room_resp2 = client.post("/rooms", json=VALID_ROOM_2)
    room_id2 = room_resp2.json()["id"]

    payload1 = _booking_payload(room_id1, guest_name="Alice", guest_email="alice@example.com")
    payload2 = _booking_payload(room_id2, guest_name="Bob", guest_email="bob@example.com")

    client.post("/bookings", json=payload1)
    client.post("/bookings", json=payload2)

    response = client.get("/bookings")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["guest_name"] == "Alice"
    assert data[1]["guest_name"] == "Bob"


def test_get_booking(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    response = client.get(f"/bookings/{booking_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == booking_id
    assert data["guest_name"] == payload["guest_name"]
    assert data["room"]["id"] == room_id


def test_get_booking_not_found(client):
    response = client.get("/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Booking not found"


def test_get_booking_invalid_id(client):
    response = client.get("/bookings/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_booking(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    update_data = {"guest_name": "Updated Name", "guests_count": 3}
    response = client.put(f"/bookings/{booking_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["guest_name"] == "Updated Name"
    assert data["guests_count"] == 3
    assert data["guest_email"] == payload["guest_email"]


def test_update_booking_not_found(client):
    response = client.put("/bookings/9999", json={"guest_name": "Nobody"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Booking not found"


@pytest.mark.parametrize(
    "update_data",
    [
        {"guests_count": 0},
        {"guests_count": -1},
        {"guest_name": ""},
        {"guest_email": ""},
        {"season": "unknown"},
    ],
)
def test_update_booking_invalid_data(client, update_data):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    response = client.put(f"/bookings/{booking_id}", json=update_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_booking_change_dates_conflict(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    today = date.today()
    payload1 = _booking_payload(
        room_id,
        check_in=(today + timedelta(days=1)).isoformat(),
        check_out=(today + timedelta(days=5)).isoformat(),
    )
    resp1 = client.post("/bookings", json=payload1)
    assert resp1.status_code == status.HTTP_201_CREATED

    payload2 = _booking_payload(
        room_id,
        check_in=(today + timedelta(days=10)).isoformat(),
        check_out=(today + timedelta(days=15)).isoformat(),
    )
    resp2 = client.post("/bookings", json=payload2)
    assert resp2.status_code == status.HTTP_201_CREATED
    booking2_id = resp2.json()["id"]

    update_data = {
        "check_in": (today + timedelta(days=2)).isoformat(),
        "check_out": (today + timedelta(days=4)).isoformat(),
    }
    response = client.put(f"/bookings/{booking2_id}", json=update_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "not available" in response.json()["detail"]


def test_update_booking_invalid_dates(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    today = date.today()
    payload = _booking_payload(
        room_id,
        check_in=(today + timedelta(days=1)).isoformat(),
        check_out=(today + timedelta(days=5)).isoformat(),
    )
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    update_data = {
        "check_in": (today + timedelta(days=5)).isoformat(),
        "check_out": (today + timedelta(days=1)).isoformat(),
    }
    response = client.put(f"/bookings/{booking_id}", json=update_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "check_out must be after check_in" in response.json()["detail"]


def test_update_booking_no_body(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    response = client.put(f"/bookings/{booking_id}", json={})
    assert response.status_code == status.HTTP_200_OK


def test_delete_booking(client):
    room_resp = client.post("/rooms", json=VALID_ROOM)
    room_id = room_resp.json()["id"]

    payload = _booking_payload(room_id)
    create_resp = client.post("/bookings", json=payload)
    booking_id = create_resp.json()["id"]

    response = client.delete(f"/bookings/{booking_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get(f"/bookings/{booking_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_booking_not_found(client):
    response = client.delete("/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Booking not found"


def test_delete_booking_invalid_id(client):
    response = client.delete("/bookings/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
