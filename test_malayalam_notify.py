import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import get_user_profile
from notifier import send_welcome_notification

user_id = '2a672f92-f0a9-4f9b-b8ee-2d48295b4eb9'
user = get_user_profile(user_id)

if user:
    print(f"Sending welcome notification to: {user.get('name')} ({user.get('phone')})")
    print(f"Language: {user.get('language', 'malayalam')}")
    print()
    
    from notifier import format_welcome_notification_ml, get_top_eligible_schemes
    user_name = user.get('name', '') if user.get('name') else ''
    eligible_schemes = get_top_eligible_schemes(user)
    message = format_welcome_notification_ml(user_name, eligible_schemes)
    
    with open('malayalam_message.txt', 'w', encoding='utf-8') as f:
        f.write("=== MALAYALAM MESSAGE ===\n\n")
        f.write(message)
        f.write("\n\n===========================\n")
    
    print("Message written to malayalam_message.txt")
    print()
    
    result = send_welcome_notification(user)
    print(f"Result: {result}")
else:
    print("User not found!")
