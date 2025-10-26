from functools import cached_property
from pathlib import Path # for type annotations
from typing import Optional

import numpy as np
from loguru import logger
from numpy.typing import NDArray

"""
───────────────────────────────────────────────
English Explanation
───────────────────────────────────────────────
SentenceTransformer  
   - A class from the sentence-transformers library.
   - It is used to create embeddings (numerical vector representations) of sentences, paragraphs, or documents.
   - The embeddings are later stored in a vector database like Qdrant for semantic similarity search.
   - Example models: "all-MiniLM-L6-v2", "multi-qa-MiniLM-L6-cos-v1".

CrossEncoder  
   - A model that compares two pieces of text directly and predicts their relationship (similarity, entailment, ranking, etc.).
   - Unlike SentenceTransformer (which encodes each text separately), CrossEncoder jointly processes both texts for higher accuracy.
   - Useful for re-ranking retrieved documents or tweets in a RAG pipeline.

AutoTokenizer  
   - Comes from the transformers library (Hugging Face).
   - Automatically loads the correct tokenizer for any transformer model (BERT, RoBERTa, etc.).
   - It converts raw text into token IDs (numbers) that can be understood by the transformer model.

───────────────────────────────────────────────
توضیح فارسی
───────────────────────────────────────────────
SentenceTransformer  
   این کلاس برای تبدیل جمله‌ها یا پاراگراف‌ها به بردارهای عددی استفاده می‌شود تا بتوان مفهوم معنایی آن‌ها را با یکدیگر مقایسه کرد.  
   خروجی آن معمولاً در پایگاه داده‌ی برداری مثل کودرانت ذخیره می‌شود تا بتوان نزدیک‌ترین جمله‌ها را از نظر معنا پیدا کرد.

CrossEncoder  
   این مدل برای مقایسه‌ی مستقیم دو جمله یا متن به کار می‌رود تا میزان شباهت یا ارتباط آن‌ها را پیش‌بینی کند.  
   تفاوت آن با مدل قبلی در این است که هر دو جمله را هم‌زمان پردازش می‌کند و دقت بیشتری دارد.  
   معمولاً برای بازچینش یا بهبود نتایج جست‌وجوی معنایی در سیستم‌های راگ استفاده می‌شود.

AutoTokenizer  
   این ابزار متن خام را به شناسه‌های عددی تبدیل می‌کند تا مدل زبانی بتواند آن را بفهمد.  
   به صورت خودکار با هر مدل زبانی (مثل برت یا روبِرتا) سازگار است و در مرحله‌ی آماده‌سازی داده برای ترنسفورمرها کاربرد دارد.
───────────────────────────────────────────────
"""
from sentence_transformers.SentenceTransformer import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder
from transformers import AutoTokenizer

from llm_engineering.settings import settings


