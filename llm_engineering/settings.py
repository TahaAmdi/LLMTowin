from turtle import st
from loguru import logger
"""
این کتابخانه برای مدیریت تنظیمات پروژه استفاده می‌شود.
به‌صورت خودکار مقدار متغیرهای محیطی مثل آدرس پایگاه‌داده، کلید دسترسی و رمزها را می‌خواند
و آن‌ها را در قالب یک مدل داده‌ای ساخت‌یافته و قابل کنترل قرار می‌دهد.
به این ترتیب نیازی نیست تنظیمات را دستی تعریف یا از فایل‌های جداگانه بخوانی؛
همه‌چیز مرتب، ایمن و یک‌جا مدیریت می‌شود    
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from zenml.client import Client
from zenml.exceptions import EntityExistsError

class Settings(BaseSettings):
    # SettingsConfigDict is used to configure pydantic settings behavior,
    # such as specifying an environment file to load variables from.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# --- Required settings even when working locally. ---

    #OpenAI API.
    OPENAI_MODEL_ID: str = "gpt-40-mini"
    # OpenAI API key for accessing OpenAI services.
    OPENAI_API_KEY: str | None = None

    #HuggingFace API.
    HUGGINGFACE_API_KEY: str | None = None

    #Comet ML (during training).
    # Comet ML is used for experiment tracking and model monitoring.
    COMET_API_KEY: str | None = None
    COMET_PROJECT_NAME: str = "twin"

    # --- Required settings when deploying the code. ---
    # --- Otherwise, default values values work fine. ---

    #MongoDB database settings.
    DATABASE_HOST: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "twin"

    #Qdrant vector database settings.
    USE_QDRANT_CLOUD: bool = False                  # Whether to use Qdrant Cloud or local instance.
    QDRANT_DATABASE_HOST: str = "localhost"         # Hostname for local Qdrant instance.
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"                   # URL for local or cloud Qdrant instance.
    QDRANT_APIKEY: str | None = None                # API key for local or cloud Qdrant instance.

    # AWS Authentication.
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    # --- Optional settings used to tweak the code. ---

    #AWS SageMaker settings.
    HF_MODEL_ID: str = "mlabonne/TwinLlama-3.1-8B-DPO"   # HuggingFace model ID for SageMaker deployment.
    GPU_INSTANCE_TYPE: str = "ml.g5.2xlarge"             # GPU instance type for SageMaker deployment.
    SM_NUM_GPUS: int = 1                                 # Number of GPUs for SageMaker instance.
    MAX_INPUT_LENGTH: int = 2048                         # Maximum input length for the model.
    MAX_TOTAL_TOKENS: int = 4096                         # Maximum total tokens (input + output).
    COPIES: int = 1                                      # Number of model copies to deploy.
    GPUS: int = 1                                        # Number of GPUs to use.
    CPUS: int = 2                                        # Number of CPUs to use.

    """ ____________AWS SageMaker inference settings_____________. 
Temperature, Top-p, and Max New Tokens — Generation Controls
-------------------------------------------------------------

English Explanation:
These parameters control the creativity, determinism, and length of generated text.
- temperature: Controls randomness. Lower = more focused and factual; higher = more creative and diverse.
- top_p: Limits the cumulative probability of token sampling. A smaller value restricts choices to the most likely words.
- max_new_tokens: Defines the maximum number of tokens the model can generate in one response.

Example:
For temperature=0.01, top_p=0.9, max_new_tokens=150:
→ The model produces logical, precise, and extended answers — ideal for technical or analytical contexts.

-------------------------------------------------------------

توضيح فارسي:
اين سه پارامتر ميزان خلاق بودن، قابل پيش‌بيني بودن و طول پاسخ مدل زباني را تعيين مي‌كنند.
- دما (temperature): ميزان تصادفي بودن توليد را مشخص مي‌كند. عدد كم‌تر يعني پاسخ منطقي‌تر و علمي‌تر، عدد بالاتر يعني پاسخ خلاقانه‌تر و غيرقابل پيش‌بيني‌تر.
- احتمال برش (top_p): محدوده‌ي احتمالات انتخاب واژه‌ها را تعيين مي‌كند. هرچه كم‌تر باشد، مدل فقط از بين واژه‌هاي معقول‌تر انتخاب مي‌كند.
- حداكثر توكن جديد (max_new_tokens): حداكثر تعداد واژه‌هايي كه مدل در يك پاسخ توليد مي‌كند را مشخص مي‌كند.

نمونه:
وقتي دما ۰٫۰۱، احتمال برش ۰٫۹ و حداكثر توكن ۱۵۰ باشد،
مدل پاسخي دقيق، منطقي و نسبتاً طولاني توليد مي‌كند كه براي متن‌هاي فني و تحليلي مناسب است.

    """
    SAGEMAKER_ENDPOINT_CONFIG_INFERENCE: str = "twin"    # It is the SageMaker endpoint configuration name for inference.
    SAGEMAKER_ENDPOINT_INFERENCE: str = "twin"           # It is the SageMaker endpoint name for inference.
    
    TEMPERATURE_INFERENCE: float = 0.01                  # Temperature setting for inference. It controls randomness means of output.
                                                         # Higher values like 0.8 will make the output more random,
                                                         # while lower values like 0.2 will make it more focused and deterministic.
    
    TOP_P_INFERENCE: float = 0.9                         # Top-p (nucleus) sampling parameter for inference.
                                                         # It considers the smallest set of tokens whose cumulative probability
                                                         # exceeds the threshold p. This helps in generating more coherent and contextually relevant text.
    
    MAX_NEW_TOKENS_INFERENCE: int = 150                  # Maximum new tokens to generate during inference.

    """
RAG (Retrieval-Augmented Generation) Configuration
--------------------------------------------------

English Explanation:
These settings define the models and device used for the RAG pipeline.
RAG enhances an LLM by combining retrieval and generation — first fetching
relevant context from a vector database (e.g., Qdrant), then generating
an informed and grounded response.

- TEXT_EMBEDDING_MODEL_ID: The embedding model used to convert text into vectors for similarity search.
- RERANKING_CROSS_ENCODER_MODEL_ID: A re-ranking model that scores and orders retrieved documents.
- RAG_MODEL_DEVICE: The hardware used for inference, usually "cpu" or "cuda".

Example Flow:
Query → Embedding → Retrieve top matches → Re-rank → Inject into LLM prompt → Generate answer.

--------------------------------------------------

توضيح فارسي:
اين تنظيمات مربوط به سامانه‌ي توليد تقويت‌شده با بازيابي است (RAG).
در اين روش، مدل زباني ابتدا داده‌هاي مرتبط را از پايگاه برداري (مانند Qdrant) جست‌وجو مي‌كند
و سپس با استفاده از آن داده‌ها پاسخ آگاهانه و مبتني بر حقيقت توليد مي‌كند.

- شناسه‌ي مدل تبديل متن به بردار (TEXT_EMBEDDING_MODEL_ID): مدلي كه جملات را به بردارهاي عددي تبديل مي‌كند تا بتوان شباهت ميان آن‌ها را سنجيد.
- شناسه‌ي مدل بازچيني (RERANKING_CROSS_ENCODER_MODEL_ID): مدلي كه پس از بازيابي داده‌ها، نتايج را براساس ارتباط دقيق‌تر مرتب مي‌كند.
- سخت‌افزار اجرا (RAG_MODEL_DEVICE): تعيين مي‌كند اجراي مدل روي پردازنده‌ي مركزي يا گرافيكي انجام شود.

نمونه‌ي فرايند:
پرسش ← تبديل به بردار ← بازيابي داده‌هاي مشابه ← بازچيني ← تزريق به مدل زباني ← توليد پاسخ
"""
    # RAG
    TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"

    # LinkedIn Credentials
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None

    """
💡 @property
----------------------------------------
EN:
@property is used to define a method that behaves like an attribute.
It allows you to calculate or retrieve values dynamically
without calling the method with parentheses.

FA:
@property برای زمانی است که می‌خواهیم یک تابع مانند یک ویژگی (attribute)
رفتار کند. یعنی بدون پرانتز صدا زده شود ولی در واقع پشت صحنه محاسبه انجام ‌شود.
این رویکرد برای ویژگی‌هایی مفید است که مقدارشان از روی داده‌های دیگر به‌صورت لحظه‌ای محاسبه می‌شود.

