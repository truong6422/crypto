"""Module internationalization cho ứng dụng."""

import gettext
import os
from pathlib import Path
from typing import Optional

from .config import settings


class I18nManager:
    """Quản lý internationalization."""
    
    def __init__(self):
        self._translations = {}
        self._current_locale = settings.DEFAULT_LOCALE
        self._load_translations()
    
    def _load_translations(self):
        """Tải các file translation."""
        locale_path = Path(settings.LOCALE_PATH)
        
        for locale in settings.SUPPORTED_LOCALES:
            locale_dir = locale_path / locale / "LC_MESSAGES"
            mo_file = locale_dir / "messages.mo"
            
            if mo_file.exists():
                with open(mo_file, 'rb') as f:
                    self._translations[locale] = gettext.GNUTranslations(f)
    
    def set_locale(self, locale: str):
        """Thiết lập locale hiện tại."""
        if locale in settings.SUPPORTED_LOCALES:
            self._current_locale = locale
    
    def gettext(self, message: str) -> str:
        """Dịch message sang locale hiện tại."""
        if self._current_locale in self._translations:
            return self._translations[self._current_locale].gettext(message)
        return message
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Dịch message với số nhiều."""
        if self._current_locale in self._translations:
            return self._translations[self._current_locale].ngettext(singular, plural, n)
        return singular if n == 1 else plural


# Global i18n instance
i18n = I18nManager()


def gettext(message: str) -> str:
    """Helper function để dịch message."""
    return i18n.gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Helper function để dịch message với số nhiều."""
    return i18n.ngettext(singular, plural, n) 