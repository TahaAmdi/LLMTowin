from zenml import pipeline
from loguru import logger

from steps.etl.get_or_create_user import get_or_create_user


@pipeline
def user_test_pipeline(user_name: str):
    """یک پایپ‌لاین ساده برای تست گام get_or_create_user."""
    logger.info(f"Pipeline started for user: {user_name}")
    
    get_or_create_user(user_full_name=user_name)
    
    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    logger.info("Running test pipeline...")
    
    user_test_pipeline(user_name="Ali Rezaei (Test Run)")
    
    logger.info("Pipeline run finished. Check ZenML dashboard.")