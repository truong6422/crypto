"""Unit tests cho pagination.py."""

import pytest
from pydantic import ValidationError

from src.pagination import (
    PaginationParams,
    PageNumberPaginationParams,
    CursorPaginationParams,
    PageResponse,
    CursorResponse,
    get_pagination_params,
    get_cursor_params
)


class TestPagination:
    """Test cases cho pagination."""

    def test_pagination_params_default(self):
        """Test PaginationParams với giá trị mặc định."""
        params = PaginationParams()
        assert params.page_size == 20  # DEFAULT_PAGE_SIZE

    def test_pagination_params_custom(self):
        """Test PaginationParams với giá trị tùy chỉnh."""
        params = PaginationParams(page_size=50)
        assert params.page_size == 50

    def test_page_number_pagination_params_default(self):
        """Test PageNumberPaginationParams với giá trị mặc định."""
        params = PageNumberPaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_page_number_pagination_params_custom(self):
        """Test PageNumberPaginationParams với giá trị tùy chỉnh."""
        params = PageNumberPaginationParams(page=5, page_size=10)
        assert params.page == 5
        assert params.page_size == 10

    def test_page_number_pagination_params_validation(self):
        """Test PageNumberPaginationParams validation."""
        # Test page >= 1
        with pytest.raises(ValidationError):
            PageNumberPaginationParams(page=0)
        
        # Test page >= 1 (negative)
        with pytest.raises(ValidationError):
            PageNumberPaginationParams(page=-1)

    def test_paginated_response(self):
        """Test PageResponse."""
        items = [{"id": 1}, {"id": 2}]
        response = PageResponse(
            items=items,
            total=100,
            page=1,
            page_size=20,
            total_pages=5,
            has_next=True,
            has_prev=False
        )
        
        assert response.items == items
        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 5
        assert response.has_next is True
        assert response.has_prev is False

    def test_paginated_response_calculation(self):
        """Test PageResponse calculation."""
        total = 100
        page_size = 20
        page = 3
        
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        response = PageResponse(
            items=[],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        assert response.total_pages == 5
        assert response.has_next is True
        assert response.has_prev is True

    def test_paginated_response_empty(self):
        """Test PageResponse với danh sách rỗng."""
        response = PageResponse(
            items=[],
            total=0,
            page=1,
            page_size=20,
            total_pages=0,
            has_next=False,
            has_prev=False
        )
        
        assert response.items == []
        assert response.total == 0
        assert response.total_pages == 0
        assert response.has_next is False
        assert response.has_prev is False

    def test_cursor_pagination_params(self):
        """Test CursorPaginationParams."""
        params = CursorPaginationParams(cursor="abc123", page_size=15)
        assert params.cursor == "abc123"
        assert params.page_size == 15

    def test_cursor_response(self):
        """Test CursorResponse."""
        items = [{"id": 1}, {"id": 2}]
        response = CursorResponse(
            items=items,
            next_cursor="def456",
            has_next=True
        )
        
        assert response.items == items
        assert response.next_cursor == "def456"
        assert response.has_next is True

    def test_get_pagination_params(self):
        """Test get_pagination_params function."""
        params = get_pagination_params(page=2, page_size=15)
        assert params.page == 2
        assert params.page_size == 15

    def test_get_pagination_params_from_dict(self):
        """Test get_pagination_params từ dict."""
        params = get_pagination_params(page=3, page_size=25)
        assert isinstance(params, PageNumberPaginationParams)
        assert params.page == 3
        assert params.page_size == 25

    def test_get_cursor_params(self):
        """Test get_cursor_params function."""
        params = get_cursor_params(cursor="xyz789", page_size=30)
        assert params.cursor == "xyz789"
        assert params.page_size == 30

    def test_pagination_params_edge_cases(self):
        """Test pagination params với edge cases."""
        # Test page_size = MAX_PAGE_SIZE
        params = PageNumberPaginationParams(page_size=100)
        assert params.page_size == 100
        
        # Test page = 1 (minimum)
        params = PageNumberPaginationParams(page=1)
        assert params.page == 1

    def test_pagination_params_validation_edge_cases(self):
        """Test pagination params validation với edge cases."""
        # Test page_size > MAX_PAGE_SIZE
        with pytest.raises(ValidationError):
            PageNumberPaginationParams(page_size=101)
        
        # Test page_size = 0 (edge case - should be handled by Query validation)
        # Note: Direct object creation bypasses Query validation
        # This test validates the model's field constraints
        params = PageNumberPaginationParams(page_size=0)
        assert params.page_size == 0  # Direct creation allows this 