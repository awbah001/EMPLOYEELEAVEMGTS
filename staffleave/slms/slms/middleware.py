"""
Middleware for cache control and security headers
"""

class NoCacheMiddleware:
    """
    Middleware to prevent caching of authenticated pages.
    This ensures users cannot access pages via browser back button after logout.
    
    Uses multiple strategies:
    1. Cache-Control headers (no-cache, no-store, must-revalidate)
    2. Pragma headers (no-cache)
    3. Expires headers (0)
    4. ETag and Last-Modified headers (force revalidation)
    5. Private directive (only for user)
    
    Applies to all authenticated requests to prevent browser caching of 
    sensitive pages containing user data.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Apply aggressive no-cache headers to all authenticated requests
        if request.user.is_authenticated:
            # Cache-Control: Most important - tells browsers and proxies not to cache
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0, post-check=0, pre-check=0'
            
            # Pragma: Legacy HTTP/1.0 support
            response['Pragma'] = 'no-cache'
            
            # Expires: Set to past date to expire immediately
            response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            
            # Remove ETag to force revalidation
            if 'ETag' in response:
                del response['ETag']
            
            # Force Last-Modified check
            response['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            
            # Additional headers for browsers
            response['Vary'] = 'Cookie'
        
        # Also apply to logout pages to clear browser history
        if '/doLogout' in request.path or 'logout' in request.path.lower():
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0, post-check=0, pre-check=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            if 'ETag' in response:
                del response['ETag']
            response['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        
        return response

