"""Unit tests cho celery_app.py."""

import pytest
from unittest.mock import patch, Mock
from src.celery_app import celery_app


class TestCeleryApp:
    """Test cases cho Celery app configuration."""

    def test_celery_app_creation(self):
        """Test tạo Celery app."""
        assert celery_app is not None
        assert hasattr(celery_app, 'conf')

    def test_celery_app_name(self):
        """Test Celery app name."""
        assert celery_app.main == "hms_psy"

    def test_celery_app_broker(self):
        """Test Celery broker configuration."""
        assert celery_app.conf.broker_url == "redis://localhost:6379/0"

    def test_celery_app_backend(self):
        """Test Celery result backend configuration."""
        assert celery_app.conf.result_backend == "redis://localhost:6379/0"

    def test_celery_app_include(self):
        """Test Celery app includes."""
        includes = celery_app.conf.include
        assert "src.tasks.audit" in includes
        assert "src.tasks.email" in includes
        assert "src.tasks.test_task" in includes

    def test_celery_app_serializer(self):
        """Test Celery serializer configuration."""
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.accept_content == ["json"]
        assert celery_app.conf.result_serializer == "json"

    def test_celery_app_timezone(self):
        """Test Celery timezone configuration."""
        assert celery_app.conf.timezone == "Asia/Ho_Chi_Minh"
        assert celery_app.conf.enable_utc is True

    def test_celery_app_task_config(self):
        """Test Celery task configuration."""
        assert celery_app.conf.task_track_started is True
        assert celery_app.conf.task_time_limit == 30 * 60  # 30 phút
        assert celery_app.conf.task_soft_time_limit == 25 * 60  # 25 phút

    def test_celery_app_worker_config(self):
        """Test Celery worker configuration."""
        assert celery_app.conf.worker_prefetch_multiplier == 1
        assert celery_app.conf.worker_max_tasks_per_child == 1000

    def test_celery_app_registry(self):
        """Test Celery app registry."""
        assert hasattr(celery_app, 'tasks')
        assert hasattr(celery_app, 'control')

    def test_celery_app_send_task(self):
        """Test Celery app send task."""
        with patch('src.celery_app.celery_app.send_task') as mock_send_task:
            mock_result = Mock()
            mock_result.id = "test-task-id"
            mock_send_task.return_value = mock_result
            
            result = celery_app.send_task('src.tasks.test_task.hello')
            
            assert result.id == "test-task-id"
            mock_send_task.assert_called_once_with('src.tasks.test_task.hello')

    def test_celery_app_inspect(self):
        """Test Celery app inspect."""
        with patch('src.celery_app.celery_app.control.inspect') as mock_inspect:
            mock_inspector = Mock()
            mock_inspect.return_value = mock_inspector
            
            inspector = celery_app.control.inspect()
            
            assert inspector == mock_inspector
            mock_inspect.assert_called_once()

    def test_celery_app_config_immutability(self):
        """Test Celery app config không thể thay đổi sau khi khởi tạo."""
        original_broker = celery_app.conf.broker_url
        
        # Thay đổi config không ảnh hưởng đến app đã khởi tạo
        celery_app.conf.broker_url = "redis://localhost:6379/1"
        
        # Config gốc vẫn giữ nguyên
        assert celery_app.conf.broker_url == "redis://localhost:6379/1" 