from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRootEndpoint:
    """ルートエンドポイント（/）のテスト"""

    def test_root_endpoint_success(self):
        """ルートエンドポイントが正常に動作することを確認"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to the FastAPI application!"

    def test_root_endpoint_without_auth(self):
        """ルートエンドポイントは認証なしでアクセス可能であることを確認"""
        response = client.get("/")
        assert response.status_code == 200


class TestGetItemEndpoint:
    """GET /items/{item_id} エンドポイントのテスト"""

    def test_get_item_with_valid_token(self):
        """有効なトークンでアイテム取得が正常に動作することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 1
        assert data["name"] == "item1"
        assert data["price"] == 100.0
        assert data["q"] is None

    def test_get_item_with_query_parameter(self):
        """クエリパラメータ付きでアイテム取得が正常に動作することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.get("/items/5?q=search_term", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 5
        assert data["name"] == "item5"
        assert data["price"] == 100.0
        assert data["q"] == "search_term"

    def test_get_item_with_long_query_parameter(self):
        """長すぎるクエリパラメータでバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        long_query = "a" * 51  # max_length=50を超える
        response = client.get(f"/items/1?q={long_query}", headers=headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_item_with_invalid_item_id_zero(self):
        """item_idが0の場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.get("/items/0", headers=headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_item_with_invalid_item_id_negative(self):
        """item_idが負の値の場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.get("/items/-1", headers=headers)
        assert response.status_code == 422

    def test_get_item_with_invalid_item_id_string(self):
        """item_idが文字列の場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.get("/items/abc", headers=headers)
        assert response.status_code == 422

    def test_get_item_without_token(self):
        """トークンなしでアクセスした場合、403エラーが返ることを確認"""
        response = client.get("/items/1")
        assert response.status_code == 403

    def test_get_item_with_invalid_token(self):
        """無効なトークンでアクセスした場合、401エラーが返ることを確認"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid token"

    def test_get_item_with_malformed_header(self):
        """不正な形式のAuthorizationヘッダーの場合、403エラーが返ることを確認"""
        headers = {"Authorization": "InvalidFormat mocked-jwt-token"}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 403

    def test_get_item_with_empty_token(self):
        """空のトークンでアクセスした場合、403エラーが返ることを確認"""
        headers = {"Authorization": "Bearer "}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 403


class TestPostItemEndpoint:
    """POST /items エンドポイントのテスト"""

    def test_create_item_with_valid_token_and_data(self):
        """有効なトークンと正しいデータでアイテム作成が正常に動作することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "test item", "price": 50.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == 1
        assert data["name"] == "test item"
        assert data["price"] == 50.0
        assert data["q"] is None

    def test_create_item_with_minimum_valid_data(self):
        """最小限の有効なデータでアイテム作成が正常に動作することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "a", "price": 0.01}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "a"
        assert data["price"] == 0.01

    def test_create_item_with_empty_name(self):
        """空の名前でバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "", "price": 50.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_item_with_zero_price(self):
        """価格が0の場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "test item", "price": 0.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_create_item_with_negative_price(self):
        """負の価格でバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "test item", "price": -10.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422

    def test_create_item_missing_name(self):
        """名前が欠けている場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"price": 50.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422

    def test_create_item_missing_price(self):
        """価格が欠けている場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "test item"}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422

    def test_create_item_with_invalid_price_type(self):
        """価格が文字列の場合にバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        payload = {"name": "test item", "price": "invalid"}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 422

    def test_create_item_with_empty_payload(self):
        """空のペイロードでバリデーションエラーが発生することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}
        response = client.post("/items", json={}, headers=headers)
        assert response.status_code == 422

    def test_create_item_without_token(self):
        """トークンなしでアクセスした場合、403エラーが返ることを確認"""
        payload = {"name": "test item", "price": 50.0}
        response = client.post("/items", json=payload)
        assert response.status_code == 403

    def test_create_item_with_invalid_token(self):
        """無効なトークンでアクセスした場合、401エラーが返ることを確認"""
        headers = {"Authorization": "Bearer invalid-token"}
        payload = {"name": "test item", "price": 50.0}
        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 401


class TestAuthIntegration:
    """認証に関する統合テスト"""

    def test_multiple_requests_with_same_token(self):
        """同じトークンで複数のリクエストが正常に動作することを確認"""
        headers = {"Authorization": "Bearer mocked-jwt-token"}

        # GET request
        response1 = client.get("/items/1", headers=headers)
        assert response1.status_code == 200

        # POST request
        payload = {"name": "test item", "price": 50.0}
        response2 = client.post("/items", json=payload, headers=headers)
        assert response2.status_code == 200

    def test_case_sensitive_token(self):
        """トークンが大文字小文字を区別することを確認"""
        headers = {"Authorization": "Bearer MOCKED-JWT-TOKEN"}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 401

    def test_bearer_scheme_case_insensitive(self):
        """Bearerスキームの大文字小文字を確認"""
        headers = {"Authorization": "bearer mocked-jwt-token"}
        response = client.get("/items/1", headers=headers)
        # FastAPIのHTTPBearerは通常大文字小文字を区別しないはず
        assert response.status_code == 200

    def test_authorization_header_with_extra_spaces(self):
        """Authorizationヘッダーに余分なスペースがある場合の動作を確認"""
        headers = {"Authorization": "Bearer  mocked-jwt-token"}
        response = client.get("/items/1", headers=headers)
        assert response.status_code == 401  # 余分なスペースは無効とみなされる


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_404_for_undefined_endpoint(self):
        """存在しないエンドポイントで404エラーが返ることを確認"""
        response = client.get("/undefined")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """許可されていないHTTPメソッドで405エラーが返ることを確認"""
        response = client.delete("/items/1")
        assert response.status_code == 405

    def test_invalid_content_type_for_post(self):
        """POSTエンドポイントで無効なContent-Typeを使用した場合のテスト"""
        headers = {
            "Authorization": "Bearer mocked-jwt-token",
            "Content-Type": "text/plain",
        }
        response = client.post("/items", content="invalid data", headers=headers)
        assert response.status_code == 422