"""
    ───────────────────────────────────────────────
    English Explanation
    ───────────────────────────────────────────────
    A singleton-style wrapper for the SentenceTransformer model used to create text embeddings
    (vector representations of sentences, paragraphs, or documents).

    Purpose:
        - Ensures that the embedding model is loaded only once across the application to save memory and loading time.
        - Provides a clean interface to encode texts into dense embeddings.
        - Supports retrieving the embedding dimension automatically.
        - Configurable via environment settings (model name, device, and cache directory).

    Key Attributes:
        _model_id (str): Identifier for the pre-trained embedding model.
        device (str): Computation device, e.g., 'cpu' or 'cuda'.
        _model (SentenceTransformer): The actual transformer model instance.
    
    Example:
        >>> model = EmbeddingModelSingleton()
        >>> emb = model.encode(["AI changes everything", "Transformers are powerful"])
        >>> print(emb.shape)  # (2, 384) or (2, 768) depending on the model

    Notes:
        - The embeddings can be stored in a vector database (like Qdrant or FAISS) for semantic search and retrieval.
        - Typically used in RAG pipelines or document retrieval systems to match queries with semantically similar content.

    ───────────────────────────────────────────────
    توضیح فارسی
    ───────────────────────────────────────────────
    این کلاس یک پوسته رپر برای مدل سنتنسس_ترنسفرمر است که برای تبدیل جمله‌ها و متن‌ها
    به بردارهای عددی امبدینگ به کار می‌رود.

    هدف اصلی آن این است که مدل فقط یک‌بار در کل برنامه بارگذاری شود
    تا حافظه و زمان اجرا صرفه‌جویی شود.

    وظایف:
        - ایجاد و نگهداری مدل به صورت سنگلتون (فقط یک اینستنس در کل پروژه)
        - فراهم کردن متدی برای تبدیل متن به بردار عددی
        - استخراج خودکار اندازه‌ی بُعد امبدینگ
        - پشتیبانی از تنظیمات مدل، دیوایس، و مسیر کش از فایل ستنیگ

    مثال:
        >>> model = EmbeddingModelSingleton()
        >>> embedding = model.encode(["هوش مصنوعی آینده را تغییر می‌دهد"])
        >>> print(embedding.shape)  # (1, 384) یا (1, 768)

    نکات:
        - خروجی این کلاس معمولاً در پایگاه داده‌ی برداری مثل کیودرانت ذخیره می‌شود
          تا جست‌وجوی معنایی و سیستم‌های رگ بتوانند نزدیک‌ترین جملات را از نظر معنا پیدا کنند.
        - در پروژه‌های رگ به عنوان لایه‌ی امبدینگ استفاده می‌شود.
    ───────────────────────────────────────────────
"""
class EmbeddingModelSingleton:
    """Singleton wrapper for embedding models to avoid redundant loads."""

    def __init__(self,
                 model_id: str = settings.TEXT_EMBEDDING_MODEL_ID,
                 device: str = settings.RAG_MODEL_DEVICE,
                 cache_dir: Optional[Path] = None,
                 ) -> None:
        self._model_id = model_id
        self.device = device
        
        self._model = SentenceTransformer(
            self._model_id,
            device=self.device,
            cache_folder= str(cache_dir) if cache_dir else None
        )

        self._model.eval()  # Set the model to evaluation mode

       
    
    @property # Return the underlying model instance(like getter in Java or C#)
    def model_id(self) -> str:
        """
        Returns the identifier of the pre-trained transformer model to use.

        Returns:
            str: The identifier of the pre-trained transformer model to use.
        """
        return self._model_id
    
    
    
    @cached_property # Load once and cache
    def embedding_size(self) -> int:
        """
        Returns the dimensionality of the embeddings produced by the model.

        Returns:
            int: The dimensionality of the embeddings.
        """
        dummy_embedding = self._model.encode("")
        return dummy_embedding.shape[0] # e.g., 384 or 768 depending on the model
    
    
    
    @property
    def max_input_length(self) -> int:
        """
        Returns the maximum input length (in tokens) that the model can handle.

        Returns:
            int: The maximum input length in tokens.
        """
        return self._model.max_seq_length
    
    
    
    @property
    def tokenizer(self) -> AutoTokenizer:
        """
        Returns the tokenizer used to tokenize input text.

        Returns:
            AutoTokenizer: The tokenizer used to tokenize input text.
        """

        return self._model.tokenizer

    
    # Call method to encode texts into embeddings
    def __call__(self, input_txt: str | list[str], to_list:bool = True) -> NDArray[np.float32] | list[float] | list[list[float]]:
        """
        Generates embeddings for the input text using the pre-trained transformer model.

        Args:
            input_text (str): The input text to generate embeddings for.
            to_list (bool): Whether to return the embeddings as a list or numpy array. Defaults to True.

        Returns:
            Union[np.ndarray, list]: The embeddings generated for the input text.
        """
        try:
            # Generate embeddings.
            # using for (for example) calculating similarity later like cosine.
            embeddings = self._model.encode(input_txt)
        except Exception:
            logger.error("Failed to generate embeddings.")
            return [] if to_list else np.array([])
        
        # Convert to list if specified. 
        # It is useful for JSON serialization. and storage in some DBs.
        if to_list:
            embeddings = embeddings.tolist()
        return embeddings
    


class CrossEncoderModelSingleton:
    def _init_(
        self,
        model_id:str = settings.RERANKING_CROSS_ENCODER_MODEL_ID,
        device: str = settings.RAG_MODEL_DEVICE,
    ) -> None:
        """
        A singleton class that provides a pre-trained cross-encoder model for scoring pairs of input text.
        """
        self._model_id = model_id
        self.device = device

        self._model = CrossEncoder(
            self._model_id,
            device=self.device
        )
        self._model.eval()  # Set the model to evaluation mode

    def __call__(self, pairs: list[tuple[str, str]], to_list: bool = True) -> NDArray[np.float32] | list[float]:
        scores = self._model.predict(pairs)

        if to_list:
            scores = scores.tolist()

        return scores
    