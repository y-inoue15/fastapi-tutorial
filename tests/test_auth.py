import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.auth import verify_token


class TestVerifyToken:
    """verify_token関数のテストクラス"""

    def test_verify_token_valid(self):
        """有効なトークンの場合、トークンを返すことを確認"""
        # 有効なトークン
        valid_token = "mocked-jwt-token"
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=valid_token
        )

        result = verify_token(credentials)
        assert result == valid_token

    def test_verify_token_invalid(self):
        """無効なトークンの場合、HTTPExceptionが発生することを確認"""
        # 無効なトークン
        invalid_token = "invalid-token"
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=invalid_token
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_verify_token_empty(self):
        """空のトークンの場合、HTTPExceptionが発生することを確認"""
        empty_token = ""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=empty_token
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_verify_token_whitespace_only(self):
        """空白のみのトークンの場合、HTTPExceptionが発生することを確認"""
        whitespace_token = "   "
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=whitespace_token
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_verify_token_different_case(self):
        """大文字小文字が異なるトークンの場合、HTTPExceptionが発生することを確認"""
        different_case_token = "MOCKED-JWT-TOKEN"
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=different_case_token
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
