import uuid
from abc import ABC

from llm_engineering.domain import documents # abc is used to create abstract base classes
"""
This file imports three core typing utilities — TypeVar, Generic, and Type —  
which are used to build flexible, reusable, and type-safe class or function templates.  
They make your architecture dynamic without losing clarity or safety.

TypeVar:
    - Defines a type placeholder (like a generic "T") for flexibility.
    - It means “this function or class can handle any data type,  
      but once it starts with one type, it stays consistent.”
    - Example: A repository class that can work for both User and Post models.

Generic:
    - Used when you design a class that should support multiple types.
    - It allows writing one logic for all — e.g., Repository[User], Repository[Product].
    - Keeps the code DRY (Don’t Repeat Yourself) and modular.

Type:
    - Used when you need to receive a class itself instead of an object instance.
    - Example: def build(cls: Type): return cls() → dynamically creates a new instance.

Together:
These three form the backbone of type-safe generic programming in Python.  
They’re especially powerful in clean architectures (like Repositories, Pipelines, and DataLoaders),  
where the same logic must adapt to different data models without code duplication.


این سه ابزار برای ساخت کلاس‌ها و توابعی استفاده می‌شوند که قابل استفاده برای انواع داده‌ی مختلف هستند  
و در عین حال، از بروز خطاهای نوعی (تایپ ارور) جلوگیری می‌کنند و خوانایی کد را بالا می‌برند.

TypeVar:
    - یک متغیر نوعی (مثل تی) تعریف می‌کند تا نوع داده بعداً مشخص شود.  
      یعنی تابع یا کلاس می‌تواند با هر نوعی کار کند، اما در همان نوع باقی می‌ماند.

Generic:
    - برای کلاس‌هایی استفاده می‌شود که باید با چند نوع داده مختلف کار کنند.  
      مثلاً کلاس رپو که می‌تواند هم برای یوزر و هم پروداکت به کار رود.

Type:
    - وقتی لازم است خودِ کلاس را بگیری نه شیء ساخته‌شده از آن.  
      مثلاً زمانی که می‌خواهی به‌صورت پویا از روی کلاس، نمونه بسازی.

کاربرد عملی:
در پروژه‌هایی مثل ZenML یا LLM pipelines، از این مفاهیم استفاده می‌شود  
تا کلاس‌ها و استپ‌ها بتوانند با مدل‌های مختلف (مثل User، Comment، LinkedInProfile) کار کنند  
بدون آنکه منطق تکراری یا وابستگی خاصی ایجاد شود.
"""
from typing import Generic, Type, TypeVar

from loguru import logger
"""
پایدانتیک ابزاری است برای تعریف قالب داده‌ها به‌صورت دقیق و خودکار.
یعنی وقتی برای داده‌ها ساختار مشخص می‌کنی (مثلاً عدد، رشته یا فهرست)،
پایدانتیک بررسی می‌کند که داده‌های ورودی همان نوع باشند و اگر اشتباه باشند، خطا می‌دهد.

به‌طور خلاصه:
پایدانتیک باعث می‌شود داده‌های برنامه همیشه تمیز، معتبر و قابل اعتماد باشند.
"""
from pydantic import BaseModel, Field, UUID4
from pymongo import errors

from llm_engineering.settings import settings
from llm_engineering.infrastructure.db.mongo import connection
from llm_engineering.domain.exceptions import ImproperlyConfigured


_database = connection.get_database(settings.DATABASE_NAME)

T = TypeVar("T", bound="NoSQLBaseDocument") # bound is used to limit the types that can be used with this TypeVar
"""
این کلاس، الگوی اصلی تمام مدل‌های داده‌ی نوساختار است (مثل یوزر، پروفایل یا لینکدین دیتا).
نوع داده‌ی آن محدود به فرزندان (ارث بری از کلاس والد) خودش است، و با کمک پایدانتیک اعتبار داده‌ها را بررسی می‌کند
"""
class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    # id = uuid4() -> ID:UUID4-> showing type of id is UUID4, Field-> pydantic field function
    id: UUID4 = Field(default_factory=uuid.uuid4)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        
        return self.id == value.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """Convert "_id" (str object) into "id" (UUID object)."""
        if not data: 
            raise ValueError("Data is Empty")

        id = data.pop("_id") # pop is used to remove the key from dict and return its value
        return cls(**dict(id=uuid.UUID(id), **data)) # unpacking the dict and passing it to the class constructor
    
    def to_mongo(self:T, **kwargs) -> dict :    
        """**kwargs means any number of keyword arguments can be passed to the function."""
        """Convert "id" (UUID object) into "_id" (str object)."""
        """حذف فیلدهای تنظیم‌نشده و استفاده از نام مستعار برای فیلدها"""
        exclude_unset = kwargs.pop("exclude_unset", False) # exclude_unset is used to exclude fields that were not set
        by_alias = kwargs.pop("by_alias", True) # by_alias is used to exclude fields with alias

        # self.model_dump() -> pydantic method to convert model to dict
        """parsed means the data converted to mongo format"""
        parsed = self._model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id")) # convert UUID to str

        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)

        return parsed
    
    def _model_dump(self:T, **kwargs) -> dict:
        """Override pydantic's model_dump to convert "_id" back to "id"."""
        dict_ = super().model_dump(**kwargs) # call the parent class's model_dump method

        for key, value in dict_.items():
            """isistance is used instead of if type(value) == uuid.UUID"""
            if isinstance(value, uuid.UUID): # check if the value is of type UUID
                dict_[key] = str(value)

        return dict_
    
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "Document should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name
    
    def save(self:T, **kwargs) -> T | None:
        """Save the document to the database."""

        collection = _database[self.get_collection_name()]
        try:
            instance = collection.insert_one(self.to_mongo(**kwargs))

            return self
        except errors.WriteError:
            logger.exception("Failed to insert document.")

            return None
        
    @classmethod
    def get_or_create(cls:Type[T], **filter_options) -> T | None:
        collection = _database[cls.get_collection_name()]
        try:
            inctance = collection.find_one(filter_options)
            if inctance:
                return cls.from_mongo(inctance)
            else:
                new_instance = cls(**filter_options) # create a new instance with the filter options
                new_instance.save() # save the new instance to the database
                return new_instance
            
        except errors.OperationFailure:
            logger.exception(f"Failed to retrieve document with filter options: {filter_options}")
            raise

    @classmethod
    def bulk_insert(cls:Type[T], documents: list[T], **kwargs) -> bool:
        """Insert multiple documents into the database."""
        collection = _database[cls.get_collection_name()]
        try:
            collection.insert_many(doc.to_mongo(**kwargs) for doc in documents)
            return True
        except errors.BulkWriteError:
            logger.exception("Failed to bulk insert documents.")
            return False
        
    @classmethod
    def find(cls: Type[T], **filter_options) -> T | None:
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            return None
        except errors.OperationFailure:
            logger.error("Failed to retrieve document")

            return None

    @classmethod
    def bulk_find(cls: Type[T], **filter_options) -> list[T]:
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            return [document for instance in instances if (document := cls.from_mongo(instance)) is not None]
        
        except errors.OperationFailure:
            logger.error("Failed to retrieve documents")
            return []
  
