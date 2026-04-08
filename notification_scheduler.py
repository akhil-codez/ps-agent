import logging
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import notifier
import database
import eligibility
from eligibility import RULES, summarize_criteria_en, summarize_criteria_ml

logger = logging.getLogger(__name__)

scheduler_instance = None

def normalize_scheme_name(name: str) -> str:
    """Normalize scheme name for matching"""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = name.replace(' ', '_')
    return name

def enrich_scheme_from_rules(scheme: dict) -> dict:
    """Enrich scheme with criteria/docs from eligibility_rules.json"""
    scheme_name = scheme.get('name', '')
    scheme_name_lower = scheme_name.lower()
    scheme_key = normalize_scheme_name(scheme_name)
    
    # Generic fallback for Kerala government schemes
    generic_docs_en = "Aadhaar, Income certificate, Caste certificate (if applicable), Bank account, Passport photo"
    generic_docs_ml = "ആധാർ, വരുമാന സർട്ടിഫിക്കറ്റ്, ജാതി സർട്ടിഫിക്കറ്റ് (ബാധ്യതയുണ്ടെങ്കിൽ), ബാങ്ക് അക്കൗണ്ട്, പാസ്‌പോർട്ട് ഫോട്ടോ"
    generic_criteria_en = "Income below ₹1 lakh; Kerala resident; Age 18+"
    generic_criteria_ml = "വരുമാനം ₹1 ലക്ഷത്തിൽ കുറവ്; കേരള സ്വദേശി; വയസ്സ് 18+"
    
    # Try exact match first
    if scheme_key in RULES:
        rule = RULES[scheme_key]
        return {
            **scheme,
            'benefit': rule.get('benefit', scheme.get('benefit', '')),
            'criteria_summary_en': summarize_criteria_en(rule),
            'criteria_summary_ml': summarize_criteria_ml(rule),
            'documents': ', '.join(rule.get('documents_needed', [])[:5]) if rule.get('documents_needed') else generic_docs_en,
            'documents_list': rule.get('documents_needed', [])[:5] if rule.get('documents_needed') else [],
            'portal': rule.get('application_portal', notifier.get_portal_for_scheme(scheme_name)),
        }
    
    # Try multiple matching strategies
    best_match = None
    best_score = 0
    
    for key, rule in RULES.items():
        rule_name = rule.get('name', '').lower()
        
        # Strategy 1: Check if scheme name contains rule name or vice versa
        if scheme_name_lower in rule_name or rule_name in scheme_name_lower:
            score = 10
        else:
            # Strategy 2: Word overlap
            key_words = set(key.replace('_', ' ').split())
            scheme_words = set(re.sub(r'[^\w\s]', '', scheme_name_lower).split())
            overlap = len(key_words & scheme_words)
            score = overlap * 2
        
        # Strategy 3: Keyword matching
        keywords = ['pension', 'social', 'security', 'sevana', 'kerala', 'government', 'health', 'education', 'housing', 'scholarship']
        for kw in keywords:
            if kw in scheme_name_lower and kw in rule_name:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = rule
    
    if best_match and best_score >= 3:
        return {
            **scheme,
            'benefit': best_match.get('benefit', scheme.get('benefit', '')),
            'criteria_summary_en': summarize_criteria_en(best_match),
            'criteria_summary_ml': summarize_criteria_ml(best_match),
            'documents': ', '.join(best_match.get('documents_needed', [])[:5]) if best_match.get('documents_needed') else generic_docs_en,
            'documents_list': best_match.get('documents_needed', [])[:5] if best_match.get('documents_needed') else [],
            'portal': best_match.get('application_portal', notifier.get_portal_for_scheme(scheme_name)),
        }
    
    # Return enriched with generic fallbacks if no match
    return {
        **scheme,
        'benefit': scheme.get('benefit', 'Check official website'),
        'criteria_summary_en': generic_criteria_en,
        'criteria_summary_ml': generic_criteria_ml,
        'documents': generic_docs_en,
        'portal': scheme.get('portal', notifier.get_portal_for_scheme(scheme_name)),
    }

