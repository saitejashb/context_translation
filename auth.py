"""
Hard-coded Authentication System
Maps users to unique internal IDs
"""

# Hard-coded user database
# Format: username -> (password, user_id)
USERS = {
    "admin": ("admin", "user_001"),
    "user": ("password", "user_002"),
    # Add more users as needed
}

def authenticate(username, password):
    """
    Authenticate user
    
    Args:
        username: Username
        password: Password
        
    Returns:
        Tuple of (success: bool, user_id: str or None, error: str or None)
    """
    if username not in USERS:
        return False, None, "Invalid username"
    
    stored_password, user_id = USERS[username]
    
    if password != stored_password:
        return False, None, "Invalid password"
    
    return True, user_id, None

def get_user_id(username):
    """
    Get user ID for a username (without authentication)
    
    Args:
        username: Username
        
    Returns:
        User ID or None
    """
    if username in USERS:
        return USERS[username][1]
    return None

def is_valid_user_id(user_id):
    """Check if user_id exists"""
    return any(uid == user_id for _, (_, uid) in USERS.items())

