"""
Hard-coded Authentication System
Maps users to unique internal IDs
"""

# Hard-coded user database
# Format: username -> (password, user_id)
USERS = {
    "admin": ("admin", "user_001"),
    "user": ("password", "user_002"),

    # New auto-generated users:
    "user1": ("user1", "user_003"),
    "user2": ("user2", "user_004"),
    "user3": ("user3", "user_005"),
    "user4": ("user4", "user_006"),
    "user5": ("user5", "user_007"),
    "user6": ("user6", "user_008"),
    "user7": ("user7", "user_009"),
    "user8": ("user8", "user_010"),
    "user9": ("user9", "user_011"),
    "user10": ("user10", "user_012"),
    "user11": ("user11", "user_013"),
    "user12": ("user12", "user_014"),
    "user13": ("user13", "user_015"),
    "user14": ("user14", "user_016"),
    "user15": ("user15", "user_017"),
    "user16": ("user16", "user_018"),
    "user17": ("user17", "user_019"),
    "user18": ("user18", "user_020"),
    "user19": ("user19", "user_021"),
    "user20": ("user20", "user_022"),
    "psudha":  ("psudha",  "user_023"),
    "dprao":   ("dprao",   "user_024"),
    "dpadmaja":("dpadmaja","user_025"),
    "drevathi":("drevathi","user_026"),
    "kreddy":  ("kreddy",  "user_027"),
    "mhraju":  ("mhraju",  "user_028"),
    "mjrao":   ("mjrao",   "user_029"),

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

