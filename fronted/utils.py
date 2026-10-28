# fronted/utils.py

def get_logged_in_user(request):
    """
    Helper function to return the logged-in user from the session.
    If using Django's built-in auth, you can adjust accordingly.
    """
    if request.user.is_authenticated:
        return request.user
    return None
