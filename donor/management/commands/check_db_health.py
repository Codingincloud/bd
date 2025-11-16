"""
Django management command to check database health
"""
from django.core.management.base import BaseCommand
from django.core.management.color import make_style
from utils.db_health import DatabaseHealthChecker
import json

class Command(BaseCommand):
    help = 'Check database health and connectivity'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = make_style()
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle(self, *args, **options):
        """Run database health check"""
        
        if options['format'] == 'json':
            self.output_json()
        else:
            self.output_text(options['verbose'])
    
    def output_text(self, verbose=False):
        """Output health check results in text format"""
        
        self.stdout.write(self.style.HTTP_INFO("🔍 Database Health Check"))
        self.stdout.write("=" * 50)
        
        # Run health check
        results = DatabaseHealthChecker.run_full_health_check()
        
        # Overall status
        if results['overall_status'] == 'healthy':
            self.stdout.write(
                self.style.SUCCESS(f"✅ Overall Status: {results['overall_status'].upper()}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Overall Status: {results['overall_status'].upper()}")
            )
        
        self.stdout.write("")
        
        # Individual checks
        for check_name, check_result in results['checks'].items():
            status = check_result['status']
            
            if status == 'pass':
                status_icon = "✅"
                status_style = self.style.SUCCESS
            elif status == 'warn':
                status_icon = "⚠️"
                status_style = self.style.WARNING
            else:
                status_icon = "❌"
                status_style = self.style.ERROR
            
            self.stdout.write(
                status_style(f"{status_icon} {check_name.title()}: {status.upper()}")
            )
            
            # Show details if verbose or if there are issues
            if verbose or status != 'pass':
                if 'message' in check_result:
                    self.stdout.write(f"   📝 {check_result['message']}")
                
                if 'issues' in check_result and check_result['issues']:
                    for issue in check_result['issues']:
                        self.stdout.write(f"   ⚠️  {issue}")
                
                if 'missing_permissions' in check_result and check_result['missing_permissions']:
                    for perm in check_result['missing_permissions']:
                        self.stdout.write(f"   🔒 Missing permission: {perm}")
                
                if 'supported' in check_result and not check_result['supported']:
                    self.stdout.write(f"   ⚠️  Version may not be fully supported")
            
            self.stdout.write("")
        
        # Recommendations
        if results['overall_status'] != 'healthy':
            self.stdout.write(self.style.HTTP_INFO("💡 Recommendations:"))
            
            for check_name, check_result in results['checks'].items():
                if check_result['status'] == 'fail':
                    if check_name == 'connection':
                        self.stdout.write("   • Check PostgreSQL service is running")
                        self.stdout.write("   • Verify database credentials in settings.py")
                        self.stdout.write("   • Ensure database exists and is accessible")
                    
                    elif check_name == 'permissions':
                        self.stdout.write("   • Grant necessary permissions to database user")
                        self.stdout.write("   • Consider using a superuser for development")
                    
                    elif check_name == 'settings':
                        self.stdout.write("   • Review database configuration in settings.py")
                        self.stdout.write("   • Ensure all required settings are provided")
    
    def output_json(self):
        """Output health check results in JSON format"""
        results = DatabaseHealthChecker.run_full_health_check()
        self.stdout.write(json.dumps(results, indent=2))
    
    def check_specific_models(self):
        """Check if specific models can be accessed"""
        model_checks = {}
        
        try:
            from donor.models import Donor, DonationRequest, EmergencyRequest
            from admin_panel.models import SystemNotification
            
            models_to_check = [
                ('Donor', Donor),
                ('DonationRequest', DonationRequest),
                ('EmergencyRequest', EmergencyRequest),
                ('SystemNotification', SystemNotification),
            ]
            
            for model_name, model_class in models_to_check:
                try:
                    count = model_class.objects.count()
                    model_checks[model_name] = {
                        'accessible': True,
                        'count': count,
                        'error': None
                    }
                except Exception as e:
                    model_checks[model_name] = {
                        'accessible': False,
                        'count': 0,
                        'error': str(e)
                    }
        
        except ImportError as e:
            model_checks['import_error'] = str(e)
        
        return model_checks
