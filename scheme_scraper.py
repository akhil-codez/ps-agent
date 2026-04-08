import requests
from bs4 import BeautifulSoup
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv('SERPER_API_KEY', '')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_url(url: str, timeout: int = 30) -> Optional[str]:
    """Fetch URL content"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

def parse_html_table(soup: BeautifulSoup) -> List[Dict]:
    """Parse HTML table to list of dicts"""
    rows = []
    table = soup.find('table')
    if not table:
        return rows
    
    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    
    for tr in table.find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        if cells and len(cells) == len(headers):
            row = dict(zip(headers, cells))
            rows.append(row)
    
    return rows

def scrape_sjd_schemes() -> List[Dict]:
    """Scrape Social Justice Department schemes - sjd.kerala.gov.in"""
    schemes = []
    url = "https://sjd.kerala.gov.in/schemes.php"
    
    html = scrape_url(url)
    if not html:
        logger.warning("Could not scrape SJD website")
        return schemes
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if 'scheme' in text.lower() or 'pension' in text.lower() or 'സ്കീം' in text:
            scheme = {
                'name': text,
                'source': 'sjd.kerala.gov.in',
                'source_url': url,
                'raw_text': text,
                'scraped_at': datetime.now().isoformat()
            }
            
            parent = link.find_parent(['li', 'div', 'tr'])
            if parent:
                scheme['raw_text'] += ' ' + parent.get_text(strip=True)
            
            schemes.append(scheme)
    
    logger.info(f"Scraped {len(schemes)} schemes from SJD")
    return schemes

def scrape_wcd_schemes() -> List[Dict]:
    """Scrape Women & Child Development schemes - wcd.kerala.gov.in"""
    schemes = []
    url = "https://wcd.kerala.gov.in/schemes.php"
    
    html = scrape_url(url)
    if not html:
        logger.warning("Could not scrape WCD website")
        return schemes
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for scheme_div in soup.find_all(['div', 'li'], class_=lambda x: x and ('scheme' in x.lower() if x else False)):
        title_elem = scheme_div.find(['h3', 'h4', 'a'])
        if title_elem:
            name = title_elem.get_text(strip=True)
        else:
            name = scheme_div.get_text(strip=True)[:100]
        
        if name:
            scheme = {
                'name': name,
                'source': 'wcd.kerala.gov.in',
                'source_url': url,
                'raw_text': scheme_div.get_text(strip=True),
                'scraped_at': datetime.now().isoformat()
            }
            schemes.append(scheme)
    
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if text and len(text) > 10 and len(text) < 200:
            if 'scheme' in text.lower() or 'child' in text.lower() or 'women' in text.lower() or 'കുട്ടി' in text:
                scheme = {
                    'name': text,
                    'source': 'wcd.kerala.gov.in',
                    'source_url': url,
                    'raw_text': text,
                    'scraped_at': datetime.now().isoformat()
                }
                if scheme not in schemes:
                    schemes.append(scheme)
    
    logger.info(f"Scraped {len(schemes)} schemes from WCD")
    return schemes

def scrape_egrantz_schemes() -> List[Dict]:
    """Scrape egrantz scholarship schemes - egrantz.kerala.gov.in"""
    schemes = []
    url = "https://egrantz.kerala.gov.in/"
    
    html = scrape_url(url)
    if not html:
        logger.warning("Could not scrape egrantz website")
        return schemes
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for scheme_card in soup.find_all(['div', 'a'], class_=lambda x: x and ('scheme' in x.lower() or 'scholarship' in x.lower() if x else False)):
        name_elem = scheme_card.find(['h3', 'h4', 'h5', 'span', 'a'])
        if name_elem:
            name = name_elem.get_text(strip=True)
        else:
            name = scheme_card.get_text(strip=True)[:100]
        
        if name and len(name) > 5:
            scheme = {
                'name': name,
                'source': 'egrantz.kerala.gov.in',
                'source_url': url,
                'raw_text': scheme_card.get_text(strip=True),
                'scraped_at': datetime.now().isoformat()
            }
            schemes.append(scheme)
    
    links_text = soup.get_text(strip=True)
    if 'scholarship' in links_text.lower():
        for text in links_text.split('\n'):
            if 'scholarship' in text.lower() and len(text) > 10 and len(text) < 200:
                scheme = {
                    'name': text.strip(),
                    'source': 'egrantz.kerala.gov.in',
                    'source_url': url,
                    'raw_text': text.strip(),
                    'scraped_at': datetime.now().isoformat()
                }
                if scheme not in schemes:
                    schemes.append(scheme)
    
    logger.info(f"Scraped {len(schemes)} schemes from egrantz")
    return schemes

def scrape_karunya_schemes() -> List[Dict]:
    """Scrape Karunya health schemes - karunya.kerala.gov.in"""
    schemes = []
    url = "https://karunya.kerala.gov.in/"
    
    html = scrape_url(url)
    if not html:
        logger.warning("Could not scrape Karunya website")
        return schemes
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if text and len(text) > 5:
            if any(kw in text.lower() for kw in ['health', 'karunya', 'medical', 'scheme', 'കരുത്ത്']):
                parent = link.find_parent(['li', 'div'])
                raw = parent.get_text(strip=True) if parent else text
                
                scheme = {
                    'name': text[:200],
                    'source': 'karunya.kerala.gov.in',
                    'source_url': url,
                    'raw_text': raw[:1000],
                    'scraped_at': datetime.now().isoformat()
                }
                if scheme not in schemes:
                    schemes.append(scheme)
    
    logger.info(f"Scraped {len(schemes)} schemes from Karunya")
    return schemes

def scrape_akshaya_schemes() -> List[Dict]:
    """Scrape Akshaya portal schemes - akshaya.kerala.gov.in"""
    schemes = []
    url = "http://akshaya.kerala.gov.in/"
    
    html = scrape_url(url)
    if not html:
        logger.warning("Could not scrape Akshaya website")
        return schemes
    
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        text = link.get_text(strip=True)
        if text and len(text) > 5:
            parent = link.find_parent(['li', 'div'])
            raw = parent.get_text(strip=True) if parent else text
            
            scheme = {
                'name': text[:200],
                'source': 'akshaya.kerala.gov.in',
                'source_url': url,
                'raw_text': raw[:1000],
                'scraped_at': datetime.now().isoformat()
            }
            if scheme not in schemes:
                schemes.append(scheme)
    
    logger.info(f"Scraped {len(schemes)} schemes from Akshaya")
    return schemes

def search_new_schemes_with_serper() -> List[Dict]:
    """Search for new Kerala government schemes using Serper API"""
    schemes = []
    
    if not SERPER_API_KEY:
        logger.warning("SERPER_API_KEY not configured")
        return schemes
    
    search_queries = [
        "site:kerala.gov.in scheme 2024 eligibility",
        "site:sjd.kerala.gov.in pension scheme",
        "site:wcd.kerala.gov.in scheme women children",
        "Kerala government welfare scheme 2024",
        "Kerala state scheme BPL APL card",
    ]
    
    for query in search_queries:
        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
                json={'q': query, 'num': 10},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('organic', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    
                    if title and len(title) > 10:
                        scheme = {
                            'name': title,
                            'source': 'Serper Search',
                            'source_url': link,
                            'raw_text': f"{title}\n{snippet}",
                            'scraped_at': datetime.now().isoformat()
                        }
                        schemes.append(scheme)
                        
        except Exception as e:
            logger.error(f"Serper search error for query '{query}': {e}")
    
    logger.info(f"Found {len(schemes)} schemes via Serper search")
    return schemes

def deduplicate_schemes(schemes: List[Dict]) -> List[Dict]:
    """Remove duplicate schemes based on name similarity"""
    seen = set()
    unique = []
    
    for scheme in schemes:
        name = scheme.get('name', '').lower().strip()
        name_normalized = ' '.join(name.split())
        
        if name_normalized and name_normalized not in seen:
            seen.add(name_normalized)
            unique.append(scheme)
    
    return unique

def scrape_all_sources() -> List[Dict]:
    """Scrape all sources and combine results"""
    print("[SCRAPER] Starting scrape of all sources...")
    
    all_schemes = []
    
    print("[SCRAPER] Scraping SJD (Social Justice)...")
    all_schemes.extend(scrape_sjd_schemes())
    
    print("[SCRAPER] Scraping WCD (Women & Child)...")
    all_schemes.extend(scrape_wcd_schemes())
    
    print("[SCRAPER] Scraping egrantz (Scholarships)...")
    all_schemes.extend(scrape_egrantz_schemes())
    
    print("[SCRAPER] Scraping Karunya (Health)...")
    all_schemes.extend(scrape_karunya_schemes())
    
    # Removed Akshaya - scrapes navigation links, not actual schemes
    # print("[SCRAPER] Scraping Akshaya...")
    # all_schemes.extend(scrape_akshaya_schemes())
    
    print("[SCRAPER] Searching with Serper API...")
    all_schemes.extend(search_new_schemes_with_serper())
    
    print(f"[SCRAPER] Total raw schemes: {len(all_schemes)}")
    
    unique_schemes = deduplicate_schemes(all_schemes)
    print(f"[SCRAPER] After deduplication: {len(unique_schemes)} schemes")
    
    return unique_schemes

def save_scraped_schemes(schemes: List[Dict], filename: str = 'scraped_schemes_raw.json'):
    """Save scraped schemes to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schemes, f, ensure_ascii=False, indent=2)
    print(f"[SCRAPER] Saved {len(schemes)} schemes to {filename}")

def load_scraped_schemes(filename: str = 'scraped_schemes_raw.json') -> List[Dict]:
    """Load previously scraped schemes"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    print("=== Scheme Scraper Test ===")
    
    schemes = scrape_all_sources()
    print(f"\nTotal schemes found: {len(schemes)}")
    
    if schemes:
        print("\nSample schemes:")
        for s in schemes[:5]:
            print(f"  - {s.get('name', 'Unknown')[:80]}")
            print(f"    Source: {s.get('source', 'Unknown')}")
    
    save_scraped_schemes(schemes)
