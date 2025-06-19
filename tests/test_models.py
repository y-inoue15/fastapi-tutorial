import pytest
from pydantic import ValidationError
from src.models import Item, ItemResponse


class TestItem:
    """Itemモデルのテストクラス"""

    def test_item_valid_creation(self):
        """有効なデータでItemを作成できることを確認"""
        item = Item(name="test item", price=100.0)
        assert item.name == "test item"
        assert item.price == 100.0

    def test_item_minimum_valid_values(self):
        """最小限の有効な値でItemを作成できることを確認"""
        item = Item(name="a", price=0.01)
        assert item.name == "a"
        assert item.price == 0.01

    def test_item_large_values(self):
        """大きな値でItemを作成できることを確認"""
        item = Item(name="a" * 1000, price=999999.99)
        assert item.name == "a" * 1000
        assert item.price == 999999.99

    def test_item_empty_name_validation(self):
        """空の名前でValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name="", price=100.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
        assert errors[0]["loc"] == ("name",)

    def test_item_zero_price_validation(self):
        """価格が0でValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name="test item", price=0.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than"
        assert errors[0]["loc"] == ("price",)

    def test_item_negative_price_validation(self):
        """負の価格でValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name="test item", price=-10.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than"
        assert errors[0]["loc"] == ("price",)

    def test_item_missing_name(self):
        """名前が欠けている場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(price=100.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("name",)

    def test_item_missing_price(self):
        """価格が欠けている場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name="test item")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("price",)

    def test_item_invalid_name_type(self):
        """名前が文字列以外の場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name=123, price=100.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_type"
        assert errors[0]["loc"] == ("name",)

    def test_item_invalid_price_type(self):
        """価格が数値以外の場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name="test item", price="invalid")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "float_parsing"
        assert errors[0]["loc"] == ("price",)

    def test_item_none_values(self):
        """None値でValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            Item(name=None, price=None)

        errors = exc_info.value.errors()
        assert len(errors) == 2
        # nameとpriceの両方でエラーが発生
        error_locs = [error["loc"] for error in errors]
        assert ("name",) in error_locs
        assert ("price",) in error_locs

    def test_item_extra_fields_ignored(self):
        """追加のフィールドが無視されることを確認"""
        item = Item(name="test item", price=100.0, extra_field="ignored")
        assert item.name == "test item"
        assert item.price == 100.0
        assert not hasattr(item, "extra_field")

    def test_item_price_type_coercion(self):
        """価格の型変換が正しく動作することを確認"""
        # intからfloatへの変換
        item = Item(name="test item", price=100)
        assert item.price == 100.0
        assert isinstance(item.price, float)

    def test_item_string_number_price(self):
        """文字列の数値が正しく変換されることを確認"""
        item = Item(name="test item", price="100.5")
        assert item.price == 100.5
        assert isinstance(item.price, float)


class TestItemResponse:
    """ItemResponseモデルのテストクラス"""

    def test_item_response_valid_creation(self):
        """有効なデータでItemResponseを作成できることを確認"""
        response = ItemResponse(item_id=1, name="test item", price=100.0, q="search")
        assert response.item_id == 1
        assert response.name == "test item"
        assert response.price == 100.0
        assert response.q == "search"

    def test_item_response_without_q(self):
        """qパラメータなしでItemResponseを作成できることを確認"""
        response = ItemResponse(item_id=1, name="test item", price=100.0)
        assert response.item_id == 1
        assert response.name == "test item"
        assert response.price == 100.0
        assert response.q is None

    def test_item_response_q_none(self):
        """qパラメータがNoneでItemResponseを作成できることを確認"""
        response = ItemResponse(item_id=1, name="test item", price=100.0, q=None)
        assert response.item_id == 1
        assert response.name == "test item"
        assert response.price == 100.0
        assert response.q is None

    def test_item_response_missing_required_fields(self):
        """必須フィールドが欠けている場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            ItemResponse()

        errors = exc_info.value.errors()
        assert len(errors) == 3  # item_id, name, priceが必須
        error_locs = [error["loc"][0] for error in errors]
        assert "item_id" in error_locs
        assert "name" in error_locs
        assert "price" in error_locs

    def test_item_response_invalid_item_id_type(self):
        """item_idが整数以外の場合にValidationErrorが発生することを確認"""
        with pytest.raises(ValidationError) as exc_info:
            ItemResponse(item_id="invalid", name="test item", price=100.0)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "int_parsing"
        assert errors[0]["loc"] == ("item_id",)

    def test_item_response_negative_item_id(self):
        """負のitem_idでもItemResponseを作成できることを確認（バリデーション制約なし）"""
        response = ItemResponse(item_id=-1, name="test item", price=100.0)
        assert response.item_id == -1

    def test_item_response_zero_item_id(self):
        """item_idが0でもItemResponseを作成できることを確認（バリデーション制約なし）"""
        response = ItemResponse(item_id=0, name="test item", price=100.0)
        assert response.item_id == 0

    def test_item_response_type_coercion(self):
        """型変換が正しく動作することを確認"""
        response = ItemResponse(item_id="123", name="test item", price="100.5")
        assert response.item_id == 123
        assert isinstance(response.item_id, int)
        assert response.price == 100.5
        assert isinstance(response.price, float)

    def test_item_response_empty_name(self):
        """空の名前でもItemResponseを作成できることを確認（バリデーション制約なし）"""
        response = ItemResponse(item_id=1, name="", price=100.0)
        assert response.name == ""

    def test_item_response_zero_price(self):
        """価格が0でもItemResponseを作成できることを確認（バリデーション制約なし）"""
        response = ItemResponse(item_id=1, name="test item", price=0.0)
        assert response.price == 0.0

    def test_item_response_negative_price(self):
        """負の価格でもItemResponseを作成できることを確認（バリデーション制約なし）"""
        response = ItemResponse(item_id=1, name="test item", price=-100.0)
        assert response.price == -100.0


class TestModelComparison:
    """モデル間の比較テスト"""

    def test_item_vs_item_response_validation_differences(self):
        """ItemとItemResponseのバリデーション制約の違いを確認"""
        # Itemは厳しいバリデーションがある
        with pytest.raises(ValidationError):
            Item(name="", price=0.0)

        # ItemResponseは緩いバリデーション（制約なし）
        response = ItemResponse(item_id=1, name="", price=0.0)
        assert response.name == ""
        assert response.price == 0.0

    def test_models_json_serialization(self):
        """モデルのJSON変換が正しく動作することを確認"""
        item = Item(name="test item", price=100.0)
        response = ItemResponse(item_id=1, name="test item", price=100.0, q="search")

        # JSON形式に変換できることを確認
        item_json = item.model_dump()
        response_json = response.model_dump()

        assert isinstance(item_json, dict)
        assert isinstance(response_json, dict)
        assert item_json["name"] == "test item"
        assert response_json["q"] == "search"

    def test_models_from_dict(self):
        """辞書からモデルを作成できることを確認"""
        item_data = {"name": "test item", "price": 100.0}
        response_data = {
            "item_id": 1,
            "name": "test item",
            "price": 100.0,
            "q": "search",
        }

        item = Item(**item_data)
        response = ItemResponse(**response_data)

        assert item.name == "test item"
        assert response.q == "search"
