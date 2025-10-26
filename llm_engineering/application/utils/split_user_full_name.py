from llm_engineering.domain.exceptions import ImproperlyConfigured



def split_user_full_name(user:str | None) -> tuple[str, str]:
    
    """Splits a user's full name into first and last name.

    Args:
        user (str | None): The full name of the user.

    Returns:
        tuple[str, str]: A tuple containing the first name and last name.
    Raises:
        ImproperlyConfigured: If the user name is not provided.
    """
    if user is None:
        raise ImproperlyConfigured("User name must be provided.")

    name_tokens = user.split(" ") # retun a list of strings
    if len(name_tokens) == 0:
        raise ImproperlyConfigured("User name must be provided.")
    elif len(name_tokens) == 1:
        first_name, last_name = name_tokens[0], name_tokens[0]
    else:
        # More than one token, assume last token is last name
        # return a tuple of strings 
        first_name, last_name = " ".join(name_tokens[:-1]), name_tokens[-1] 

    return first_name, last_name