"""
Simple Nepal location utilities without external API dependencies
"""

# Major Nepal cities with coordinates
NEPAL_CITIES = {
    'kathmandu': {'lat': 27.7172, 'lng': 85.3240, 'name': 'Kathmandu'},
    'pokhara': {'lat': 28.2096, 'lng': 83.9856, 'name': 'Pokhara'},
    'lalitpur': {'lat': 27.6683, 'lng': 85.3206, 'name': 'Lalitpur'},
    'bhaktapur': {'lat': 27.6710, 'lng': 85.4298, 'name': 'Bhaktapur'},
    'biratnagar': {'lat': 26.4525, 'lng': 87.2718, 'name': 'Biratnagar'},
    'birgunj': {'lat': 27.0104, 'lng': 84.8803, 'name': 'Birgunj'},
    'dharan': {'lat': 26.8147, 'lng': 87.2789, 'name': 'Dharan'},
    'hetauda': {'lat': 27.4287, 'lng': 85.0326, 'name': 'Hetauda'},
    'janakpur': {'lat': 26.7288, 'lng': 85.9256, 'name': 'Janakpur'},
    'butwal': {'lat': 27.7000, 'lng': 83.4486, 'name': 'Butwal'},
    'dhangadhi': {'lat': 28.6833, 'lng': 80.6167, 'name': 'Dhangadhi'},
    'tulsipur': {'lat': 28.1333, 'lng': 82.2833, 'name': 'Tulsipur'},
    'nepalgunj': {'lat': 28.0500, 'lng': 81.6167, 'name': 'Nepalgunj'},
    'bharatpur': {'lat': 27.6833, 'lng': 84.4333, 'name': 'Bharatpur'},
    'gorkha': {'lat': 28.0000, 'lng': 84.6333, 'name': 'Gorkha'},
    'chitwan': {'lat': 27.5291, 'lng': 84.3542, 'name': 'Chitwan'},
    'lumbini': {'lat': 27.4833, 'lng': 83.2833, 'name': 'Lumbini'},
    'mustang': {'lat': 28.7833, 'lng': 83.7333, 'name': 'Mustang'},
    'solukhumbu': {'lat': 27.7333, 'lng': 86.7167, 'name': 'Solukhumbu'},
    'everest': {'lat': 27.9881, 'lng': 86.9250, 'name': 'Everest Base Camp'},
    'thamel': {'lat': 27.7156, 'lng': 85.3145, 'name': 'Thamel, Kathmandu'},
    'patan': {'lat': 27.6683, 'lng': 85.3206, 'name': 'Patan'},
    'durbar square': {'lat': 27.7045, 'lng': 85.3077, 'name': 'Durbar Square, Kathmandu'},
    'new road': {'lat': 27.7006, 'lng': 85.3140, 'name': 'New Road, Kathmandu'},
    'ring road': {'lat': 27.7172, 'lng': 85.3240, 'name': 'Ring Road, Kathmandu'},
    'tribhuvan airport': {'lat': 27.6966, 'lng': 85.3591, 'name': 'Tribhuvan International Airport'},
    'pashupatinath': {'lat': 27.7106, 'lng': 85.3481, 'name': 'Pashupatinath Temple'},
    'swayambhunath': {'lat': 27.7149, 'lng': 85.2906, 'name': 'Swayambhunath Temple'},
    'boudhanath': {'lat': 27.7215, 'lng': 85.3618, 'name': 'Boudhanath Stupa'},
}

# Districts of Nepal
NEPAL_DISTRICTS = [
    'Achham', 'Arghakhanchi', 'Baglung', 'Baitadi', 'Bajhang', 'Bajura', 'Banke',
    'Bara', 'Bardiya', 'Bhaktapur', 'Bhojpur', 'Chitwan', 'Dadeldhura', 'Dailekh',
    'Dang', 'Darchula', 'Dhading', 'Dhankuta', 'Dhanusa', 'Dolakha', 'Dolpa',
    'Doti', 'Gorkha', 'Gulmi', 'Humla', 'Ilam', 'Jajarkot', 'Jhapa', 'Jumla',
    'Kailali', 'Kalikot', 'Kanchanpur', 'Kapilvastu', 'Kaski', 'Kathmandu',
    'Kavrepalanchok', 'Khotang', 'Lalitpur', 'Lamjung', 'Mahottari', 'Makwanpur',
    'Manang', 'Morang', 'Mugu', 'Mustang', 'Myagdi', 'Nawalparasi', 'Nuwakot',
    'Okhaldhunga', 'Palpa', 'Panchthar', 'Parbat', 'Parsa', 'Pyuthan', 'Ramechhap',
    'Rasuwa', 'Rautahat', 'Rolpa', 'Rukum', 'Rupandehi', 'Salyan', 'Sankhuwasabha',
    'Saptari', 'Sarlahi', 'Sindhuli', 'Sindhupalchok', 'Siraha', 'Solukhumbu',
    'Sunsari', 'Surkhet', 'Syangja', 'Tanahu', 'Taplejung', 'Terhathum', 'Udayapur'
]


def get_nepal_location(location_name):
    """
    Get coordinates for a Nepal location
    
    Args:
        location_name: Name of the location
        
    Returns:
        Dict with lat, lng, name or None
    """
    if not location_name:
        return None
    
    # Normalize the location name
    normalized = location_name.lower().strip()
    
    # Check exact match first
    if normalized in NEPAL_CITIES:
        return NEPAL_CITIES[normalized]
    
    # Check partial matches
    for key, value in NEPAL_CITIES.items():
        if normalized in key or key in normalized:
            return value
    
    # Check if it's a district
    for district in NEPAL_DISTRICTS:
        if district.lower() == normalized:
            # For districts without specific coordinates, use approximate center
            return {
                'lat': 27.7172,  # Approximate center of Nepal
                'lng': 85.3240,
                'name': district
            }
    
    return None


def get_nepal_suggestions(query):
    """
    Get location suggestions for Nepal
    
    Args:
        query: Partial location name
        
    Returns:
        List of suggestion dictionaries
    """
    if not query or len(query) < 2:
        return []
    
    suggestions = []
    query_lower = query.lower()
    
    # Search in cities
    for key, value in NEPAL_CITIES.items():
        if query_lower in key or query_lower in value['name'].lower():
            suggestions.append({
                'name': value['name'],
                'lat': value['lat'],
                'lng': value['lng'],
                'type': 'city'
            })
    
    # Search in districts
    for district in NEPAL_DISTRICTS:
        if query_lower in district.lower():
            suggestions.append({
                'name': district,
                'lat': 27.7172,  # Default center
                'lng': 85.3240,
                'type': 'district'
            })
    
    # Remove duplicates and limit results
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion['name'] not in seen:
            seen.add(suggestion['name'])
            unique_suggestions.append(suggestion)
            if len(unique_suggestions) >= 8:
                break
    
    return unique_suggestions


def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate distance between two points using Haversine formula
    
    Returns:
        Distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return round(c * r, 2)


def get_popular_cities():
    """Get list of popular Nepal cities for autocomplete"""
    popular = [
        'Kathmandu', 'Pokhara', 'Lalitpur', 'Bhaktapur', 'Biratnagar',
        'Birgunj', 'Dharan', 'Hetauda', 'Janakpur', 'Butwal',
        'Chitwan', 'Bharatpur', 'Nepalgunj', 'Dhangadhi'
    ]
    return popular
