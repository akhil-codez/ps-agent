import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio

from notification_scheduler import scrape_and_notify

print("=== Testing Scrape and Notify ===")
result = asyncio.run(scrape_and_notify())
print(f"\nResult: {result}")
