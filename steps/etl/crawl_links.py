"""
For parsing URLs.*|>
*|>Parsing URLs is essential in web crawling and ETL processes because it allows you to break down a URL into its components.
It is used to extract components such as the scheme, netloc, path, etc.
این کتابخانه در پایتون برای تجزیه و تحلیل و دستکاری یو ار ال ها استفاده می‌شود
تا بتوانید اجزای مختلف یک یو ار ال را استخراج کنید
"""
from asyncore import dispatcher
from urllib.parse import urlparse
"""
Importing logger for logging purposes.*|>
|>Logging is crucial for monitoring the execution of ETL processes, *|> 
*|>debugging issues, and keeping track of the workflow.
ETL means Extract, Transform, Load, which is a common process in data engineering.
کتابخانه لاگورو یک کتابخانه قدرتمند  لاگینگ برای ثبت وقایع در پایتون
است که استفاده از آن را ساده‌تر و کارآمدتر می‌کند.
همچنین قابلیت‌های پیشرفته‌ای مانند قالب‌بندی انعطاف‌پذیر،
مدیریت سطح لاگینگ، و خروجی به چندین مقصد را فراهم می‌کند.
"""
from loguru import Logger, logger
from tqdm import tqdm
"""
For type annotations.*|>
*|>Type annotations help in improving code readability and maintainability.
این کتابخانه به شما امکان می‌دهد تا نوع داده‌های متغیرها و پارامترهای توابع را مشخص کنید
و به این ترتیب کد شما قابل فهم‌تر و نگهداری آن آسان‌تر می‌شود.
"""
from typing_extensions import Annotated
"""
ZenML imports.*|>
*|>ZenML is a machine learning operations (MLOps) framework that helps
streamline the process of building, deploying, and maintaining machine learning models.
It provides tools and abstractions to manage the entire machine learning lifecycle,
from data ingestion to model deployment and monitoring.
این یک فریم‌ورک عملیات یادگیری ماشین ام ال اپس است که به ساده‌سازی فرآیند ساخت،
استقرار و نگهداری مدل‌های یادگیری ماشین کمک می‌کند.
این فریم‌ورک ابزارها و انتزاع‌هایی را برای مدیریت کل چرخه عمر یادگیری ماشین،
از جذب داده‌ها تا استقرار و نظارت بر مدل فراهم می‌کند.
"""
from zenml import get_step_context, step
"""
CrawlerDispatcher 
یه کلاس مرکزی 
(Dispatcher pattern) 
برای مدیریت انواع 
crawler هاست.
فرض کن پروژه‌ی 
LLM Twin می‌خواد از چندین منبع 
(LinkedIn، Medium، GitHub، Twitter، ...) داده جمع کنه.
به‌جای اینکه برای هر منبع جداگانه کد بنویسه،
یک Dispatcher وجود داره که می‌گه:
لینک رو بده من، خودم تشخیص می‌دم از چه نوعیه و با کدوم crawler باید خونده بشه.
"""
from llm_engineering.application.crawlers.dispatcher import CrawlerDispatcher
"""
بوزر داکیومنت یک مدل داده برای کاربر است که در پایگاه داده (مانند مونگو) ذخیره می‌شود.
در ساختار تمیز نرم‌افزار، بخش «هسته منطقی» جایی است که موجودیت‌های اصلی سیستم، مانند کاربر، تعریف می‌شوند.

در اینجا، تمام اطلاعات مربوط به کاربر (مثل نام، معرفی، و پیوندهای اجتماعی) در قالب UserDocument نگهداری می‌شود.

💡 کاربرد در این گام:
زمانی که خزنده از پیوندها داده جمع‌آوری می‌کند، باید بداند این داده متعلق به کدام کاربر است.
به همین دلیل، user: UserDocument به ZenML اطلاع می‌دهد که:

«من در حال جمع‌آوری داده‌های مربوط به این کاربر خاص هستم؛ لطفاً داده‌های استخراج‌شده را به همان کاربر متصل کن.»    
"""
from llm_engineering.domain.documents import UserDocument

"""
یعنی تو به این گام از خط لوله می‌گی:
برو این دو تا لینک رو برام بخون.
هرچی اطلاعات هست (متن مقاله، توضیح پروژه و...) استخراج کن،
ولی یادت باشه اینا مربوط به کاربر مونا حسینی هستن.
"""
#crawl_links(user=mona, links=["https://medium.com/@mona/article1", "https://github.com/mona/project1"])
@step
def crawl_links(user: UserDocument, links: list[str]) -> Annotated[list[str], "crawled_links"]:

    return[]