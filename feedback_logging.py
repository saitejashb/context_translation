"""
Feedback and Translation Logging Module
Logs all translations and feedback to Supabase
"""

from datetime import datetime
try:
    from supabase_config import get_supabase_client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("Warning: Supabase not configured. Logging will not work.")

def log_translation(user_id, translation_model, source_text, translated_text, translation_id=None):
    """
    Log translation to Supabase
    
    Args:
        user_id: User ID
        translation_model: Model used (e.g., "indictrans2", "gemini-3-pro", "google-standard", "google-adaptive")
        source_text: Original English text
        translated_text: Translated Telugu text
        translation_id: Optional translation session ID
        
    Returns:
        Dict with success status
    """
    if not HAS_SUPABASE:
        # Silent - Supabase is optional for translation logging
        return {"success": True}
    
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        translation_log = {
            "user_id": user_id,
            "translation_model": translation_model,
            "source_text": source_text[:5000],  # Limit length
            "translated_text": translated_text[:5000],  # Limit length
            "translation_id": translation_id,
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("translation_logs").insert(translation_log).execute()
        return {"success": True, "data": response.data}
        
    except Exception as e:
        # Silent error - Supabase is optional
        # Only log if it's not a table/schema error (which means Supabase isn't set up)
        error_str = str(e)
        if "table" not in error_str.lower() and "schema" not in error_str.lower():
            print(f"Error logging translation: {e}")
        return {"success": False, "error": str(e)}

def log_feedback(user_id, translation_id, translation_model, feedback_data):
    """
    Log feedback to Supabase
    
    Args:
        user_id: User ID
        translation_id: Translation session ID
        translation_model: Model used
        feedback_data: Dict with feedback fields (ratings, comments, etc.)
        
    Returns:
        Dict with success status
    """
    if not HAS_SUPABASE:
        # Supabase is required for feedback - return error so user knows
        return {"success": False, "error": "Supabase not configured. Please install supabase library to save feedback."}
    
    try:
        supabase = get_supabase_client()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        feedback_log = {
            "user_id": user_id,
            "translation_id": translation_id,
            "translation_model": translation_model,
            "file_type": feedback_data.get("file_type"),
            "language_pair": feedback_data.get("language_pair", "English-Telugu"),
            "translation_method": feedback_data.get("translation_method", translation_model),
            "overall_quality": feedback_data.get("overall_quality"),
            "structure_preservation": feedback_data.get("structure_preservation"),
            "preview_features": feedback_data.get("preview_features"),
            "suggestions": feedback_data.get("suggestions", ""),
            "thumbs_rating": feedback_data.get("thumbs_rating"),
            "criteria_ratings": feedback_data.get("criteria_ratings"),  # Store as JSON
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("feedback").insert(feedback_log).execute()
        return {"success": True, "data": response.data}
        
    except Exception as e:
        print(f"Error logging feedback: {e}")
        return {"success": False, "error": str(e)}

