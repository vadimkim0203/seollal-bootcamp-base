import pytest


@pytest.mark.skip
async def test_list_products(client, seed_product):
    response = client.get("/products?count_per_page=200")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["next"] == "http://localhost:5000/products?page=1&count_per_page=200"
    assert response_data["previous"] == ""
    assert response_data["results"][-1] == seed_product