def get_eligible_schemes_for_user(user: dict) -> list:
    """Get list of schemes user is eligible for"""
    house_ownership = user.get('house_ownership', '')
    vehicle_type = user.get('vehicle_type', 'none')
    marital_status = user.get('marital_status', '')
    employment_status = user.get('employment_status', '')
    education_level = user.get('education_level', '')
    is_urban = user.get('is_urban', False)
    has_health_insurance = user.get('has_health_insurance', False)
    
    profile = {
        'income': user.get('income'),
        'age': user.get('age'),
        'category': user.get('category'),
        'family_size': user.get('family_size'),
        'district': user.get('district'),
        'kerala_resident': True,
        'has_bpl_card': user.get('category') == 'BPL',
        'has_aadhaar': True,
        'has_bank_account': True,
        'is_rural': not is_urban,
        'is_urban': is_urban,
        'has_family': True,
        'is_widowed': marital_status == 'widowed',
        'has_disability_cert': user.get('has_disability_cert', False),
        'is_artisan': user.get('is_artisan', False),
        'is_student': education_level in ['higher_secondary', 'graduate', 'post_graduate'] if education_level else False,
        'willing_for_manual_work': True,
        'has_private_insurance': has_health_insurance,
        'receives_other_pension': user.get('receives_other_pension', False),
        'remarried': user.get('remarried', False),
        'owns_4_wheeler': vehicle_type in ['four_wheeler', 'both'],
        'government_employee': employment_status == 'govt_employee',
        'has_pucca_house': house_ownership == 'owned',
        'is_food_business': user.get('is_food_business', False),
        'income_above_100000': user.get('income', 0) > 100000,
        'income_above_300000': user.get('income', 0) > 300000,
        'income_above_500000': user.get('income', 0) > 500000,
        'age_below_60': user.get('age', 0) < 60,
        'age_below_18': user.get('age', 0) < 18,
    }
    
    eligible = []
    
    for scheme_key, rule in RULES.items():
        result = eligibility.check_eligibility(rule['name'], profile)
        if result['eligible'] is True:
            eligible.append({
                'name': rule['name'],
                'benefit': rule.get('benefit', ''),
                'portal': rule.get('application_portal', ''),
                'description': rule.get('description', ''),
                'criteria_summary_en': summarize_criteria_en(rule),
                'criteria_summary_ml': summarize_criteria_ml(rule),
                'documents': ', '.join(rule.get('documents_needed', [])[:5]),
            })
    
    return eligible

async def send_daily_digest():
    """Daily job: Send digest of eligible schemes to all users"""
    logger.info(f"[{datetime.now()}] Starting daily digest...")
    
    users = database.get_all_users_for_notifications()
    logger.info(f"Processing {len(users)} users")
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            eligible_schemes = get_eligible_schemes_for_user(user)
            
            if eligible_schemes:
                result = notifier.notify_user_daily_digest(user, eligible_schemes)
                if result['success']:
                    sent += 1
                else:
                    failed += 1
            else:
                logger.info(f"No eligible schemes for user {user.get('user_id')}")
        except Exception as e:
            logger.error(f"Error processing user {user.get('user_id')}: {str(e)}")
            failed += 1
    
    logger.info(f"[{datetime.now()}] Daily digest complete: {sent} sent, {failed} failed")
    return {'sent': sent, 'failed': failed, 'total': len(users)}

async def send_instant_notification(scheme_name: str):
    """Send instant notification about a specific scheme"""
    logger.info(f"[{datetime.now()}] Sending instant notification for: {scheme_name}")
    
    scheme_key = scheme_name.lower().replace(' ', '_').replace('-', '_')
    
    if scheme_key not in RULES:
        logger.error(f"Scheme not found: {scheme_name}")
        return {'success': False, 'error': 'Scheme not found'}
    
    rule = RULES[scheme_key]
    scheme = {
        'name': rule['name'],
        'benefit': rule.get('benefit', ''),
        'portal': rule.get('application_portal', ''),
        'description': rule.get('description', ''),
    }
    
    result = notifier.broadcast_to_eligible_users(scheme)
    logger.info(f"Instant notification result: {result}")
    
    return {'success': True, **result}

