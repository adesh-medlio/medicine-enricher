"""
Medicine Data Enrichment Pipeline
Enriches Excel file with medicine data from 1mg.com via Google search
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import quote_plus, urlparse
import logging
import os
import tempfile
import shutil
from datetime import datetime
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SafeExcelSaver:
    """Corruption-proof Excel file saver"""
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.temp_dir = tempfile.mkdtemp()
        
    def safe_save(self, df, progress_count=None):
        """
        Safely save DataFrame to Excel with corruption protection.
        Uses atomic operations to prevent corruption.
        """
        try:
            # Create unique temporary file
            temp_filename = f"temp_save_{int(time.time())}_{os.getpid()}.xlsx"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            
            logger.info(f"Saving to temporary file: {temp_filename}")
            
            # Save to temporary location first
            df.to_excel(temp_path, index=False)
            
            # Verify the temporary file is valid and complete
            try:
                test_df = pd.read_excel(temp_path)
                if len(test_df) != len(df):
                    raise ValueError(f"Row count mismatch: expected {len(df)}, got {len(test_df)}")
                if len(test_df.columns) != len(df.columns):
                    raise ValueError(f"Column count mismatch: expected {len(df.columns)}, got {len(test_df.columns)}")
                logger.info(f"✅ Temporary file validated: {len(test_df)} rows, {len(test_df.columns)} columns")
            except Exception as e:
                logger.error(f"❌ Temporary file validation failed: {e}")
                return False
            
            # Create timestamped backup of existing file if it exists
            if os.path.exists(self.output_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.output_path.replace('.xlsx', f'_backup_{timestamp}.xlsx')
                try:
                    shutil.copy2(self.output_path, backup_path)
                    logger.info(f"📁 Previous version backed up: {os.path.basename(backup_path)}")
                except Exception as e:
                    logger.warning(f"Could not create backup: {e}")
            
            # Atomic move from temp to final location (this prevents corruption)
            shutil.move(temp_path, self.output_path)
            logger.info(f"✅ File saved successfully: {os.path.basename(self.output_path)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Save failed: {e}")
            
            # Emergency backup with progress count
            if progress_count is not None:
                emergency_path = self.output_path.replace('.xlsx', f'_emergency_{progress_count}_{int(time.time())}.xlsx')
                try:
                    df.to_excel(emergency_path, index=False)
                    logger.info(f"💾 Emergency backup saved: {os.path.basename(emergency_path)}")
                    return True
                except Exception as backup_error:
                    logger.error(f"❌ Emergency backup also failed: {backup_error}")
            
            return False
    
    def cleanup(self):
        """Clean up temporary directory"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Could not clean up temp directory: {e}")

class MedicineEnricher:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.saver = None
        self.current_df = None
        self.shutdown_requested = False
        
        # Set up graceful shutdown handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.warning(f"🛑 Shutdown signal received ({signum}). Saving current progress...")
        self.shutdown_requested = True
        
        if self.saver and self.current_df is not None:
            logger.info("💾 Emergency save in progress...")
            emergency_path = f"emergency_save_{int(time.time())}.xlsx"
            try:
                self.current_df.to_excel(emergency_path, index=False)
                logger.info(f"✅ Emergency save completed: {emergency_path}")
            except Exception as e:
                logger.error(f"❌ Emergency save failed: {e}")
        
        logger.info("🔄 Cleaning up...")
        if self.saver:
            self.saver.cleanup()
        
        logger.info("👋 Shutdown complete. Your progress has been saved.")
        sys.exit(0)
        
    def google_search_1mg(self, medicine_name, manufacturer_name=None):
        """
        Search for medicine on 1mg.com using multiple strategies
        Returns the first valid 1mg URL or None
        """
        try:
            # Clean medicine name for search
            clean_name = medicine_name.strip()
            
            # Strategy 1: Try direct 1mg search first (often more accurate)
            logger.info(f"Trying direct 1mg search first for: {clean_name}")
            direct_result = self._try_direct_1mg_search(clean_name, manufacturer_name)
            if direct_result:
                return direct_result
            
            # Strategy 2: Google search as fallback
            logger.info(f"Direct search failed, trying Google search for: {clean_name}")
            
            # Try multiple search strategies with manufacturer if available
            search_queries = []
            
            if manufacturer_name and manufacturer_name.strip():
                clean_manufacturer = manufacturer_name.strip()
                # More specific searches with manufacturer - exact match priority
                search_queries.extend([
                    f'site:1mg.com/drugs "{clean_name}" "{clean_manufacturer}" -substitute -alternative',
                    f'site:1mg.com "{clean_name}" "{clean_manufacturer}"',
                    f'1mg.com "{clean_name}" "{clean_manufacturer}" -substitute',
                    f'site:1mg.com/drugs "{clean_name}" {clean_manufacturer}',
                ])
            
            # Fallback searches without manufacturer - also prioritize exact matches
            search_queries.extend([
                f'site:1mg.com/drugs "{clean_name}" -substitute -alternative',
                f'site:1mg.com "{clean_name}" drugs -substitute',
                f'1mg.com "{clean_name}"'
            ])
            
            for search_query in search_queries:
                logger.info(f"Trying search: {search_query}")
                
                encoded_query = quote_plus(search_query)
                google_url = f"https://www.google.com/search?q={encoded_query}&num=10"
                
                # Add more realistic headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(google_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Debug: Save response to check what we're getting
                logger.debug(f"Response status: {response.status_code}")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Multiple strategies to find links
                found_urls = []
                
                # Strategy 1: Look for direct links in href attributes
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Extract actual URL from Google redirect
                    if '/url?q=' in href:
                        try:
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                            from urllib.parse import unquote
                            actual_url = unquote(actual_url)
                            
                            if self._is_valid_1mg_url(actual_url, clean_name):
                                found_urls.append(actual_url)
                        except:
                            continue
                    
                    # Direct 1mg links
                    elif '1mg.com' in href and '/drugs/' in href:
                        if self._is_valid_1mg_url(href, clean_name):
                            found_urls.append(href)
                
                # Strategy 2: Look in text content for URLs
                page_text = soup.get_text()
                import re
                url_pattern = r'https?://(?:www\.)?1mg\.com/drugs/[^\s<>"\']*'
                text_urls = re.findall(url_pattern, page_text)
                
                for url in text_urls:
                    if self._is_valid_1mg_url(url, clean_name):
                        found_urls.append(url)
                
                # Return first valid URL found
                if found_urls:
                    best_url = found_urls[0]
                    logger.info(f"Found valid 1mg URL: {best_url}")
                    return best_url
                
                # Add delay between search attempts
                time.sleep(2)
            
            # If no URL found with Google search, try direct 1mg search again with different approach
            logger.warning(f"Google search failed to find valid URL for: {clean_name}")
            return None
            
        except Exception as e:
            logger.error(f"Google search failed for {medicine_name}: {str(e)}")
            return self._try_direct_1mg_search(medicine_name, manufacturer_name)
    
    def _try_direct_1mg_search(self, medicine_name, manufacturer_name=None):
        """
        Try searching directly on 1mg.com as primary method
        """
        try:
            logger.info(f"Trying direct 1mg search for: {medicine_name}")
            
            # Create multiple search queries to try
            search_queries = []
            
            if manufacturer_name and manufacturer_name.strip():
                clean_manufacturer = manufacturer_name.strip()
                logger.info(f"Including manufacturer in search: {clean_manufacturer}")
                
                # Try with manufacturer first
                search_queries.extend([
                    f"{medicine_name} {clean_manufacturer}",
                    f"{medicine_name}",  # Fallback without manufacturer
                ])
            else:
                search_queries = [medicine_name]
            
            # Try each search query
            for search_query in search_queries:
                logger.info(f"Trying 1mg search query: {search_query}")
                
                # 1mg search URL
                search_url = f"https://www.1mg.com/search/all?name={quote_plus(search_query)}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.1mg.com/',
                }
                
                response = requests.get(search_url, headers=headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for drug links in search results - prioritize exact matches
                found_urls = []
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/drugs/'):
                        full_url = f"https://www.1mg.com{href}"
                        if self._is_valid_1mg_url(full_url, medicine_name):
                            found_urls.append(full_url)
                    elif self._is_valid_1mg_url(href, medicine_name):
                        found_urls.append(href)
                
                # If we found URLs, prioritize the best match
                if found_urls:
                    # Sort URLs by how well they match the medicine name
                    def url_match_score(url):
                        url_lower = url.lower()
                        medicine_words = medicine_name.lower().replace(' ', '-').split('-')
                        score = 0
                        for word in medicine_words:
                            if len(word) > 2 and word in url_lower:
                                score += len(word)  # Longer words get higher score
                        return score
                    
                    # Sort by match score (highest first)
                    found_urls.sort(key=url_match_score, reverse=True)
                    
                    best_url = found_urls[0]
                    match_score = url_match_score(best_url)
                    
                    logger.info(f"Found {len(found_urls)} URLs, best match (score {match_score}): {best_url}")
                    
                    # If we have a good match score, return it
                    if match_score > 0:
                        return best_url
                    else:
                        logger.warning(f"Low match score ({match_score}) for URL: {best_url}")
                        # Continue to try next search query
                
                # Add delay between search attempts
                time.sleep(1)
            
            logger.warning(f"No valid 1mg URL found via direct search for: {medicine_name}")
            return None
            
        except Exception as e:
            logger.error(f"Direct 1mg search failed for {medicine_name}: {str(e)}")
            return None
    
    def _is_valid_1mg_url(self, url, medicine_name=None):
        """Validate if URL is a valid 1mg medicine page and matches the medicine name"""
        try:
            from urllib.parse import unquote
            url = unquote(url)  # Decode URL encoding
            
            parsed = urlparse(url)
            
            # Check domain and path
            valid_domain = parsed.netloc in ['www.1mg.com', '1mg.com']
            valid_path = '/drugs/' in parsed.path
            reasonable_length = len(parsed.path) > 10
            
            # Additional checks to avoid invalid URLs
            not_search = 'search' not in parsed.path.lower()
            not_category = 'category' not in parsed.path.lower()
            not_substitute = 'substitute' not in parsed.path.lower()
            
            basic_valid = valid_domain and valid_path and reasonable_length and not_search and not_category and not_substitute
            
            # If we have medicine name, check if URL contains similar words
            if basic_valid and medicine_name:
                url_path = parsed.path.lower()
                medicine_words = medicine_name.lower().replace('tablet', '').replace('capsule', '').split()
                
                # Check if at least some key words from medicine name appear in URL
                medicine_key_words = [word for word in medicine_words if len(word) > 3 and word not in ['tablet', 'capsule', 'syrup', 'drops']]
                
                if medicine_key_words:
                    # Count how many key words appear in URL
                    matches = sum(1 for word in medicine_key_words if word in url_path)
                    match_ratio = matches / len(medicine_key_words)
                    
                    # If less than 30% of key words match, this might be wrong medicine
                    if match_ratio < 0.3:
                        logger.debug(f"URL word match ratio too low ({match_ratio:.2f}) for {medicine_name}: {url}")
                        return False
            
            if basic_valid:
                logger.debug(f"Valid 1mg URL: {url}")
            else:
                logger.debug(f"Invalid 1mg URL: {url} (domain: {valid_domain}, path: {valid_path}, length: {reasonable_length})")
            
            return basic_valid
            
        except Exception as e:
            logger.debug(f"URL validation error for {url}: {str(e)}")
            return False
    
    def fetch_1mg_page(self, url):
        """
        Fetch and parse 1mg medicine page
        Returns raw HTML content for targeted scraping
        """
        try:
            logger.info(f"Fetching page: {url}")
            
            # Use shorter timeout and retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, timeout=10)  # Reduced timeout
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        logger.error(f"Page fetch timed out after {max_retries} attempts")
                        return None
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Error on attempt {attempt + 1}: {str(e)}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        raise
            
            # Return raw HTML content for targeted scraping
            logger.info(f"Successfully fetched page content ({len(response.content)} bytes)")
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to fetch page {url}: {str(e)}")
            return None
    
    def extract_targeted_data(self, soup, medicine_name, manufacturer_name=None):
        """
        Extract data directly from HTML using targeted scraping
        Returns dict with extracted fields or None
        """
        try:
            logger.info(f"Attempting targeted extraction for: {medicine_name}")
            
            extracted_data = {}
            
            # First, validate we're on the right medicine page
            page_title = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
            if page_title:
                found_medicine_name = page_title.get_text().strip()
                extracted_data['found_medicine_name'] = found_medicine_name
                
                # Enhanced similarity check
                medicine_words = set(word.lower() for word in medicine_name.lower().split() if len(word) > 2)
                found_words = set(word.lower() for word in found_medicine_name.lower().split() if len(word) > 2)
                
                # Remove common words that don't help with matching
                common_words = {'tablet', 'capsule', 'syrup', 'drops', 'mg', 'gm', 'ml', 'strip', 'bottle'}
                medicine_words = medicine_words - common_words
                found_words = found_words - common_words
                
                # Calculate overlap
                if medicine_words:
                    common_words_found = medicine_words.intersection(found_words)
                    similarity = len(common_words_found) / len(medicine_words)
                    
                    logger.info(f"Found medicine: '{found_medicine_name}' (similarity: {similarity:.2f})")
                    logger.info(f"Expected words: {medicine_words}")
                    logger.info(f"Found words: {found_words}")
                    logger.info(f"Common words: {common_words_found}")
                    
                    # If similarity is too low, this might be wrong medicine
                    if similarity < 0.4:  # Increased threshold
                        logger.warning(f"LOW SIMILARITY between searched '{medicine_name}' and found '{found_medicine_name}'")
                        extracted_data['similarity_warning'] = f"Low similarity: {similarity:.2f} - Possible wrong medicine!"
                        
                        # If similarity is very low, reject this result
                        if similarity < 0.2:
                            logger.error(f"REJECTING result due to very low similarity: {similarity:.2f}")
                            return None
                else:
                    similarity = 0.0
                    logger.warning(f"No meaningful words to compare for: {medicine_name}")
                    extracted_data['similarity_warning'] = "No meaningful words to compare"
            
            # Extract manufacturer from the page to verify
            marketer_sections = soup.find_all('div', class_='DrugHeader__meta___B3BcU')
            for section in marketer_sections:
                title_elem = section.find('div', class_='DrugHeader__meta-title___22zXC')
                if title_elem and 'marketer' in title_elem.get_text().lower():
                    value_elem = section.find('div', class_='DrugHeader__meta-value___vqYM0')
                    if value_elem:
                        found_manufacturer = value_elem.get_text().strip()
                        extracted_data['found_manufacturer'] = found_manufacturer
                        
                        # If we have expected manufacturer, check if it matches
                        if manufacturer_name:
                            if manufacturer_name.lower() not in found_manufacturer.lower():
                                logger.warning(f"Manufacturer mismatch: expected '{manufacturer_name}', found '{found_manufacturer}'")
                                extracted_data['manufacturer_warning'] = f"Expected: {manufacturer_name}, Found: {found_manufacturer}"
                        break
            
            # Extract salt composition using consistent class
            salt_elem = soup.find('div', class_='saltInfo')
            if salt_elem:
                # Get text and clean it
                salt_text = salt_elem.get_text().strip()
                # Remove any extra whitespace and newlines
                salt_text = ' '.join(salt_text.split())
                extracted_data['salt_composition'] = salt_text
                logger.info(f"Found salt composition via targeted scraping: {salt_text[:50]}...")
            else:
                # Fallback: look for salt composition in meta sections
                meta_sections = soup.find_all('div', class_='DrugHeader__meta___B3BcU')
                for section in meta_sections:
                    title_elem = section.find('div', class_='DrugHeader__meta-title___22zXC')
                    if title_elem and 'SALT COMPOSITION' in title_elem.get_text().upper():
                        value_elem = section.find('div', class_='DrugHeader__meta-value___vqYM0')
                        if value_elem:
                            salt_text = value_elem.get_text().strip()
                            salt_text = ' '.join(salt_text.split())
                            extracted_data['salt_composition'] = salt_text
                            logger.info(f"Found salt composition via meta fallback: {salt_text[:50]}...")
                            break
            
            # Extract medicine description from overview sections
            overview_sections = soup.find_all('div', class_='DrugOverview__content___22ZBX')
            if overview_sections:
                # Get the first substantial description (usually the main overview)
                for section in overview_sections:
                    desc_text = section.get_text().strip()
                    # Clean and limit description length
                    desc_text = ' '.join(desc_text.split())
                    if len(desc_text) > 50:  # Only use substantial descriptions
                        # Limit to first 2-3 sentences or 300 characters
                        sentences = desc_text.split('.')
                        if len(sentences) >= 2:
                            desc_text = '. '.join(sentences[:2]) + '.'
                        else:
                            desc_text = desc_text[:300]
                        
                        extracted_data['medicine_description'] = desc_text
                        logger.info(f"Found description via targeted scraping: {desc_text[:50]}...")
                        break
            
            # If we got both fields, return success
            if 'salt_composition' in extracted_data and 'medicine_description' in extracted_data:
                logger.info(f"Targeted extraction successful for: {medicine_name}")
                return extracted_data
            
            # If we're missing fields, try additional fallbacks
            if 'medicine_description' not in extracted_data:
                # Try introduction section
                intro_sections = soup.find_all('div', class_='DrugOverview__container___CqA8x')
                for container in intro_sections:
                    title_elem = container.find('h2', class_='DrugOverview__title___1OwgG')
                    if title_elem and ('glance' in title_elem.get_text().lower() or 'overview' in title_elem.get_text().lower()):
                        content_elem = container.find('div', class_='DrugOverview__content___22ZBX')
                        if content_elem:
                            desc_text = content_elem.get_text().strip()
                            desc_text = ' '.join(desc_text.split())[:300]
                            extracted_data['medicine_description'] = desc_text
                            logger.info(f"Found description via intro fallback: {desc_text[:50]}...")
                            break
            
            # Return what we found, even if incomplete
            if extracted_data:
                logger.info(f"Partial targeted extraction for: {medicine_name} - found {len(extracted_data)} fields")
                return extracted_data
            else:
                logger.warning(f"Targeted extraction found no data for: {medicine_name}")
                return None
                
        except Exception as e:
            logger.error(f"Targeted extraction failed for {medicine_name}: {str(e)}")
            return None
    
    def extract_with_groq_fallback(self, page_content, medicine_name):
        """
        Fallback: Extract structured data using Groq API (original method)
        Returns dict with extracted fields or None
        """
        # List of models to try (in order of preference)
        models_to_try = [
            'llama-3.1-8b-instant',      # Fast and reliable
            'llama-3.3-70b-versatile',   # More capable but slower
            'openai/gpt-oss-20b'         # Alternative option
        ]
        
        for model_name in models_to_try:
            try:
                # Truncate content to avoid token limits
                max_content_length = 3000  # Reduced from 6000 since we're using as fallback
                if len(page_content) > max_content_length:
                    page_content = page_content[:max_content_length]
                
                # Simplified prompt to avoid issues
                prompt = f"""Extract medicine information from this 1mg page for "{medicine_name}".

Content: {page_content}

Return ONLY valid JSON with these fields:
{{
    "salt_composition": "active ingredients",
    "medicine_description": "brief 2-3 line description"
}}

If information not found, use empty string. JSON only, no explanation."""

                headers = {
                    'Authorization': f'Bearer {self.groq_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': model_name,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 200,  # Reduced from 300
                    'top_p': 1,
                    'stream': False
                }
                
                logger.info(f"Calling Groq API fallback ({model_name}) for: {medicine_name}")
                
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                # If this model works, process the response
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check for API errors in response
                    if 'error' in result:
                        logger.error(f"Groq API returned error with {model_name}: {result['error']}")
                        continue  # Try next model
                    
                    # Extract content
                    if 'choices' not in result or not result['choices']:
                        logger.error(f"No choices in Groq response with {model_name}: {result}")
                        continue  # Try next model
                        
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Parse JSON response
                    try:
                        # Clean the response - sometimes it has markdown formatting
                        if content.startswith('```json'):
                            content = content.replace('```json', '').replace('```', '').strip()
                        elif content.startswith('```'):
                            content = content.replace('```', '').strip()
                        
                        extracted_data = json.loads(content)
                        
                        # Validate required fields
                        required_fields = ['salt_composition', 'medicine_description']
                        if all(field in extracted_data for field in required_fields):
                            logger.info(f"Successfully extracted data for: {medicine_name} using {model_name} (fallback)")
                            return extracted_data
                        else:
                            logger.warning(f"Missing required fields in Groq response for: {medicine_name} using {model_name}")
                            logger.warning(f"Response: {content}")
                            continue  # Try next model
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Groq JSON response for {medicine_name} using {model_name}: {str(e)}")
                        logger.error(f"Raw response: {content}")
                        continue  # Try next model
                
                else:
                    # Log error and try next model
                    logger.warning(f"Groq API error {response.status_code} with {model_name}: {response.text}")
                    continue
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Groq API request failed for {medicine_name} with {model_name}: {str(e)}")
                continue  # Try next model
            except Exception as e:
                logger.warning(f"Groq API call failed for {medicine_name} with {model_name}: {str(e)}")
                continue  # Try next model
        
        # If all models failed
        logger.error(f"All Groq models failed for {medicine_name} (fallback)")
        return None
    
    def process_medicine(self, medicine_name, manufacturer_name=None):
        """
        Complete pipeline for processing a single medicine
        Uses targeted scraping first, then AI fallback if needed
        Returns dict with extracted data or None
        """
        try:
            # Step 1: Search for 1mg URL (now includes manufacturer)
            url = self.google_search_1mg(medicine_name, manufacturer_name)
            if not url:
                return None
            
            # Rate limiting - reduced since direct search is faster
            time.sleep(2)  # Reduced from 4 to 2 seconds
            
            # Step 2: Fetch page content
            page_content = self.fetch_1mg_page(url)
            if not page_content:
                return None
            
            # Step 3: Parse HTML for targeted extraction
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Step 4: Try targeted extraction first (fast and efficient)
            extracted_data = self.extract_targeted_data(soup, medicine_name, manufacturer_name)
            
            # Step 5: If targeted extraction failed or incomplete, use AI fallback
            if not extracted_data or len(extracted_data) < 2:
                logger.info(f"Targeted extraction incomplete for {medicine_name}, trying AI fallback...")
                
                # Clean page content for AI processing
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extract main content - focus on medicine-specific content
                main_content = soup.find('main') or soup.find('div', class_='container') or soup
                clean_content = main_content.get_text()
                
                # Clean text
                lines = (line.strip() for line in clean_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_content = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit text length to avoid token limits
                if len(clean_content) > 5000:  # Reduced from 10000
                    clean_content = clean_content[:5000]
                
                # Try AI extraction
                ai_extracted_data = self.extract_with_groq_fallback(clean_content, medicine_name)
                
                if ai_extracted_data:
                    # Merge with any data from targeted extraction
                    if extracted_data:
                        # Prefer targeted data over AI data for fields we found
                        for key, value in extracted_data.items():
                            if value and value.strip():  # Only use non-empty values
                                ai_extracted_data[key] = value
                    extracted_data = ai_extracted_data
                else:
                    # If AI also failed, use whatever we got from targeted extraction
                    if not extracted_data:
                        logger.error(f"Both targeted and AI extraction failed for: {medicine_name}")
                        return None
            
            # Add source URL to the result
            if extracted_data:
                extracted_data['source_url'] = url
                
                # Log success with method used
                method_used = "targeted" if len(extracted_data) >= 3 else "hybrid (targeted + AI)"
                logger.info(f"Successfully extracted data for {medicine_name} using {method_used} method")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Failed to process medicine {medicine_name}: {str(e)}")
            return None
    
    def enrich_excel(self, input_path, output_path):
        """
        Main function to enrich Excel file with medicine data
        """
        # Initialize safe saver
        self.saver = SafeExcelSaver(output_path)
        
        try:
            # Read Excel file
            logger.info(f"Reading Excel file: {input_path}")
            df = pd.read_excel(input_path)
            self.current_df = df  # Store for emergency saves
            
            # Validate required column
            if 'name' not in df.columns:
                raise ValueError("Excel file must contain 'name' column")
            
            # Check for manufacturer column (optional)
            has_manufacturer = 'manufacturer_name' in df.columns or 'manufacturer' in df.columns
            manufacturer_col = 'manufacturer_name' if 'manufacturer_name' in df.columns else 'manufacturer'
            
            if has_manufacturer:
                logger.info(f"Found manufacturer column: '{manufacturer_col}' - will use for more accurate searches")
            else:
                logger.info("No manufacturer column found - searches will use medicine name only")
                logger.info("Available columns: " + ", ".join(df.columns.tolist()))
            
            # Add new columns if they don't exist
            new_columns = ['salt_composition', 'medicine_description', 'source_url', 'processing_status', 
                          'found_medicine_name', 'found_manufacturer', 'similarity_warning', 'manufacturer_warning']
            for col in new_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Check if this is a resume operation
            existing_success = len(df[df['processing_status'] == 'SUCCESS'])
            if existing_success > 0:
                logger.info(f"Found {existing_success} already processed medicines - will skip these")
            
            # Filter to only unprocessed medicines
            unprocessed_mask = (df['processing_status'] == '') | (df['processing_status'].isna())
            unprocessed_df = df[unprocessed_mask]
            
            total_medicines = len(df)
            unprocessed_count = len(unprocessed_df)
            
            logger.info(f"Total medicines: {total_medicines}")
            logger.info(f"Already processed: {existing_success}")
            logger.info(f"To process: {unprocessed_count}")
            
            if unprocessed_count == 0:
                logger.info("All medicines already processed!")
                return df
            
            # Process each unprocessed medicine
            processed_count = 0
            for idx in unprocessed_df.index:
                # Check for shutdown request
                if self.shutdown_requested:
                    logger.info("🛑 Shutdown requested - stopping processing")
                    break
                    
                medicine_name = str(df.at[idx, 'name']).strip()
                
                # Get manufacturer name if available
                manufacturer_name = None
                if has_manufacturer and manufacturer_col in df.columns:
                    manufacturer_value = df.at[idx, manufacturer_col]
                    if pd.notna(manufacturer_value) and str(manufacturer_value).strip():
                        manufacturer_name = str(manufacturer_value).strip()
                        logger.info(f"Using manufacturer: {manufacturer_name}")
                
                if not medicine_name or medicine_name.lower() == 'nan':
                    df.at[idx, 'processing_status'] = 'SKIPPED_EMPTY_NAME'
                    continue
                
                processed_count += 1
                search_info = f"{medicine_name}"
                if manufacturer_name:
                    search_info += f" (by {manufacturer_name})"
                logger.info(f"Processing {processed_count}/{unprocessed_count}: {search_info} (row {idx + 1})")
                
                try:
                    extracted_data = self.process_medicine(medicine_name, manufacturer_name)
                    
                    if extracted_data:
                        df.at[idx, 'salt_composition'] = extracted_data.get('salt_composition', '')
                        df.at[idx, 'medicine_description'] = extracted_data.get('medicine_description', '')
                        df.at[idx, 'source_url'] = extracted_data.get('source_url', '')
                        df.at[idx, 'found_medicine_name'] = extracted_data.get('found_medicine_name', '')
                        df.at[idx, 'found_manufacturer'] = extracted_data.get('found_manufacturer', '')
                        df.at[idx, 'similarity_warning'] = extracted_data.get('similarity_warning', '')
                        df.at[idx, 'manufacturer_warning'] = extracted_data.get('manufacturer_warning', '')
                        df.at[idx, 'processing_status'] = 'SUCCESS'
                    else:
                        df.at[idx, 'processing_status'] = 'FAILED_NO_DATA'
                        
                except Exception as e:
                    logger.error(f"Error processing {medicine_name}: {str(e)}")
                    df.at[idx, 'processing_status'] = f'ERROR: {str(e)[:100]}'
                
                # Update current_df for emergency saves
                self.current_df = df
                
                # CORRUPTION-PROOF PROGRESS SAVE every 10 medicines
                if processed_count % 10 == 0:
                    logger.info(f"🔄 Saving progress: {processed_count}/{unprocessed_count} processed")
                    success = self.saver.safe_save(df, processed_count)
                    if success:
                        logger.info(f"✅ Progress saved successfully")
                    else:
                        logger.warning(f"⚠️ Progress save failed - but continuing processing")
            
            # CORRUPTION-PROOF FINAL SAVE
            logger.info(f"🔄 Performing final save...")
            final_success = self.saver.safe_save(df)
            
            if final_success:
                logger.info(f"✅ Enrichment complete. Results saved to: {output_path}")
            else:
                logger.error(f"❌ Final save failed - check emergency backup files")
                raise Exception("Final save failed - data may be in emergency backup files")
            
            # Print summary
            success_count = len(df[df['processing_status'] == 'SUCCESS'])
            logger.info(f"📊 Summary: {success_count}/{total_medicines} medicines successfully enriched")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to enrich Excel file: {str(e)}")
            raise
        finally:
            # Always cleanup temporary files
            if self.saver:
                self.saver.cleanup()
            self.current_df = None


def main():
    """Example usage"""
    from config import get_groq_api_key
    
    # Configuration
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
        
    INPUT_FILE = "medicines_input.xlsx"
    OUTPUT_FILE = "medicines_enriched.xlsx"
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Run enrichment
    try:
        enricher.enrich_excel(INPUT_FILE, OUTPUT_FILE)
        print(f"✅ Enrichment completed successfully!")
        print(f"📄 Results saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Enrichment failed: {str(e)}")


if __name__ == "__main__":
    main()