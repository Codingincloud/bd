from django import forms
from .models import Donor
# Removed Nepal locations dependency


class LocationUpdateForm(forms.ModelForm):
    """Simple form for updating donor location"""
    
    # Add a choice field for popular cities
    POPULAR_CITIES = [
        ('Kathmandu', 'Kathmandu'),
        ('Pokhara', 'Pokhara'),
        ('Lalitpur', 'Lalitpur'),
        ('Bhaktapur', 'Bhaktapur'),
        ('Biratnagar', 'Biratnagar'),
        ('Birgunj', 'Birgunj'),
        ('Dharan', 'Dharan'),
        ('Butwal', 'Butwal'),
        ('Hetauda', 'Hetauda'),
        ('Janakpur', 'Janakpur'),
    ]

    popular_city = forms.ChoiceField(
        choices=[('', 'Select a popular city')] + POPULAR_CITIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'fillCityFromPopular(this.value)'
        })
    )
    
    # Manual coordinate fields
    manual_latitude = forms.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 27.7172',
            'step': 'any'
        })
    )
    
    manual_longitude = forms.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 85.3240',
            'step': 'any'
        })
    )
    
    class Meta:
        model = Donor
        fields = ['address', 'city', 'state', 'postal_code', 'latitude', 'longitude']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your state/province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal code'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial values for manual coordinate fields
        if self.instance and self.instance.pk:
            self.fields['manual_latitude'].initial = self.instance.latitude
            self.fields['manual_longitude'].initial = self.instance.longitude
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Handle manual coordinates
        manual_lat = cleaned_data.get('manual_latitude')
        manual_lng = cleaned_data.get('manual_longitude')
        
        if manual_lat is not None and manual_lng is not None:
            cleaned_data['latitude'] = manual_lat
            cleaned_data['longitude'] = manual_lng
        
        return cleaned_data


class SimpleLocationForm(forms.Form):
    """Very simple location form for quick updates"""
    
    LOCATION_CHOICES = [
        ('', 'Choose your location...'),
        ('kathmandu', 'Kathmandu'),
        ('pokhara', 'Pokhara'),
        ('lalitpur', 'Lalitpur (Patan)'),
        ('bhaktapur', 'Bhaktapur'),
        ('biratnagar', 'Biratnagar'),
        ('birgunj', 'Birgunj'),
        ('dharan', 'Dharan'),
        ('hetauda', 'Hetauda'),
        ('janakpur', 'Janakpur'),
        ('butwal', 'Butwal'),
        ('chitwan', 'Chitwan'),
        ('bharatpur', 'Bharatpur'),
        ('nepalgunj', 'Nepalgunj'),
        ('dhangadhi', 'Dhangadhi'),
        ('other', 'Other (I will enter manually)')
    ]
    
    location_choice = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'handleLocationChoice(this.value)'
        }),
        label='Quick Location Selection'
    )
    
    custom_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city name',
            'style': 'display: none;'
        }),
        label='City Name'
    )
    
    custom_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your address',
            'style': 'display: none;'
        }),
        label='Address'
    )


class MedicalInfoUpdateForm(forms.ModelForm):
    """Form for donors to update their medical information"""

    class Meta:
        model = Donor
        fields = [
            'weight', 'height', 'medical_conditions',
            'emergency_contact_name', 'emergency_contact_phone',
            'allow_emergency_contact'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your weight in kg',
                'step': '0.1',
                'min': '30',
                'max': '200'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your height in cm',
                'step': '0.1',
                'min': '100',
                'max': '250'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List any medical conditions, allergies, or medications you are taking'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of emergency contact'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number of emergency contact'
            }),
            'allow_emergency_contact': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'weight': 'Weight (kg)',
            'height': 'Height (cm)',
            'medical_conditions': 'Medical Conditions & Medications',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'allow_emergency_contact': 'Allow emergency contact during urgent blood needs'
        }


class HealthMetricsForm(forms.Form):
    """Form for donors to update basic health metrics they can measure at home"""

    current_weight = forms.DecimalField(
        max_digits=5,
        decimal_places=1,
        min_value=30,
        max_value=200,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current weight in kg',
            'step': '0.1'
        }),
        label='Current Weight (kg)'
    )

    blood_pressure_systolic = forms.IntegerField(
        min_value=80,
        max_value=200,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 120'
        }),
        label='Blood Pressure - Systolic (top number)'
    )

    blood_pressure_diastolic = forms.IntegerField(
        min_value=50,
        max_value=120,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 80'
        }),
        label='Blood Pressure - Diastolic (bottom number)'
    )

    resting_heart_rate = forms.IntegerField(
        min_value=40,
        max_value=150,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Beats per minute'
        }),
        label='Resting Heart Rate (bpm)'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes about your health today'
        }),
        label='Health Notes (Optional)'
    )
