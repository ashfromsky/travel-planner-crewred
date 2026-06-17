import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestInfrastructure:
    async def test_ping(self, async_client: AsyncClient):
        response = await async_client.get("/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "current_time" in data


class TestProjects:
    async def test_create_project_success(self, async_client: AsyncClient):
        payload = {
            "name": "Trip to Chicago",
            "description": "Art museum visit",
            "start_date": "2026-07-01",
            "places": [
                {"external_id": 123},
                {"external_id": 456}
            ]
        }
        response = await async_client.post("/api/v1/projects/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Trip to Chicago"
        assert len(data["places"]) == 2
        assert data["places"][0]["title"] == "Mock Artwork 123"
        assert data["places"][1]["title"] == "Mock Artwork 456"

    async def test_create_project_not_found_in_aic(self, async_client: AsyncClient):
        payload = {
            "name": "Trip with bad place",
            "places": [
                {"external_id": 999999}
            ]
        }
        response = await async_client.post("/api/v1/projects/", json=payload)
        assert response.status_code == 404

    async def test_create_project_too_many_places(self, async_client: AsyncClient):
        payload = {
            "name": "Too many places",
            "places": [{"external_id": i} for i in range(11)]
        }
        response = await async_client.post("/api/v1/projects/", json=payload)
        assert response.status_code == 422

    async def test_list_projects_pagination(self, async_client: AsyncClient):
        for i in range(5):
            payload = {"name": f"Project {i}"}
            await async_client.post("/api/v1/projects/", json=payload)

        response = await async_client.get("/api/v1/projects/?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_project_by_id_success(self, async_client: AsyncClient):
        payload = {"name": "Single Project"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Single Project"

    async def test_get_project_by_id_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/projects/9999")
        assert response.status_code == 404

    async def test_update_project(self, async_client: AsyncClient):
        payload = {"name": "Old Name", "description": "Old Desc"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        update_payload = {"name": "New Name", "description": "New Desc", "start_date": "2026-08-01"}
        response = await async_client.patch(f"/api/v1/projects/{project_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New Desc"
        assert data["start_date"] == "2026-08-01"

    async def test_delete_project_success(self, async_client: AsyncClient):
        payload = {"name": "Delete Me"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == 204

        get_res = await async_client.get(f"/api/v1/projects/{project_id}")
        assert get_res.status_code == 404

    async def test_delete_project_conflict_visited(self, async_client: AsyncClient):
        payload = {
            "name": "Cannot Delete",
            "places": [{"external_id": 123}]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_data = create_res.json()
        project_id = project_data["id"]
        place_id = project_data["places"][0]["id"]

        patch_res = await async_client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"is_visited": True}
        )
        assert patch_res.status_code == 200

        delete_res = await async_client.delete(f"/api/v1/projects/{project_id}")
        assert delete_res.status_code == 409


class TestPlaces:
    async def test_add_place_success(self, async_client: AsyncClient):
        payload = {"name": "Project for Place"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.post(
            f"/api/v1/projects/{project_id}/places/",
            json={"external_id": 100}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["external_id"] == 100
        assert data["title"] == "Mock Artwork 100"

    async def test_add_place_duplicate_conflict(self, async_client: AsyncClient):
        payload = {"name": "Duplicate Place"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        await async_client.post(
            f"/api/v1/projects/{project_id}/places/",
            json={"external_id": 100}
        )

        response = await async_client.post(
            f"/api/v1/projects/{project_id}/places/",
            json={"external_id": 100}
        )
        assert response.status_code == 409

    async def test_add_place_too_many_places(self, async_client: AsyncClient):
        payload = {
            "name": "Limit Project",
            "places": [{"external_id": i} for i in range(10)]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.post(
            f"/api/v1/projects/{project_id}/places/",
            json={"external_id": 99}
        )
        assert response.status_code == 422

    async def test_list_places(self, async_client: AsyncClient):
        payload = {
            "name": "List Places Project",
            "places": [{"external_id": 10}, {"external_id": 20}]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.get(f"/api/v1/projects/{project_id}/places/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_place_by_id_success(self, async_client: AsyncClient):
        payload = {
            "name": "Get Place Project",
            "places": [{"external_id": 50}]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_data = create_res.json()
        project_id = project_data["id"]
        place_id = project_data["places"][0]["id"]

        response = await async_client.get(f"/api/v1/projects/{project_id}/places/{place_id}")
        assert response.status_code == 200
        assert response.json()["external_id"] == 50

    async def test_get_place_by_id_not_found(self, async_client: AsyncClient):
        payload = {"name": "Empty Project"}
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_id = create_res.json()["id"]

        response = await async_client.get(f"/api/v1/projects/{project_id}/places/9999")
        assert response.status_code == 404

    async def test_patch_place_update(self, async_client: AsyncClient):
        payload = {
            "name": "Update Place Project",
            "places": [{"external_id": 30}]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_data = create_res.json()
        project_id = project_data["id"]
        place_id = project_data["places"][0]["id"]

        patch_res = await async_client.patch(
            f"/api/v1/projects/{project_id}/places/{place_id}",
            json={"notes": "Checked notes", "is_visited": True}
        )
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["notes"] == "Checked notes"
        assert data["is_visited"] is True

    async def test_project_completion_trigger(self, async_client: AsyncClient):
        payload = {
            "name": "Trigger Completion Project",
            "places": [{"external_id": 111}, {"external_id": 222}]
        }
        create_res = await async_client.post("/api/v1/projects/", json=payload)
        project_data = create_res.json()
        project_id = project_data["id"]
        place_1_id = project_data["places"][0]["id"]
        place_2_id = project_data["places"][1]["id"]

        project_res = await async_client.get(f"/api/v1/projects/{project_id}")
        assert project_res.json()["status"] == "active"

        await async_client.patch(
            f"/api/v1/projects/{project_id}/places/{place_1_id}",
            json={"is_visited": True}
        )

        project_res = await async_client.get(f"/api/v1/projects/{project_id}")
        assert project_res.json()["status"] == "active"

        await async_client.patch(
            f"/api/v1/projects/{project_id}/places/{place_2_id}",
            json={"is_visited": True}
        )

        project_res = await async_client.get(f"/api/v1/projects/{project_id}")
        assert project_res.json()["status"] == "completed"
