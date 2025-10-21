"""crawl_links and get_or_create_user are defined in steps/etl.py
They are imported here to be used in the pipeline.

1)
crawl_links: A step that crawls web links to extract data. |>*
 مرحله‌ای که پیوندهای وب را برای استخراج داده‌ها بررسی می‌کند.

2)
get_or_create_user: A step that retrieves 
an existing user or creates a new one if not found. |>*
مرحله‌ای که یک کاربر موجود را بازیابی می‌کند یا 
در صورت عدم وجود، یک کاربر جدید ایجاد می‌کند

"""

from zenml import pipeline
from steps.etl import crawl_links, get_or_create_user
