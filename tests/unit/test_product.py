import math
import random

from app.models.product import product_table
from app.schemas.product import ProductCreateRequest, ProductCreateResponse
from app.services.product import ProductService


async def test_create_product(mocker, db_connection):
    test_product_dict = {
        "id": 100,
        "name": "test product {rand}".format(rand=math.floor(random.random() * 10000)),
        "image": "http://example.com",
        "description": "best product",
        "price": 1000,
        "stock": 10,
    }
    test_product = ProductCreateRequest(**test_product_dict)
    expected_product = ProductCreateResponse(**test_product_dict)

    mock_mappings = mocker.Mock()
    mock_mappings.first.return_value = test_product_dict
    mock_records = mocker.Mock()
    mock_records.mappings.return_value = mock_mappings

    mock_db = mocker.AsyncMock()
    mock_db.execute.return_value = mock_records

    mocker.patch("app.database.database_connection")
    product_service = ProductService(mock_db)

    try:
        result = await product_service.create(test_product)
        assert result == expected_product
        # Really should assert the correct input, but too much for now
        mock_db.execute.assert_called_once()
    finally:
        delete_statement = product_table.delete().where(
            product_table.c.name == test_product_dict["name"]
        )
        await db_connection.execute(delete_statement)
