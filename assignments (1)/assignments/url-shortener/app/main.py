from flask import Flask, jsonify, request, redirect, abort
from app.models import db
from app.utils import (
    is_valid_url, 
    generate_unique_short_code, 
    sanitize_url, 
    validate_short_code
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """
    Shorten URL endpoint
    
    Expected JSON payload:
    {
        "url": "https://example.com/very/long/url"
    }
    
    Returns:
    {
        "short_code": "abc123",
        "original_url": "https://example.com/very/long/url",
        "short_url": "http://localhost:5000/abc123"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "Missing 'url' field in request body"
            }), 400
        
        original_url = data['url']
        
        # Validate URL
        if not is_valid_url(original_url):
            return jsonify({
                "error": "Invalid URL format"
            }), 400
        
        # Sanitize URL
        sanitized_url = sanitize_url(original_url)
        
        # Generate unique short code
        short_code = generate_unique_short_code(db)
        
        if not short_code:
            return jsonify({
                "error": "Unable to generate unique short code"
            }), 500
        
        # Store URL mapping
        success = db.create_url_mapping(short_code, sanitized_url)
        
        if not success:
            return jsonify({
                "error": "Failed to create URL mapping"
            }), 500
        
        # Log the creation
        logger.info(f"Created short URL: {short_code} -> {sanitized_url}")
        
        # Return response
        return jsonify({
            "short_code": short_code,
            "original_url": sanitized_url,
            "short_url": f"http://localhost:5000/{short_code}"
        }), 201
        
    except Exception as e:
        logger.error(f"Error in shorten_url: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/<short_code>')
def redirect_to_original(short_code):
    """
    Redirect endpoint
    
    Args:
        short_code: The short code to redirect
        
    Returns:
        Redirect to original URL or 404 if not found
    """
    try:
        # Validate short code format
        if not validate_short_code(short_code):
            abort(404, description="Invalid short code format")
        
        # Get URL mapping
        mapping = db.get_url_mapping(short_code)
        
        if not mapping:
            abort(404, description="Short code not found")
        
        # Increment click count
        db.increment_click_count(short_code)
        
        # Log the redirect
        logger.info(f"Redirect: {short_code} -> {mapping['original_url']}")
        
        # Redirect to original URL
        return redirect(mapping['original_url'], code=302)
        
    except Exception as e:
        logger.error(f"Error in redirect: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/api/stats/<short_code>')
def get_url_stats(short_code):
    """
    Analytics endpoint
    
    Args:
        short_code: The short code to get stats for
        
    Returns:
        JSON with URL statistics
    """
    try:
        # Validate short code format
        if not validate_short_code(short_code):
            return jsonify({
                "error": "Invalid short code format"
            }), 400
        
        # Get URL mapping
        mapping = db.get_url_mapping(short_code)
        
        if not mapping:
            return jsonify({
                "error": "Short code not found"
            }), 404
        
        # Return statistics
        return jsonify({
            "short_code": mapping['short_code'],
            "original_url": mapping['original_url'],
            "click_count": mapping['click_count'],
            "created_at": mapping['created_at']
        })
        
    except Exception as e:
        logger.error(f"Error in get_url_stats: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": error.description if hasattr(error, 'description') else "Resource not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)