from doctest import UnexpectedException
from gc import collect
import selectors
from tokenize import Ignore
import uuid
from uuid import UUID
from abc import ABC
from typing import Any, List, Optional, Callable, Generic, Type, TypeVar, Dict
from aiohttp import Payload
from attr import has
import numpy as np

from loguru import Record, logger
from pydantic import BaseModel, Field, UUID4 # pydantic is used for data validation and settings management

from qdrant_client.http import exceptions
from sympy import false, use

from llm_engineering.domain import documents
"""
EN — qdrant_client.http.models: Distance, VectorParams
------------------------------------------------------
- Distance: Enum defining the similarity metric used by a collection
  (e.g., COSINE, DOT, EUCLID).
- VectorParams: Schema for a collection’s vector settings such as:
  * size  -> embedding dimensionality (e.g., 384, 768, 1536)
  * distance -> which Distance metric to use

Typical use:
    from qdrant_client.http.models import Distance, VectorParams
    params = VectorParams(size=768, distance=Distance.COSINE)
    # pass params when creating a collection

FA — توضیح فارسی
----------------
- «فاصله»: نوع سنجهٔ شباهت که برای سنجش نزدیکی بردارها در یک مجموعه به کار می‌رود
  (مانند سنجهٔ کسینوسی، ضرب نقطه‌ای، یا اقلیدسی).
- «پارامترهای بردار»: تنظیمات اصلی یک مجموعه، شامل اندازهٔ بُعدِ بردار و سنجهٔ شباهت.
در عمل، نخست اندازهٔ بردار و سنجه انتخاب می‌شود و سپس این تنظیمات هنگام ساخت مجموعه
استفاده می‌گردد تا موتور جست‌وجوی برداری بداند چگونه شباهت را محاسبه کند.
"""
from qdrant_client.http.models import Distance, VectorParams
"""
EN — qdrant_client.models: PointStruct, CollectionInfo
------------------------------------------------------
- PointStruct: A single indexed item (point) consisting of:
  * id       -> unique identifier (int/str)
  * vector   -> the embedding list/array
  * payload  -> optional metadata dict (e.g., title, url, tags)
  Used when upserting/searching points.

- CollectionInfo: Introspection object with metadata about a collection
  (e.g., vector size, distance metric, number of points, status).
  Useful for validating that a collection was created/configured as expected.

Typical use:
    from qdrant_client.models import PointStruct, CollectionInfo
    point = PointStruct(id="doc-1", vector=vec, payload={"source": "blog"})
    # upsert point into a collection
    # later, fetch CollectionInfo to verify collection settings & counts

FA — توضیح فارسی
----------------
- «PointStruct»:
 نمایندهٔ یک موردِ فهرست‌ شده شامل شناسهٔ یکتا، بردارِ نگاشتی،
  و داده‌های کمکی دلخواه. برای ثبت، به‌روزرسانی یا جست‌وجوی موارد استفاده می‌شود.
- «CollectionInfo»:
 بازنماییِ وضعیت و ویژگی‌های یک مجموعه مانند اندازهٔ بُعد،
  سنجهٔ شباهت، شمارِ موارد و وضعیت عملیاتی. برای اطمینان از درست بودن پیکربندی
  و پایش مجموعه کاربرد دارد.
"""
from qdrant_client.models import PointStruct, CollectionInfo

from llm_engineering.application.networks.embeddings import EmbeddingModelSingleton
from llm_engineering.domain.exceptions import ImproperlyConfigured
from llm_engineering.domain.types import DataCategory
from llm_engineering.infrastructure.db.qdrant import connection

T = TypeVar('T', bound='VectorBaseDocument')

