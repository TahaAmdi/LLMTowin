from abc import ABC
from typing import Optional

from sympy import O
"""
pydantic models for representing documents in the LLM engineering domain.
it is used to define the structure and validation of document-related data.
Also, it serves as a base for other document models.
این کتابخانه شامل مدل‌های پایدنتیک برای نمایش اسناد در حوزه مهندسی ال_ال_ام است.
از این برای تعریف ساختار و اعتبارسنجی داده‌های مرتبط با اسناد استفاده می‌شود.
همچنین، به عنوان پایه‌ای برای سایر مدل‌های سند عمل می‌کند.   
"""
from pydantic import UUID4, Field

from .base.nosql import NoSQLBaseDocument
from .types import DataCategory


class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    # class Settings is used to define configuration for the document model
    class Settings:
        name = "users"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    

class Document(NoSQLBaseDocument, ABC):
    content : dict
    platform : str
    author_id: UUID4 = Field(alias = "authorId")
    author_full_name: str = Field(alias = "author_full_name")


class RepositoryDocument(Document):
    name: str
    link: str

    class Settings:
        name = DataCategory.REPOSITORIES

    
class PostDocument(Document):
    image: Optional[str] = None
    link: str | None = None

    class Settings:
        name = DataCategory.POSTS


class ArticleDocument(Document):
    link: str

    class Settings:
        name = DataCategory.ARTICLES


    