💡 @classmethod
----------------------------------------
EN:
@classmethod defines a method that works on the class itself, not on an instance.
It receives 'cls' instead of 'self' and is used when you need to access or modify
class-level data shared across all instances.

FA:
@classmethod برای تعریف متدی استفاده می‌شود که بر روی خود کلاس عمل می‌کند،
نه بر روی یک نمونه خاص از آن. به‌جای self، پارامتر cls را می‌گیرد
و زمانی کاربرد دارد که بخواهیم داده یا رفتار سطح کلاس را مدیریت کنیم
(مثل شمارنده‌ها، ساخت اشیاء از داده‌های خاص، یا متدهای کارخانه‌ای).

💡 @staticmethod
----------------------------------------
EN:
@staticmethod defines a method that doesn't depend on class or instance state.
It’s just a utility function placed inside a class for organizational purposes.

FA:
@staticmethod برای زمانی است که متد نیازی به هیچ داده‌ای از کلاس یا شیء ندارد.
صرفاً یک تابع کمکی است که به‌صورت منطقی به کلاس مربوط می‌شود،
اما مستقل از وضعیت کلاس یا نمونه عمل می‌کند.
    """ 
    @property
    def OPEN_MAX_TOKEN_WINDOW(self) -> int: # Returns the maximum token window for the specified OpenAI model.
        official_max_token_window = {
            "gpt-3.5-turbo": 16385,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }.get(self.OPENAI_MODEL_ID, 128000)

        max_token_window = int(official_max_token_window * 0.90)  # Use 90% of the official limit as a buffer.

        return max_token_window
    
    """
    Loads configuration settings securely from the ZenML secret store.

    This method attempts to retrieve sensitive configuration values (e.g., API keys,
    database URIs, and authentication tokens) stored in ZenML’s secret management system.
    If the secret store is unavailable or missing, it falls back to default local
    settings, ensuring that the program can still run with safe defaults.

    Returns:
        Settings: The initialized settings object containing environment configuration.
    """

    """
    این متد تنظیمات پروژه را به‌صورت ایمن از فضای ذخیره‌سازی محرمانه‌ی ذن_مل بارگذاری می‌کند.

    در ابتدا تلاش می‌کند داده‌های حساس مانند کلیدهای دسترسی، آدرس پایگاه‌داده یا توکن‌ها را 
    از بخش نگهداری رمز ذن_مل بخواند و در قالب یک شیء از کلاس ستینگ بازگرداند.  
    اگر ذن_مل در دسترس نباشد یا داده‌ای پیدا نکند، از تنظیمات پیش‌فرض محلی استفاده می‌شود  
    تا اجرای پروژه بدون خطا ادامه یابد.

    خروجی:
        شیء تنظیمات اولیه که شامل مقادیر پیکربندی محیط اجرا است.
    """
    @classmethod
    def load_settings(cls) -> "Settings":
        """
        Tries to load the settings from the ZenML secret store. If the secret does not exist, it initializes the settings from the .env file and default values.

        Returns:
            Settings: The initialized settings object.
        """

        try:
            logger.info("Trying to load settings from ZenML secret store...")

            settings_secrets = Client().get_secret("settings")
            settings = Settings(**settings_secrets.secret_values)
        except(RuntimeError, KeyError):
            logger.warning(
                "Failed to load settings from the ZenML secret store. Defaulting to loading the settings from the '.env' file."
            )
            settings = Settings()

        return settings
    
    def export(self) -> None:
        """
        Exports the settings to the ZenML secret store.
        it means that the current configuration settings of the application
        are saved securely in ZenML's secret management system.
        """

        env_vars = settings.model_dump()
        for key, value in env_vars.items():
            env_vars[key] = str(value)

        client = Client()

        try:
            client.create_secret(name="settings", values=env_vars)
        except EntityExistsError:
            logger.warning(
                "Secret 'scope' already exists. Delete it manually by running 'zenml secret delete settings', before trying to recreate it."
            )


settings = Settings.load_settings()