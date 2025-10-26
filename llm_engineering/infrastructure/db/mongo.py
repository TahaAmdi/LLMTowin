"""
    A singleton connector class responsible for establishing and maintaining a single
    connection to the MongoDB vector database.  
    It automatically decides whether to connect to a local instance or the MongoDB Cloud,
    based on the settings configuration.

    If the connection is already established, it reuses the existing client instead
    of creating a new one — ensuring efficiency and consistency across the project.

    Attributes:
        _instance (MongoClient | None): Holds the single shared instance of MongoClient.

    Returns:
        MongoClient: The connected MongoDB client ready for database operations.

        
    این کلاس وظیفه‌ی ایجاد و نگهداری یک اتصال پایدار (فقط یک‌بار) به پایگاه داده‌ی مونگودیبی را دارد.  
    خودش به‌صورت خودکار تشخیص می‌دهد که آیا باید به نسخه‌ی ابری وصل شود یا نسخه‌ی محلی،
    بر اساس تنظیمات پروژه.

    اگر اتصال قبلاً ساخته شده باشد، همان را دوباره استفاده می‌کند تا از ایجاد چند اتصال
    غیرضروری جلوگیری کند — این کار باعث صرفه‌جویی در حافظه، افزایش سرعت و ثبات در عملکرد می‌شود.

    ویژگی‌ها:
        _instance: تنها نسخه‌ی ساخته‌شده از مونگودیبی را نگه می‌دارد.

    خروجی:
        یک نمونه‌ی فعال از مونگودیبی که آماده‌ی انجام عملیات پایگاه داده است.
"""
from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from llm_engineering.settings import settings


class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    def __new__(cls) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                logger.error(f"Couldn't connect to the database: {e!s}")

                raise

        logger.info(f"Connection to MongoDB with URI successful: {settings.DATABASE_HOST}")

        return cls._instance


connection = MongoDatabaseConnector()