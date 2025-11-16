"""
Database health check utilities for PostgreSQL
"""
from django.db import connection, connections
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseHealthChecker:
    """Utility class for checking database health and connectivity"""
    
    @staticmethod
    def check_connection(database_alias='default'):
        """
        Check if database connection is working
        
        Args:
            database_alias (str): Database alias to check
            
        Returns:
            tuple: (is_connected, error_message)
        """
        try:
            db_conn = connections[database_alias]
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    return True, "Database connection successful"
                else:
                    return False, "Database query returned unexpected result"
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False, str(e)
    
    @staticmethod
    def check_postgresql_version():
        """
        Check PostgreSQL version
        
        Returns:
            tuple: (version_string, is_supported)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
                # Extract version number
                import re
                version_match = re.search(r'PostgreSQL (\d+\.\d+)', version)
                if version_match:
                    version_num = float(version_match.group(1))
                    is_supported = version_num >= 10.0  # Minimum supported version
                    return version, is_supported
                else:
                    return version, False
        except Exception as e:
            logger.error(f"Failed to check PostgreSQL version: {e}")
            return f"Error: {e}", False
    
    @staticmethod
    def check_database_settings():
        """
        Validate database settings
        
        Returns:
            list: List of validation issues
        """
        issues = []
        
        try:
            db_config = settings.DATABASES['default']
            
            # Check required settings
            required_settings = ['ENGINE', 'NAME', 'USER', 'HOST', 'PORT']
            for setting in required_settings:
                if not db_config.get(setting):
                    issues.append(f"Missing required database setting: {setting}")
            
            # Check engine
            if db_config.get('ENGINE') != 'django.db.backends.postgresql':
                issues.append(f"Expected PostgreSQL engine, got: {db_config.get('ENGINE')}")
            
            # Check port
            port = db_config.get('PORT')
            if port and str(port) != '5432':
                issues.append(f"Non-standard PostgreSQL port: {port}")
            
        except KeyError:
            issues.append("Default database configuration not found")
        except Exception as e:
            issues.append(f"Error checking database settings: {e}")
        
        return issues
    
    @staticmethod
    def check_database_permissions():
        """
        Check if database user has necessary permissions
        
        Returns:
            tuple: (has_permissions, missing_permissions)
        """
        missing_permissions = []
        
        try:
            with connection.cursor() as cursor:
                # Check if user can create tables
                try:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS _health_check_temp (
                            id SERIAL PRIMARY KEY,
                            test_field VARCHAR(50)
                        )
                    """)
                    cursor.execute("DROP TABLE IF EXISTS _health_check_temp")
                except Exception:
                    missing_permissions.append("CREATE TABLE")
                
                # Check if user can insert data
                try:
                    cursor.execute("SELECT 1 FROM auth_user LIMIT 1")
                except Exception:
                    missing_permissions.append("SELECT")
                
                # Check if user can create indexes
                try:
                    cursor.execute("""
                        SELECT has_table_privilege(current_user, 'auth_user', 'INSERT')
                    """)
                    result = cursor.fetchone()
                    if not result or not result[0]:
                        missing_permissions.append("INSERT")
                except Exception:
                    missing_permissions.append("INSERT (check failed)")
        
        except Exception as e:
            logger.error(f"Failed to check database permissions: {e}")
            missing_permissions.append(f"Permission check failed: {e}")
        
        return len(missing_permissions) == 0, missing_permissions
    
    @staticmethod
    def run_full_health_check():
        """
        Run comprehensive database health check
        
        Returns:
            dict: Health check results
        """
        results = {
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Connection check
        is_connected, conn_message = DatabaseHealthChecker.check_connection()
        results['checks']['connection'] = {
            'status': 'pass' if is_connected else 'fail',
            'message': conn_message
        }
        
        if not is_connected:
            results['overall_status'] = 'unhealthy'
            return results
        
        # Version check
        version, is_supported = DatabaseHealthChecker.check_postgresql_version()
        results['checks']['version'] = {
            'status': 'pass' if is_supported else 'warn',
            'message': f"PostgreSQL version: {version}",
            'supported': is_supported
        }
        
        # Settings check
        setting_issues = DatabaseHealthChecker.check_database_settings()
        results['checks']['settings'] = {
            'status': 'pass' if not setting_issues else 'fail',
            'issues': setting_issues
        }
        
        if setting_issues:
            results['overall_status'] = 'unhealthy'
        
        # Permissions check
        has_perms, missing_perms = DatabaseHealthChecker.check_database_permissions()
        results['checks']['permissions'] = {
            'status': 'pass' if has_perms else 'fail',
            'missing_permissions': missing_perms
        }
        
        if not has_perms:
            results['overall_status'] = 'unhealthy'
        
        return results

def validate_database_health():
    """
    Quick function to validate database health
    Raises ImproperlyConfigured if database is not healthy
    """
    health_results = DatabaseHealthChecker.run_full_health_check()
    
    if health_results['overall_status'] == 'unhealthy':
        error_messages = []
        for check_name, check_result in health_results['checks'].items():
            if check_result['status'] == 'fail':
                if 'message' in check_result:
                    error_messages.append(f"{check_name}: {check_result['message']}")
                if 'issues' in check_result:
                    error_messages.extend([f"{check_name}: {issue}" for issue in check_result['issues']])
                if 'missing_permissions' in check_result:
                    error_messages.extend([f"{check_name}: Missing {perm}" for perm in check_result['missing_permissions']])
        
        raise ImproperlyConfigured(
            f"Database health check failed:\n" + "\n".join(error_messages)
        )
    
    return True
