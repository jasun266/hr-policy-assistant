from conftest import as_user


def test_requires_a_known_employee(client):
    assert client.get("/api/me/balance").status_code == 422          # header missing
    assert client.get("/api/me/balance", headers=as_user("X999")).status_code == 401


def test_chat_draft_confirm_approve_flow(client):
    r = client.post("/api/chat", headers=as_user("E001"),
                    json={"message": "Please apply annual leave from 2026-11-08 to 2026-11-12"})
    assert r.status_code == 200
    draft = r.json()["drafts"][0]

    assert client.post(f"/api/me/requests/{draft['id']}/confirm", headers=as_user("E002")).status_code == 404
    assert client.post(f"/api/me/requests/{draft['id']}/confirm", headers=as_user("E001")).json()["status"] == "pending"

    team = client.get("/api/team/requests", headers=as_user("M001")).json()
    assert [t["id"] for t in team] == [draft["id"]] and team[0]["employee_name"] == "Rahim Uddin"
    assert client.post(f"/api/team/requests/{draft['id']}/approve", headers=as_user("E002")).status_code == 404
    assert client.post(f"/api/team/requests/{draft['id']}/approve", headers=as_user("M001")).json()["status"] == "approved"

    annual = next(b for b in client.get("/api/me/balance", headers=as_user("E001")).json() if b["leave_type"] == "annual")
    assert (annual["used"], annual["remaining"]) == (11, 9)


def test_conversation_is_private_to_its_owner(client):
    conv = client.post("/api/chat", headers=as_user("E001"), json={"message": "What is the remote work policy?"}).json()
    r = client.post("/api/chat", headers=as_user("E002"),
                    json={"message": "what did we discuss?", "conversation_id": conv["conversation_id"]})
    assert r.status_code == 404


def test_conflict_errors_are_readable(client):
    r = client.post("/api/chat", headers=as_user("E001"),
                    json={"message": "Apply annual leave 2026-11-08 to 2026-11-08"}).json()
    rid = r["drafts"][0]["id"]
    client.post(f"/api/me/requests/{rid}/confirm", headers=as_user("E001"))
    again = client.post(f"/api/me/requests/{rid}/confirm", headers=as_user("E001"))
    assert again.status_code == 409 and again.json()["detail"]["code"] == "NOT_A_DRAFT"
