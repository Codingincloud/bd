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
                'addressdetails': 1,
                'zoom': 18,
                'accept-language': 'en',  # Force English language
                'namedetails': 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/reverse",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    address = data.get('address', {})
                    result = {
                        'success': True,
                        'display_name': data['display_name'],
                        'formatted_address': self._format_nepal_address(address),
                        'address_details': address,

                        # Detailed components
                        'house_number': address.get('house_number', ''),
                        'road': address.get('road', ''),
                        'neighbourhood': address.get('neighbourhood', ''),
                        'suburb': address.get('suburb', ''),
                        'quarter': address.get('quarter', ''),
                        'village': address.get('village', ''),
                        'town': address.get('town', ''),
                        'city': self._get_city_name(address),
                        'municipality': address.get('municipality', ''),
                        'district': address.get('state_district', ''),
                        'state': address.get('state', ''),
                        'region': address.get('region', ''),
                        'postcode': address.get('postcode', ''),
                        'country': address.get('country', ''),
                        'country_code': address.get('country_code', '').upper(),

                        # Nepal-specific
                        'ward': self._extract_ward_number(address),
                        'tole': address.get('neighbourhood', ''),
                        'vdc_municipality': self._get_vdc_municipality(address),

                        # Coordinates
                        'latitude': float(lat),
                        'longitude': float(lng),

                        # Additional info
                        'place_type': data.get('type', ''),
                        'importance': data.get('importance', 0),
                        'confidence': self._calculate_confidence(data),
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

    def _format_nepal_address(self, address):
        """Format address specifically for Nepal with English names only"""
        import re
        parts = []

        def clean_english_text(text):
            """Clean text to ensure English characters only"""
            if not text:
                return ''
            # Remove non-ASCII characters and clean up
            cleaned = re.sub(r'[^\x00-\x7F]+', '', str(text)).strip()
            return cleaned.title() if cleaned else ''

        # House number and road
        if address.get('house_number'):
            parts.append(clean_english_text(address['house_number']))
        if address.get('road'):
            parts.append(clean_english_text(address['road']))

        # Neighbourhood/Tole
        if address.get('neighbourhood'):
            parts.append(clean_english_text(address['neighbourhood']))
        elif address.get('suburb'):
            parts.append(clean_english_text(address['suburb']))

        # City/Municipality
        city = self._get_city_name(address)
        if city:
            parts.append(city)

        # District
        if address.get('state_district'):
            parts.append(clean_english_text(address['state_district']))

        # State/Province
        if address.get('state'):
            parts.append(clean_english_text(address['state']))

        # Country (always in English)
        if address.get('country'):
            parts.append('Nepal' if 'nepal' in address['country'].lower() else address['country'])

        return ', '.join(filter(None, parts))

    def _get_city_name(self, address):
        """Extract the most appropriate city name in English"""
        # Prefer English names and common international names
        city_name = (address.get('city') or
                    address.get('town') or
                    address.get('municipality') or
                    address.get('village') or
                    address.get('suburb', ''))

        # Clean up the city name to ensure English characters
        if city_name:
            # Remove any non-ASCII characters and clean up
            import re
            city_name = re.sub(r'[^\x00-\x7F]+', '', city_name).strip()
            # Capitalize properly
            city_name = city_name.title()

        return city_name

    def _extract_ward_number(self, address):
        """Extract ward number from Nepal address"""
        import re
        # Look for ward information in various fields
        for field in ['neighbourhood', 'suburb', 'quarter']:
            value = address.get(field, '')
            if 'ward' in value.lower():
                # Extract number from "Ward 5" or "Ward No. 5"
                match = re.search(r'ward\s*(?:no\.?\s*)?(\d+)', value.lower())
                if match:
                    return match.group(1)
        return ''

    def _get_vdc_municipality(self, address):
        """Get VDC or Municipality name"""
        return (address.get('municipality') or
                address.get('city') or
                address.get('town') or
                address.get('village', ''))

    def _calculate_confidence(self, data):
        """Calculate confidence score based on available data"""
        score = 0
        address = data.get('address', {})

        # Base score from importance
        score += (data.get('importance', 0) * 50)

        # Add points for detailed address components
        if address.get('house_number'): score += 10
        if address.get('road'): score += 10
        if address.get('neighbourhood'): score += 10
        if address.get('city'): score += 15
        if address.get('postcode'): score += 5

        return min(100, max(0, score))


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
