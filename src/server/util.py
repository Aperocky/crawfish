SUCCESS_RESULT = {"success": True}
FAILURE_RESULT = {"success": False}
AUTH_CACHE = {}

def fail_with_reason(reason):
    result = FAILURE_RESULT.copy()
    result.update({"reason": reason})
    return result

def populate_auth_cache(author_id, result):
    AUTH_CACHE["author_id"] = author_id
    AUTH_CACHE["result"] = result

def populate_auth_image(images):
    AUTH_CACHE["images"] = images
