import requests
import time
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Geocoding service using OpenStreetMap Nominatim API
    Free service, no API key required
    """
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BloodDonationSystem/1.0 (Contact: admin@bloodbank.com)'
        })
    
    def geocode(self, address: str, country: str = "Nepal") -> Optional[Dict]:
        """
        Convert address to coordinates
        
        Args:
            address: Address string (e.g., "Kathmandu", "Thamel, Kathmandu")
            country: Country to limit search (default: Nepal)
            
        Returns:
            Dict with lat, lng, display_name, and other details or None
        """
        # Create cache key
        cache_key = f"geocode_{address}_{country}".lower().replace(" ", "_")
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'q': f"{address}, {country}",
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': self._get_country_code(country)
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = {
                        'lat': float(data[0]['lat']),
                        'lng': float(data[0]['lon']),
                        'display_name': data[0]['display_name'],
                        'address_details': data[0].get('address', {}),
                        'importance': data[0].get('importance', 0)
                    }
                    
                    # Cache for 24 hours
                    cache.set(cache_key, result, 86400)
                    return result
            
            # Rate limiting - be nice to the free service
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Geocoding error for '{address}': {str(e)}")
        
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Convert coordinates to address
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Dict with address information or None
        """
        cache_key = f"reverse_{lat}_{lng}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/reverse",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = {
                        'display_name': data['display_name'],
                        'address_details': data.get('address', {})
                    }
                    
                    # Cache for 24 hours
                    cache.set(cache_key, result, 86400)
                    return result
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Reverse geocoding error for {lat}, {lng}: {str(e)}")
        
        return None
    
    def search_suggestions(self, query: str, country: str = "Nepal", limit: int = 5) -> List[Dict]:
        """
        Get address suggestions for autocomplete
        
        Args:
            query: Partial address string
            country: Country to limit search
            limit: Maximum number of suggestions
            
        Returns:
            List of suggestion dictionaries
        """
        if len(query) < 3:  # Don't search for very short queries
            return []
        
        cache_key = f"suggestions_{query}_{country}_{limit}".lower().replace(" ", "_")
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'q': f"{query}, {country}",
                'format': 'json',
                'limit': limit,
                'addressdetails': 1,
                'countrycodes': self._get_country_code(country)
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = []
                
                for item in data:
                    suggestion = {
                        'display_name': item['display_name'],
                        'lat': float(item['lat']),
                        'lng': float(item['lon']),
                        'address_details': item.get('address', {}),
                        'type': item.get('type', ''),
                        'importance': item.get('importance', 0)
                    }
                    suggestions.append(suggestion)
                
                # Cache for 1 hour
                cache.set(cache_key, suggestions, 3600)
                return suggestions
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Suggestions error for '{query}': {str(e)}")
        
        return []
    
    def _get_country_code(self, country: str) -> str:
        """Get ISO country code for country name"""
        country_codes = {
            'nepal': 'np',
            'india': 'in',
            'china': 'cn',
            'bangladesh': 'bd',
            'pakistan': 'pk',
            'sri lanka': 'lk',
            'bhutan': 'bt',
            'myanmar': 'mm'
        }
        return country_codes.get(country.lower(), 'np')


# Global instance
geocoding_service = GeocodingService()


def geocode_address(address: str, country: str = "Nepal") -> Optional[Tuple[float, float]]:
    """
    Simple function to get coordinates from address
    
    Returns:
        Tuple of (latitude, longitude) or None
    """
    result = geocoding_service.geocode(address, country)
    if result:
        return (result['lat'], result['lng'])
    return None


def get_address_suggestions(query: str, country: str = "Nepal") -> List[str]:
    """
    Simple function to get address suggestions
    
    Returns:
        List of address strings
    """
    suggestions = geocoding_service.search_suggestions(query, country)
    return [s['display_name'] for s in suggestions]
