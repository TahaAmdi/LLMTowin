from enum import StrEnum


class DataCategory(StrEnum):
    PROMPT = "prompt" 
    QUERIES = "queries"

    INSTRUCT_DATASET_SAMPLES = "instruct_dataset_samples"
    INSTRUCT_DATASET = "instruct_dataset"
    PREFERENCE_DATASET_SAMPLES = "preference_dataset_samples"
    PREFERENCE_DATASET = "preference_dataset"

    POSTS = "posts"
    ARTICLES = "articles"
    REPOSITORIES = "repositories"

"""
───────────────────────────────────────────────
English Explanation
───────────────────────────────────────────────
StrEnum is a Python class that combines Enum and str.  
It allows you to define constants that behave both like strings and enumerations.

For example:
    DataCategory.PROMPT == "prompt"     → True
    str(DataCategory.PROMPT)            → "prompt"

This helps to maintain consistency across the project and avoid typos in data category names.

───────────────────────────────────────────────
توضیح فارسی
───────────────────────────────────────────────
کلاس StrEnum ترکیبی از رشته و شمارنده است.  
یعنی هر مقدار هم مانند رشته عمل می‌کند، هم مانند مقدار ثابت از نوع Enum.  

به عنوان نمونه:
    DataCategory.PROMPT == "prompt"  → درست است  
    str(DataCategory.PROMPT)         → خروجی برابر با "prompt"  

استفاده از این ساختار باعث می‌شود نام دسته‌های داده در سراسر پروژه ثابت بمانند
و اشتباه‌های تایپی یا ناهماهنگی در نوشتار از بین برود.
───────────────────────────────────────────────
"""