async def notify_all_schemes():
    """Notify about all schemes to all eligible users (one-time broadcast)"""
    logger.info(f"[{datetime.now()}] Starting broadcast for all schemes...")
    
    total_sent = 0
    total_failed = 0
    
    for scheme_key, rule in RULES.items():
        scheme = {
            'name': rule['name'],
            'benefit': rule.get('benefit', ''),
            'portal': rule.get('application_portal', ''),
            'description': rule.get('description', ''),
        }
        
        result = notifier.broadcast_to_eligible_users(scheme)
        total_sent += result['sent']
        total_failed += result['failed']
        logger.info(f"  {rule['name']}: {result['sent']} sent, {result['failed']} failed")
    
    logger.info(f"[{datetime.now()}] All schemes broadcast complete: {total_sent} sent, {total_failed} failed")
    return {'sent': total_sent, 'failed': total_failed}

def setup_scheduler():
    """Initialize and start the APScheduler"""
    global scheduler_instance
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = AsyncIOScheduler()
        
        scheduler.add_job(
            send_daily_digest,
            CronTrigger(hour=2, minute=30, timezone='UTC'),
            id='daily_digest',
            name='Daily Scheme Digest'
        )
        
        scheduler.start()
        scheduler_instance = scheduler
        
        logger.info("Notification scheduler started")
        logger.info("Daily digest scheduled at 2:30 AM UTC (8:00 AM IST)")
        
        return scheduler
        
    except ImportError:
        logger.warning("APScheduler not installed. Run: pip install apscheduler")
        logger.info("Daily notifications will not run automatically.")
        return None

def get_scheduler_status() -> dict:
    """Get current scheduler status"""
    if scheduler_instance is None:
        return {
            'running': False,
            'reason': 'Scheduler not initialized or APScheduler not installed'
        }
    
    jobs = scheduler_instance.get_jobs()
    return {
        'running': scheduler_instance.running,
        'jobs': [
            {
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None
            }
            for job in jobs
        ]
    }

def trigger_daily_digest_now():
    """Manually trigger daily digest (for testing)"""
    import asyncio
    return asyncio.run(send_daily_digest())

def trigger_instant_notification(scheme_name: str):
    """Manually trigger instant notification (for testing)"""
    import asyncio
    return asyncio.run(send_instant_notification(scheme_name))

def trigger_broadcast_all():
    """Manually trigger broadcast for all schemes (for testing)"""
    import asyncio
    return asyncio.run(notify_all_schemes())

