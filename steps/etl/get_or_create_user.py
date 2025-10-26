from loguru import logger
from typing_extensions import Annotated
from zenml import step, get_step_context

from llm_engineering.domain.documents import UserDocument
from llm_engineering.application import utils

@step
def get_or_create_user(user_full_name: str) -> Annotated[UserDocument, "user"]:
    """Get or create a user document in the database.

    Args:
        user_funll_name (str): The full name of the user.

    Returns:
        UserDocument: The user document.
    """
    logger.info(f"Getting or creating user: {user_full_name}")

    first_name, last_name = utils.split_user_full_name(user_full_name)

    user = UserDocument.get_or_create(
        first_name=first_name,
        last_name=last_name
    )
    
    if not user:
        logger.error(f"Failed to get or create user: {user_full_name}")

        raise RuntimeError(f"Failed to get or create user: {user_full_name}")
    
    step_context = get_step_context() # zenml step context
    step_context.add_output_metadata(
        output_name="user",
        metadata=_get_metadata(user_full_name, user)
    )

    return user

def _get_metadata(user_full_name: str, user: UserDocument) -> dict:
    return {
        "query": {
            "user_full_name": user_full_name,
        },
        "retrived": {
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }