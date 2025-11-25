async def test_create_and_update_deal(client, session):
    ac = client
    r = await ac.post(
        "/api/v1/auth/register",
        json={
            "email": "123@example.com",
            "password": "Pass12345",
            "name": "Owner",
            "organization_name": "Acme",
        },
    )
    print(r.text)
    assert r.status_code == 200
    tokens = r.json()
    access = tokens["access_token"]

    headers = {
        "Authorization": f"Bearer {access}",
        "X-Organization-Id": "1",
    }

    # create contact
    r = await ac.post(
        "/api/v1/contacts",
        json={"name": "John", "email": "john@example.com"},
        headers=headers,
    )
    assert r.status_code == 201
    contact = r.json()

    # create deal
    r = await ac.post(
        "/api/v1/deals",
        json={
            "contact_id": contact["id"],
            "title": "New deal",
            "amount": 1000.00,
            "currency": "USD",
        },
        headers=headers,
    )
    assert r.status_code == 201
    deal = r.json()
    assert deal["amount"] == "1000.00" or float(deal["amount"]) == 1000.0

    # # try to set status won with amount 0 (should fail)
    # r = await ac.patch(
    #     f"/api/v1/deals/{deal['id']}",
    #     json={"status": "won"},
    #     headers=headers,
    # )
    # assert r.status_code in (
    #     200,
    #     400,
    # )