async def scrape_and_notify():
    """Main workflow: Scrape schemes, add to rules, notify users about NEW schemes only"""
    print("[SCHEDULER] Starting scrape and notify cycle...")
    
    try:
        import scheme_scraper
        import eligibility_extractor
        import json
        from datetime import datetime
        
        print("[SCHEDULER] Step 1: Scraping all sources...")
        raw_schemes = scheme_scraper.scrape_all_sources()
        print(f"[SCHEDULER] Scraped {len(raw_schemes)} raw schemes")
        
        # Load previous schemes to compare
        prev_schemes_file = 'scraped_schemes_prev.json'
        try:
            with open(prev_schemes_file, 'r', encoding='utf-8') as f:
                prev_schemes = json.load(f)
                prev_names = set(s.get('name', '').lower() for s in prev_schemes)
        except:
            prev_names = set()
        
        if raw_schemes:
            print("[SCHEDULER] Step 2: Processing and adding new schemes...")
            added = eligibility_extractor.add_all_new_schemes(raw_schemes)
            print(f"[SCHEDULER] Added {added} new schemes")
            
            print("[SCHEDULER] Step 3: Reloading eligibility rules...")
            eligibility.reload_rules()
            print(f"[SCHEDULER] Total rules now: {len(eligibility.RULES)}")
        
        # Find NEW schemes (not in previous scrape)
        new_schemes = []
        for scheme in eligibility.RULES.values():
            scheme_name_lower = scheme.get('name', '').lower()
            if scheme_name_lower not in prev_names:
                new_schemes.append(scheme)
        
        print(f"[SCHEDULER] Found {len(new_schemes)} NEW schemes (not in previous scrape)")
        
        # Save current schemes for next comparison
        with open(prev_schemes_file, 'w', encoding='utf-8') as f:
            json.dump(raw_schemes, f, ensure_ascii=False, indent=2)
        
        print("[SCHEDULER] Step 4: Checking all users for eligibility (NEW schemes only)...")
        users = database.get_all_users_full_profile()
        print(f"[SCHEDULER] Processing {len(users)} users")
        
        total_notifications = 0
        
        for user in users:
            try:
                if not new_schemes:
                    print(f"[SCHEDULER] No new schemes to notify for user {user.get('phone')}")
                    continue
                
                # Filter to only eligible NEW schemes
                eligible_new = []
                for scheme in new_schemes:
                    # Quick eligibility check
                    conditions = scheme.get('conditions', {})
                    
                    # Check income
                    income_max = conditions.get('annual_income_max', 999999999)
                    user_income = user.get('income', 0)
                    if user_income > income_max and income_max < 999999999:
                        continue
                    
                    # Check age
                    age_min = conditions.get('age_min', 0)
                    user_age = user.get('age', 0)
                    if user_age < age_min:
                        continue
                    
                    # Check 7-day dedup
                    if notifier.was_notified_recently(user['user_id'], scheme['name'], days=7):
                        continue
                    
                    eligible_new.append(scheme)
                
                if not eligible_new:
                    print(f"[SCHEDULER] No eligible new schemes for user {user.get('phone')}")
                    continue
                
                # Send top 3-5 most relevant NEW schemes
                top_new = notifier.get_top_schemes_for_user(user, eligible_new, limit=5)
                
                # Enrich schemes with criteria/docs from rules
                enriched_schemes = [enrich_scheme_from_rules(s) for s in top_new]
                
                print(f"[SCHEDULER] User {user.get('phone')}: {len(eligible_new)} eligible new, sending top {len(enriched_schemes)}")
                
                result = notifier.send_eligibility_batch(user, enriched_schemes)
                if result.get('success'):
                    total_notifications += 1
                
            except Exception as e:
                print(f"[SCHEDULER] Error processing user {user.get('user_id')}: {e}")
                continue
        
        print(f"[SCHEDULER] Cycle complete! Sent {total_notifications} notifications")
        return {'success': True, 'users_notified': total_notifications, 'new_schemes': len(new_schemes)}
        
    except Exception as e:
        print(f"[SCHEDULER] Error in scrape and notify cycle: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def trigger_scrape_and_notify_now():
    """Manually trigger scrape and notify (for testing/admin)"""
    import asyncio
    return asyncio.run(scrape_and_notify())

def setup_scheduler():
    """Initialize and start the APScheduler"""
    global scheduler_instance
    
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = AsyncIOScheduler()
        
        scheduler.add_job(
            send_daily_digest,
            CronTrigger(hour=2, minute=30, timezone='UTC'),
            id='daily_digest',
            name='Daily Scheme Digest'
        )
        
        scheduler.add_job(
            scrape_and_notify,
            CronTrigger(hour=8, minute=0, timezone='Asia/Kolkata'),
            id='morning_scrape_notify',
            name='Morning Scrape & Notify (8 AM IST)'
        )
        
        scheduler.add_job(
            scrape_and_notify,
            CronTrigger(hour=15, minute=15, timezone='Asia/Kolkata'),
            id='afternoon_scrape_notify',
            name='Afternoon Scrape & Notify (3:15 PM IST)'
        )
        
        scheduler.start()
        scheduler_instance = scheduler
        
        logger.info("Notification scheduler started")
        logger.info("Jobs scheduled:")
        logger.info("  - Daily digest at 2:30 AM UTC (8:00 AM IST)")
        logger.info("  - Morning scrape & notify at 8:00 AM IST")
        logger.info("  - Afternoon scrape & notify at 3:15 PM IST")
        
        return scheduler
        
    except ImportError:
        logger.warning("APScheduler not installed. Run: pip install apscheduler")
        logger.info("Daily notifications will not run automatically.")
        return None
    logging.basicConfig(level=logging.INFO)
    
    print("=== Notification Scheduler Test ===")
    print("1. Trigger instant notification for BPL Ration Card")
    print("2. Trigger broadcast for all schemes")
    print("3. Get scheduler status")
    
    choice = input("Enter choice: ").strip()
    
    if choice == "1":
        result = trigger_instant_notification("BPL Ration Card")
        print(f"Result: {result}")
    elif choice == "2":
        result = trigger_broadcast_all()
        print(f"Result: {result}")
    elif choice == "3":
        print(f"Status: {get_scheduler_status()}")