class VectorBaseDocument(ABC, Generic[T], BaseModel):
    """
    Abstract base class for vector-based document representations.
    Provides common properties and methods for handling vector embeddings.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.id == value.id
    def __hash__(self) -> int:
        return hash(self.id)
    
    @classmethod
    def from_record(cls: Type[T], point: Record) -> T:
        _id = UUID(point.id, version=4) # ensure UUID4. it means _id is UUID4 type
        payload = point.payload or {}

        attributres = {
            "id": _id,
            **payload,
        }
        if cls._has_class_attribute("embedding"):
            attributres["embedding"] = point.vector or None

        return cls(**attributres)
    

    def to_point(self: T, **kwargs) -> PointStruct:
        exclude_unset = kwargs.pop("exclude_unset", False)
        by_alias = kwargs.pop("by_alias", True)

        payload = self.model_dump(exclude_unset=exclude_unset, by_alias=by_alias)

        _id = str(payload.pop("id"))
        vector = payload.pop("embedding", None) # using vector to store embedding
        if vector and isinstance(vector, np.ndarray):
            vector = vector.tolist()
            """
            Ensure the vector is a list for PointStruct
            Qdrant expects vectors as lists, not numpy arrays
            PointStruct requires id, vector, payload arguments
            """
        return PointStruct(id=_id, vector=vector, payload=payload)
    

    def model_dump(self: T, **kwargs) -> dict:
        # model_dump is pydantic's method to convert model to dict
        dict_ = super().model_dump(**kwargs)

        dict_ = self._uuid_to_str(dict_)
        return dict_
    

    def _uuid_to_str(self: T, item: Any) -> Any:
        if isinstance(item, UUID):
            return str(item)
        
        if isinstance(item, dict):
            return {key: self._uuid_to_str(value) for key, value in item.items()}
        
        if isinstance(item, list):
            return [self._uuid_to_str(v) for v in item]

        return item
    
    @classmethod
    def bulk_insert(cls: Type[T], documents:List["VectorBaseDocument"]) -> bool:
        try:
            cls._bulk_insert(documents)
            
        except exceptions.UnexpectedResponse:
            logger.info(
                f"Collection '{cls.get_collection_name()}' does not exist. Trying to create the collection and reinsert the documents."
            )

            cls.create_collection()

            try:
                cls._bulk_insert(documents)
            except exceptions.UnexpectedResponse as e:
                logger.error(f"Failed to insert documents in '{cls.get_collection_name()}'.")

                return False

        return True


    @classmethod
    def _bulk_insert(cls: Type[T], documents:List["VectorBaseDocument"]) -> None:
            # doc is VectorBaseDocument and forward to_point method AUTOMATICALLY
            points = [doc.to_point() for doc in documents]
            
            # Upsert points into the collection.
            # collection_name determines where should function begin to search in DB
            connection.upsert(
                collection_name=cls.get_collection_name(),
                points=points,
            )

    @classmethod
    def bulk_find(cls:Type[T], limit: int = 10, **kwargs) -> tuple[list[T], UUID|None]:
        try
            documents, next_offset = cls._bulk_find(limit=limit, **kwargs)
        except exceptions.UnexpectedResponse:
            logger.error(f"Failed to search documents in '{cls.get_collection_name()}'.")

            documents, next_offset = [], None

        return documents, next_offset


    @classmethod
    def _bulk_find(cls:Type[T], limit: int = 10, **kwargs) -> tuple[list[T], UUID|None]:
        """ 
    Fetches a paginated batch of records from the Qdrant collection 
    associated with this class.

    This is a classmethod, meaning it's called on the class (e.g., User.find()) 
    and not an instance. It uses Qdrant's `scroll` method for efficient, 
    stable pagination using an ID-based offset, not a numeric one.

    Args:
        cls (Type[T]): The class being queried (e.g., User).
        limit (int): The maximum number of records to return. Defaults to 10.
        **kwargs: A flexible set of keyword arguments that can contain
            both FILTERS and OPTIONS for the query.

            FILTERS:
            Any keyword argument that is NOT one of the options below will
            be passed directly to `connection.scroll()` as a filter.
            Example: `category="tech"` or `author="David"`

            OPTIONS (These are input arguments, NOT data in your database):
            - "offset" (UUID | None): The "bookmark" ID from which to
              start the scroll. This is the `next_offset` returned from
              a previous call. If None, scrolling starts from the beginning.
            - "with_payload" (bool): Input argument passed to `scroll()`.
              If True (default), returns the full data payload.
            - "with_vectors" (bool): Input argument passed to `scroll()`.
              If False (default), does not return the heavy vector data,
              which is a major performance optimization.

    Returns:
        tuple[list[T], UUID | None]:
            - [0]: A list of records found (as class instances).
            - [1]: The `next_offset` (a UUID), which is the bookmark for
              fetching the next page. Returns None if this is the last page.
        """
    
        """    
    یک دسته صفحه بندی شده از رکوردها را از مجموعه کدرنت
    (Qdrant) مرتبط با این کلاس واکشی می‌کند.

    این یک متد کلاس است، یعنی روی خود کلاس (مانند: کاربر.پیداکردن) صدا
    زده می‌شود، نه روی یک نمونه ساخته شده. این تابع از متد «پیمایش»
    (scroll) در کدرنت برای صفحه بندی بهینه و پایدار استفاده می‌کند.

    ورودی‌ها:
        cls (Type[T]): کلاسی که از آن پرس‌وجو می‌شود (مانند: کاربر).
        limit (int): بیشترین تعداد رکوردهای بازگشتی. پیش‌فرض ۱۰ است.
        **kwargs: مجموعه‌ای انعطاف‌پذیر از آرگومان‌های کلیدواژه‌ای که
            می‌تواند شامل «پالایه‌ها» (فیلترها) و «گزینه‌ها» برای پرس‌وجو باشد.

            پالایه‌ها:
            هر آرگومانی که جزو گزینه‌های پایین نباشد، مستقیماً به عنوان
            پالایه به تابع «پیمایش» ارسال می‌شود.
            نمونه: `category="فنی"` یا `author="داوود"`

            گزینه‌ها (اینها آرگومان‌های ورودی هستند، نه داده‌های درون پایگاه داده):
            - "offset" (شناسه یا هیچی): این یک «نشانک» یا شناسه است
              که پیمایش از آنجا شروع می‌شود. این همان «نشانک بعدی» است
              که از فراخوانی قبلی بازگشته است. اگر «هیچی» (None) باشد،
              پیمایش از ابتدا شروع می‌شود.
            - "with_payload" (بله/خیر): یک آرگومان ورودی برای «پیمایش».
              اگر «بله» (پیش‌فرض) باشد، خود داده‌های اصلی را برمی‌گرداند.
            - "with_vectors" (بله/خیر): یک آرگومان ورودی برای «پیمایش».
              اگر «خیر» (پیش‌فرض) باشد، داده‌های سنگین برداری را برنمی‌گرداند
              که باعث بهینه‌سازی بزرگ در سرعت می‌شود.

    مقدار بازگشتی:
        یک چندتایی (tuple) شامل دو بخش:
            - [۰]: لیستی از رکوردهای پیدا شده (به عنوان نمونه‌های کلاس).
            - [۱]: «نشانک بعدی» (یک شناسه)، که برای گرفتن صفحه بعدی
              استفاده می‌شود. اگر صفحه آخر باشد، «هیچی» (None) برمی‌گرداند.
        """
        collection_name = cls.get_collection_name()

        offset = kwargs.pop("offset", None) # offset comes from qdrant as str or None
        offset = str(offset) if offset else None

        records, next_offset = connection.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload = kwargs.pop("with_payload", True),
            with_vectors = kwargs.pop("with_vectors", false),
            offset=offset,
            **kwargs
        )

        documents = [cls.from_record(record) for record in records]
        if next_offset is not None:
            next_offset = UUID(next_offset, version=4)

        return documents, next_offset
    
    @classmethod
    def search(cls:Type[T], query_vector:List[float], limit:int=10, **kwargs) -> list[T]:
        """ 
        Searches for the most similar documents in the Qdrant collection
        based on the provided query vector.

        This is a classmethod, meaning it's called on the class (e.g., User.search())
        and not an instance. It uses Qdrant's `search` method to find the top-N
        most similar vectors to the input query vector.

        Args:
            cls (Type[T]): The class being queried (e.g., User).
            query_vector (List[float]): The embedding vector to search against.
            limit (int): The maximum number of similar documents to return. Defaults to 10.
            **kwargs: Additional keyword arguments passed directly to the `search()` method.

        Returns:
            list[T]: A list of the most similar documents found, as class instances.
        """
        try:
            documents = cls._search(query_vector=query_vector, limit=limit, **kwargs)
        except exceptions.UnexpectedResponse:
            logger.error(f"Failed to search documents in '{cls.get_collection_name()}'.")

            documents = []
        
        return documents
    
    @classmethod
    def _search(cls:Type[T], query_vector:List[float], limit:int=10, **kwargs) -> list[T]:
        collection_name = cls.get_collection_name()

        records = connection.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=kwargs.pop("with_payload", True),
            with_vectors=kwargs.pop("with_vectors", False),
            **kwargs
        )
        documents = [cls.from_record(record) for record in records]

        return documents
    
    @classmethod
    def get_or_create_collection(cls: Type[T]) -> CollectionInfo:
        """        
        Idempotent method to get or create a Qdrant collection.

        This function first attempts to get the collection by the name
        provided by `cls.get_collection_name()`. If it exists, it returns
        the collection info immediately.
        
        If it fails with an `UnexpectedResponse` (signaling that the
        collection does not exist), it calls the internal `_create_collection`
        method to build it, using the class's specific vector configuration.
        
        After ensuring the collection is created, it calls `get_collection`
        a second time to safely return the definitive collection info.

        Returns:
            CollectionInfo: The info of the retrieved or newly created collection.
        """
        
        """        
        تابع اصلی برای «دریافت یا ایجاد» کالکشن.

        این متد هوشمند، ابتدا تلاش می‌کند تا کالکشن را با نامی که از
        `get_collection_name` کلاس می‌گیرد، دریافت کند.
        
        اگر کالکشن وجود داشته باشد، همان را برمی‌گرداند.
        
        اگر وجود نداشته باشد (و خطای `UnexpectedResponse` رخ دهد)،
        به صورت خودکار متد `_create_collection` را صدا می‌زند تا آن را
        بسازد. پس از اطمینان از ساخت، کالکشن را دوباره دریافت کرده
        و اطلاعات آن را برمی‌گرداند.

        این تابع تضمین می‌کند که در پایان عملیات، کالکشن مورد نظر
        حتماً وجود دارد و اطلاعات آن (CollectionInfo) در دسترس است.
        
        بازگشت:
            CollectionInfo: اطلاعات کالکشن دریافت شده یا تازه ایجاد شده.
        """
        collection_name = cls.get_collection_name()

        try:
            return connection.get_collection(collection_name=collection_name)
        except exceptions.UnexpectedResponse:
            use_vector_index = cls.get_use_vector_index()

            collection_created = cls._create_collection(
                collection_name=collection_name, use_vector_index=use_vector_index
            )
            if collection_created is False:
                raise RuntimeError(f"Couldn't create collection {collection_name}") from None

            return connection.get_collection(collection_name=collection_name)

    @classmethod
    def create_collection(cls: Type[T]) -> bool:
        """        
        A public convenience method to manually trigger collection creation.

        It retrieves the necessary configuration (collection name and
        vector index settings) from the class (`cls`) and passes them to the
        internal `_create_collection` method to perform the actual creation.

        Returns:
            bool: The result of the creation operation from the connection.
        """
        
        """        
        یک متد عمومی راحت برای «ایجاد دستی» کالکشن.

        این تابع اطلاعات مورد نیاز (نام کالکشن و تنظیمات استفاده از
        وکتور) را از خود کلاس (`cls`) دریافت کرده و سپس متد داخلی
        `_create_collection` را برای انجام کار واقعی صدا می‌زند.

        بازگشت:
            bool: نتیجه عملیات ساخت کالکشن (معمولاً True).
        """
        collection_name = cls.get_collection_name()
        use_vector_index = cls.get_use_vector_index()

        return cls._create_collection(collection_name=collection_name, use_vector_index=use_vector_index)

    @classmethod
    def _create_collection(cls, collection_name: str, use_vector_index: bool = True) -> bool:
        """        
        The internal "worker" method that performs the actual creation of
        the collection in Qdrant.

        If `use_vector_index` is True, it configures the `VectorParams`
        using the size from the `EmbeddingModelSingleton` and `COSINE`
        distance. If False, it passes an empty config.

        Args:
            collection_name (str): The name for the new collection.
            use_vector_index (bool): Flag to determine if vector indexing
                                     should be configured.

        Returns:
            bool: The result of the creation operation.
        """
        
        """        
        متد داخلی و «سازنده» اصلی کالکشن در کیودرنت.

        این تابع مستقیماً `connection.create_collection` را صدا می‌زند. اگر
        `use_vector_index` برابر `True` باشد، تنظیمات برداری (مانند اندازه
        بردار و نوع فاصله) را بر اساس مدل امبدینگ (EmbeddingModelSingleton)
        پیکربندی کرده و ارسال می‌کند.

        آرگومان‌ها:
            collection_name (str): نام کالکشنی که باید ساخته شود.
            use_vector_index (bool): آیا این کالکشن باید برای جستجوی برداری
                                    پیکربندی شود یا خیر.

        بازگشت:
            bool: نتیجه عملیات ساخت کالکشن (معمولاً True).
        """
        if use_vector_index is True:
            vectors_config = VectorParams(size=EmbeddingModelSingleton().embedding_size, distance=Distance.COSINE)
        else:
            vectors_config = {}

        return connection.create_collection(collection_name=collection_name, vectors_config=vectors_config)
    
    @classmethod
    def get_category(cls:Type[T]) -> DataCategory:
        if not hasattr(cls, "Config") or not hasattr(cls.Config, "category"):
            raise ImproperlyConfigured(
                "The class should define a Config class with"
                "the 'category' property that reflects the collection's data category."
            )
        return cls.Config.category
    
    @classmethod
    def get_collection_name(cls:Type[T]) -> str:
        if not hasattr(cls, "Config") or not hasattr(cls.Config, "name"):
            raise ImproperlyConfigured(
                "The class should define a Config class with"
                "the 'name' property that reflects the collection name."
            )
        return cls.Config.name
    
    @classmethod
    def get_use_vector_index(cls:Type[T]) -> bool:
        if not hasattr(cls, "Config") or not hasattr(cls.Config, "use_vector_index"):
            raise ImproperlyConfigured(
                "The class should define a Config class with"
                "the 'use_vector_index' property that indicates"
                "whether to use vector indexing for the collection."
            )
        return cls.Config.use_vector_index  
    
    @classmethod
    def grou_by_class(
        cls:Type["VectorBaseDocument"], documents:List["VectorBaseDocument"]
    ) -> Dict[Type["VectorBaseDocument"], List["VectorBaseDocument"]]:
        """        
        Public convenience method to group documents by their actual Python class.

        This is useful for separating different types of documents 
        (e.g., UserDocument from ArticleDocument) that might be mixed 
        in the same list.
        
        It calls the `_group_by` engine, passing a selector that uses 
        `doc.__class__` to get the class type as the key.

        Args:
            documents: The list of document instances to group.

        Returns:
            A dictionary grouped by class type (e.g., 
            {UserDocument: [...], ArticleDocument: [...]}).
        """
        
        """        
        متد عمومی و راحت برای دسته‌بندی اسناد بر اساس 
        «نوع کلاس پایتون».

        این تابع برای جداسازی انواع مختلف اسناد (مانند اسناد کاربر
        از اسناد مقاله) که ممکن است در یک لیست مخلوط باشند، مفید است.
        
        این تابع موتور «گروه‌بندی» داخلی را صدا می‌زند و به عنوان قانون، دستور
        «کلاسِ سازنده سند» 
        (`doc.__class__`)
          را برای استخراج 
        کلید دسته‌بندی ارسال می‌کند.

        ورودی‌ها:
            documents: لیست اسنادی که باید دسته‌بندی شوند.

        بازگشت:
            یک دیکشنری که بر اساس نوع کلاس گروه‌بندی شده است (مانند:
            {کلاس_کاربر: [...]، کلاس_مقاله: [...]}).
        """
        return cls._group_by(documents, selectors=lambda doc: doc.__class__)
    
    @classmethod
    def group_by_category(
        cls:Type[T], documents:List["VectorBaseDocument"]
    ) -> Dict[DataCategory, List[T]]:
        """        
        Public convenience method to group documents by their `DataCategory`.

        This category is typically defined in the document's inner `Config`
        class and retrieved via the `get_category()` method.
        
        It calls the `_group_by` engine, passing a selector that uses 
        `doc.get_category()` to determine the key.

        Args:
            documents: The list of document instances to group.

        Returns:
            A dictionary grouped by `DataCategory` (e.g., 
            {DataCategory.USER: [...], DataCategory.ARTICLE: [...]}).
        """
        
        """        
        متد عمومی و راحت برای دسته‌بندی اسناد بر اساس «دسته‌بندی داده».

        این دسته‌بندی معمولاً در کلاس داخلی «کانفیگ» هر سند تعریف شده
        و از طریق متد «گت_کتگوری» قابل دسترسی است.
        
        این تابع موتور «گروه‌بندی» داخلی را صدا می‌زند و به عنوان قانون،
        دستور «گرفتن دسته‌بندی سند» (`doc.get_category()`) را برای
        استخراج کلید دسته‌بندی ارسال می‌کند.

        ورودی‌ها:
            documents: لیست اسنادی که باید دسته‌بندی شوند.

        بازگشت:
            یک دیکشنری که بر اساس «دسته‌بندی داده» گروه‌بندی شده است.
        """
        return cls._group_by(documents, selectors=lambda doc: doc.get_category())
    
    @classmethod
    def _group_by(cls: Type[T], documents: list[T], selector: Callable[[T], Any]) -> Dict[Any, list[T]]:
        """        
        The internal, generic grouping engine.

        This method iterates over a list of documents and groups them into
        a dictionary. The grouping key for each document is determined by
        executing the provided `selector` function on it.

        Args:
            documents: A list of documents (or any items) to be grouped.
            selector (Callable): A function (like a lambda) that takes one
                document as input and returns the key to group by.

        Returns:
            A dictionary where keys are the extracted keys (e.g., categories
            or class types) and values are lists of documents matching that key.
        """
        
        """        
        موتور داخلی و عمومی برای گروه‌بندی.

        این متد لیستی از اسناد را می‌گیرد و آن‌ها را در یک دیکشنری
        دسته‌بندی می‌کند. «کلید» دسته‌بندی برای هر سند، توسط اجرای
        تابع «انتخاب‌گر» بر روی آن سند مشخص می‌شود.

        ورودی‌ها:
            documents: لیستی از اسناد (یا هر آیتمی) برای دسته‌بندی.
            selector (Callable): یک تابع (مانند لامبدا) که یک سند
                به عنوان ورودی می‌گیرد و «کلید» دسته‌بندی را برمی‌گرداند.

        بازگشت:
            یک دیکشنری که کلیدهای آن، کلیدهای استخراج‌شده (مانند
            دسته‌بندی‌ها یا نوع کلاس‌ها) و مقادیر آن، لیست اسناد
            مطابق با همان کلید هستند.
        """
        grouped = {}
        for doc in documents:
            key = selector(doc)

            if key not in grouped:
                grouped[key] = []
            grouped[key].append(doc)

        return grouped
    
    @classmethod
    def collection_name_to_class(cls: Type["VectorBaseDocument"], collection_name: str) -> type["VectorBaseDocument"]:
        for subclass in cls.__subclasses__():
            try:
                if subclass.get_collection_name() == collection_name:
                    return subclass
            except ImproperlyConfigured:
                pass

            try:
                return subclass.collection_name_to_class(collection_name)
            except ValueError:
                continue

        raise ValueError(f"No subclass found for collection name: {collection_name}")

    @classmethod
    def _has_class_attribute(cls: Type[T], attribute_name: str) -> bool:
        if attribute_name in cls.__annotations__:
            return True

        for base in cls.__bases__:
            if hasattr(base, "_has_class_attribute") and base._has_class_attribute(attribute_name):
                return True

        return False
        