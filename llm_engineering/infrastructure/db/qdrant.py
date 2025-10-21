"""
    A singleton connector class responsible for establishing and maintaining a single
    connection to the Qdrant vector database.  
    It automatically decides whether to connect to a local instance or the Qdrant Cloud,
    based on the settings configuration.

    If the connection is already established, it reuses the existing client instead
    of creating a new one — ensuring efficiency and consistency across the project.

    Attributes:
        _instance (QdrantClient | None): Holds the single shared instance of QdrantClient.

    Returns:
        QdrantClient: The connected Qdrant client ready for database operations.

        
    این کلاس وظیفه‌ی ایجاد و نگهداری یک اتصال پایدار (فقط یک‌بار) به پایگاه داده‌ی کیو_درانت را دارد.  
    خودش به‌صورت خودکار تشخیص می‌دهد که آیا باید به نسخه‌ی ابری وصل شود یا نسخه‌ی محلی،
    بر اساس تنظیمات پروژه.

    اگر اتصال قبلاً ساخته شده باشد، همان را دوباره استفاده می‌کند تا از ایجاد چند اتصال
    غیرضروری جلوگیری کند — این کار باعث صرفه‌جویی در حافظه، افزایش سرعت و ثبات در عملکرد می‌شود.

    ویژگی‌ها:
        _instance: تنها نسخه‌ی ساخته‌شده از کیو_درانت را نگه می‌دارد.

    خروجی:
        یک نمونه‌ی فعال از کیو_درانت که آماده‌ی انجام عملیات پایگاه داده است.
"""
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from llm_engineering.settings import settings


class QdrantDatabaseConnector:
    _instance: QdrantClient | None = None

    def __new__(cls, *args, **kwargs) -> QdrantClient:
        if cls._instance is None:
            try:
                if settings.USE_QDRANT_CLOUD:
                    cls._instance = QdrantClient(
                        url=settings.QDRANT_CLOUD_URL,
                        api_key=settings.QDRANT_APIKEY,
                    )

                    uri = settings.QDRANT_CLOUD_URL
                else:
                    cls._instance = QdrantClient(
                        host=settings.QDRANT_DATABASE_HOST,
                        port=settings.QDRANT_DATABASE_PORT,
                    )

                    uri = f"{settings.QDRANT_DATABASE_HOST}:{settings.QDRANT_DATABASE_PORT}"

                logger.info(f"Connection to Qdrant DB with URI successful: {uri}")
            except UnexpectedResponse:
                logger.exception(
                    "Couldn't connect to Qdrant.",
                    host=settings.QDRANT_DATABASE_HOST,
                    port=settings.QDRANT_DATABASE_PORT,
                    url=settings.QDRANT_CLOUD_URL,
                )

                raise

        return cls._instance


connection = QdrantDatabaseConnector()