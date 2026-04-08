import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import get_user_profile
from notifier import send_welcome_notification, format_welcome_notification_ml, get_top_eligible_schemes

user_id = 'd467a465-8501-49af-b31a-a38601b6c3e1'
user = get_user_profile(user_id)

if user:
    print(f"User: {user.get('name')} ({user.get('phone')})")
    print(f"Language: {user.get('language', 'malayalam')}")
    print()
    
    user_name = user.get('name', '') if user.get('name') else ''
    eligible_schemes = get_top_eligible_schemes(user)
    
    print(f"Eligible schemes: {eligible_schemes}")
    print()
    
    message = format_welcome_notification_ml(user_name, eligible_schemes)
    print("=== MESSAGE ===")
    print(message)
    print("================")
    print()
    
    print("Sending notification...")
    result = send_welcome_notification(user)
    print(f"Result: {result}")
else:
    print("User not found!")
