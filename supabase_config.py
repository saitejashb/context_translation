"""
Supabase configuration for feedback storage
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from supabase import create_client, Client  # type: ignore
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False
    # Silent - Supabase is optional and only needed for comments/feedback

# Supabase configuration - use environment variables
# Supports both NEXT_PUBLIC_ (Next.js) and standard naming
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def get_supabase_client():
    """Get Supabase client"""
    if not HAS_SUPABASE_LIB:
        return None
    
    if not SUPABASE_URL or not SUPABASE_KEY or SUPABASE_URL == "your-supabase-url":
        print("Warning: Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
        return None
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def save_feedback(feedback_data):
    """Save feedback to Supabase"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        # Insert feedback into 'feedback' table
        response = supabase.table("feedback").insert(feedback_data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return {"success": False, "error": str(e)}

def save_comment(comment_data):
    """Save comment to Supabase"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        # Clean the data - remove None values and ensure proper types
        cleaned_data = {}
        for key, value in comment_data.items():
            if value is not None and value != '':
                # Skip text_position entirely - it's optional and may cause issues
                if key == 'text_position':
                    continue
                # Ensure strings are not empty
                if isinstance(value, str) and value.strip():
                    cleaned_data[key] = value.strip()
                elif not isinstance(value, str):
                    cleaned_data[key] = value
        
        # Ensure required fields are present
        if 'translation_id' not in cleaned_data or not cleaned_data['translation_id']:
            return {"success": False, "error": "translation_id is required"}
        if 'doc_type' not in cleaned_data or not cleaned_data['doc_type']:
            return {"success": False, "error": "doc_type is required"}
        if 'comment' not in cleaned_data or not cleaned_data['comment']:
            return {"success": False, "error": "comment is required"}
        if 'selected_text' not in cleaned_data:
            cleaned_data['selected_text'] = ''  # Default to empty string
        
        # Insert comment into 'comments' table
        response = supabase.table("comments").insert(cleaned_data).execute()
        return {"success": True, "data": response.data[0] if response.data else None}
    except Exception as e:
        print(f"Error saving comment: {e}")
        import traceback
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}

def get_comments(translation_id, engine=None):
    """Get comments for a translation, optionally filtered by engine"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            # Silent - Supabase is optional for reading comments
            return {"success": False, "error": "Supabase not configured"}
        
        # Build query
        query = supabase.table("comments").select("*").eq("translation_id", translation_id)
        
        # Filter by engine if provided
        if engine:
            query = query.eq("engine", engine)
        
        # Order by creation date
        response = query.order("created_at", desc=True).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        # Silent error - don't print warnings for optional feature
        # Only log if it's not a table/schema error (which means Supabase isn't set up)
        error_str = str(e)
        # Suppress warnings for table not found errors (PGRST205, schema cache errors)
        if ("PGRST205" in error_str or 
            "Could not find the table" in error_str or 
            "schema cache" in error_str.lower() or
            "not configured" in error_str.lower()):
            # Silent - table doesn't exist, which is fine
            pass
        else:
            # Only print real errors
            print(f"Error getting comments: {e}")
        return {"success": False, "error": str(e)}

def delete_comment(comment_id):
    """Delete a comment"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        # Delete comment
        response = supabase.table("comments").delete().eq("id", comment_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return {"success": False, "error": str(e)}

