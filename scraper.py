import time
import json
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EandCategoryScraper:
    def __init__(self):
        self.articles = []
        self.driver = None
        self.main_url = 'https://www.eand.ae/b2bportal/support-section.html'
        
        # Category names visible on the main support page
        self.categories = [
            'Getting Started',
            'Accounts',
            'Bills & Payments',
            'Switching to e&',
            'Managing Existing Subscriptions',
            'Business Products & Services',
            'Digital Authorization',
            'Closing an Account'
        ]
        
    def setup_driver(self):
        """Initialize Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def scrape_category(self, category_name: str):
        """Scrape FAQs from a category by clicking 'SEE MORE' button, then extracting accordions on the category page"""
        try:
            print(f"\n{'='*60}")
            print(f"Category: {category_name}")
            print(f"{'='*60}")
            
            # Make sure we're on the main page
            if 'support-section.html' not in self.driver.current_url:
                self.driver.get(self.main_url)
                time.sleep(3)
            
            # Find and click "See More" link for this category
            see_more_clicked = False
            try:
                # Find all FAQ cards
                faq_cards = self.driver.find_elements(By.CSS_SELECTOR, ".faq-card")
                
                print(f"Found {len(faq_cards)} FAQ cards on page")
                
                # Store all headings for debugging
                all_headings = []
                
                for card in faq_cards:
                    try:
                        # Find the h6 heading in this card
                        heading = card.find_element(By.TAG_NAME, "h6")
                        heading_text = heading.text.strip()
                        all_headings.append(heading_text)
                        
                        # Flexible matching: check if category words are in heading
                        category_words = set(category_name.lower().replace('&', 'and').split())
                        heading_words = set(heading_text.lower().replace('&', 'and').split())
                        
                        # Check if this card matches our category (direct match or word overlap)
                        is_match = (category_name.lower() in heading_text.lower() or 
                                   heading_text.lower() in category_name.lower() or
                                   len(category_words & heading_words) >= len(category_words) * 0.7)
                        
                        if is_match:
                            print(f"Found category card: {heading_text}")
                            
                            # Scroll to the card
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                            time.sleep(0.5)
                            
                            # Find the "See More" link within this card
                            see_more_link = card.find_element(By.CSS_SELECTOR, ".eand-black-link a")
                            
                            print(f"Clicking 'See More' link...")
                            try:
                                see_more_link.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", see_more_link)
                            
                            see_more_clicked = True
                            break
                    except Exception as e:
                        continue
                
                # If not found, print available categories
                if not see_more_clicked and all_headings:
                    print(f"Available categories on page: {all_headings}")
                
            except Exception as e:
                print(f"Error finding See More link: {e}")
            
            if not see_more_clicked:
                print(f"❌ Could not find/click 'SEE MORE' button for: {category_name}")
                print(f"⚠️  Attempting alternative navigation method...")
                
                # Try alternative: construct URL from category name
                category_slug = category_name.lower().replace(' ', '-').replace('&', 'and')
                possible_urls = [
                    f"https://www.eand.ae/b2bportal/support/{category_slug}.html",
                    f"https://www.eand.ae/b2bportal/{category_slug}.html"
                ]
                
                url_found = False
                for url in possible_urls:
                    try:
                        print(f"   Trying URL: {url}")
                        self.driver.get(url)
                        time.sleep(3)
                        
                        # Check if we landed on a valid page (not 404)
                        if "404" not in self.driver.page_source and "not found" not in self.driver.page_source.lower():
                            # Check if there are support-help-faq sections
                            test_sections = self.driver.find_elements(By.CSS_SELECTOR, ".support-help-faq")
                            if test_sections:
                                print(f"   ✓ Successfully navigated via URL")
                                url_found = True
                                break
                    except Exception as e:
                        continue
                
                if not url_found:
                    print(f"❌ All navigation methods failed for: {category_name}")
                    return
            
            # Wait for navigation to category page
            time.sleep(4)
            
            print(f"Navigated to: {self.driver.current_url}")
            
            # Find all subcategory sections (support-help-faq divs)
            subcategory_sections = self.driver.find_elements(By.CSS_SELECTOR, ".support-help-faq")
            
            print(f"Found {len(subcategory_sections)} subcategories")
            
            total_processed = 0
            
            # Process each subcategory section
            for section_idx, section in enumerate(subcategory_sections):
                try:
                    # Get the subcategory name from the h5 heading
                    try:
                        subcategory_heading = section.find_element(By.CSS_SELECTOR, "h5")
                        subcategory_name = subcategory_heading.text.strip()
                    except:
                        subcategory_name = f"Subcategory {section_idx + 1}"
                    
                    print(f"\n  Subcategory: {subcategory_name}")
                    
                    # Find all accordion buttons within this subcategory section
                    accordion_buttons = section.find_elements(By.CSS_SELECTOR, ".accordion-button")
                    print(f"  Found {len(accordion_buttons)} FAQs in this subcategory")
                    
                    # Extract FAQs from accordions in this subcategory
                    for i in range(len(accordion_buttons)):
                        try:
                            # Re-find the section and its accordion buttons to avoid stale references
                            subcategory_sections = self.driver.find_elements(By.CSS_SELECTOR, ".support-help-faq")
                            if section_idx >= len(subcategory_sections):
                                break
                            
                            section = subcategory_sections[section_idx]
                            accordion_buttons = section.find_elements(By.CSS_SELECTOR, ".accordion-button")
                            
                            if i >= len(accordion_buttons):
                                break
                            
                            button = accordion_buttons[i]
                            
                            # Extract question from the button's span
                            try:
                                question_elem = button.find_element(By.TAG_NAME, "span")
                                question_text = question_elem.text.strip()
                            except:
                                question_text = button.text.strip()
                            
                            if not question_text or len(question_text) < 10:
                                continue
                            
                            print(f"    [{i+1}] Question: {question_text[:60]}...")
                            
                            # Check if accordion is already expanded
                            is_collapsed = 'collapsed' in button.get_attribute('class')
                            
                            if is_collapsed:
                                # Click to expand the accordion
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.3)
                                try:
                                    button.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", button)
                                
                                time.sleep(1)
                            
                            # Extract the answer from the accordion body
                            try:
                                # Find the accordion item parent
                                accordion_item = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'accordion-item')]")
                                
                                # Find the accordion body (answer content)
                                accordion_body = accordion_item.find_element(By.CSS_SELECTOR, ".accordion-body")
                                
                                # Get text from ALL eand-paragraph divs with proper formatting
                                answer_text = self.extract_answer_with_all_paragraphs(accordion_body)
                                
                                if answer_text and len(answer_text) > 20:
                                    self.articles.append({
                                        'category': category_name,
                                        'subcategory': subcategory_name,
                                        'question': question_text,
                                        'answer': answer_text
                                    })
                                    print(f"        ✓ Answer extracted ({len(answer_text)} chars)")
                                    total_processed += 1
                                    
                                    # Save progress
                                    self.save_to_json()
                                else:
                                    print(f"        ✗ No answer found or too short")
                            
                            except Exception as e:
                                print(f"        ✗ Could not extract answer: {str(e)[:50]}")
                            
                        except Exception as e:
                            print(f"        Error processing accordion: {str(e)[:60]}")
                            continue
                
                except Exception as e:
                    print(f"  Error processing subcategory: {str(e)[:60]}")
                    continue
            
            processed = total_processed
            
            print(f"\nCompleted {category_name}: {processed} FAQs extracted")
            self.save_to_json(verbose=True)
            
        except Exception as e:
            print(f"Error scraping category {category_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def extract_answer_with_all_paragraphs(self, accordion_body):
        """Extract answer from all eand-paragraph divs in accordion body"""
        try:
            answer_parts = []
            
            # Find all eand-paragraph divs
            paragraph_divs = accordion_body.find_elements(By.CSS_SELECTOR, ".eand-paragraph")
            
            if not paragraph_divs:
                # Fallback to basic text extraction
                return accordion_body.text.strip()
            
            for para_div in paragraph_divs:
                # Extract text from this paragraph div
                text = para_div.text.strip()
                if text:
                    answer_parts.append(text)
            
            # Join all parts with newlines
            if answer_parts:
                return "\n\n".join(answer_parts)
            else:
                return accordion_body.text.strip()
                
        except Exception as e:
            # Fallback to simple text extraction
            return accordion_body.text.strip()
    
    def extract_formatted_answer(self, element):
        """Extract answer with proper formatting for lists and paragraphs"""
        try:
            answer_parts = []
            
            # Get all child elements in order
            children = element.find_elements(By.XPATH, "./*")
            
            if not children:
                # No child elements, just return text
                return element.text.strip()
            
            for child in children:
                tag_name = child.tag_name.lower()
                
                if tag_name == 'p':
                    # Paragraph
                    text = child.text.strip()
                    if text:
                        answer_parts.append(text)
                        
                elif tag_name == 'ul':
                    # Unordered list (bullets)
                    list_items = child.find_elements(By.TAG_NAME, "li")
                    for li in list_items:
                        text = li.text.strip()
                        if text:
                            answer_parts.append(f"• {text}")
                            
                elif tag_name == 'ol':
                    # Ordered list (numbers)
                    list_items = child.find_elements(By.TAG_NAME, "li")
                    for idx, li in enumerate(list_items, 1):
                        text = li.text.strip()
                        if text:
                            answer_parts.append(f"{idx}. {text}")
                            
                elif tag_name in ['div', 'span']:
                    # Check if it contains lists
                    nested_ul = child.find_elements(By.TAG_NAME, "ul")
                    nested_ol = child.find_elements(By.TAG_NAME, "ol")
                    
                    if nested_ul:
                        for ul in nested_ul:
                            list_items = ul.find_elements(By.TAG_NAME, "li")
                            for li in list_items:
                                text = li.text.strip()
                                if text:
                                    answer_parts.append(f"• {text}")
                    elif nested_ol:
                        for ol in nested_ol:
                            list_items = ol.find_elements(By.TAG_NAME, "li")
                            for idx, li in enumerate(list_items, 1):
                                text = li.text.strip()
                                if text:
                                    answer_parts.append(f"{idx}. {text}")
                    else:
                        # Just get text if no lists
                        text = child.text.strip()
                        if text and len(text) > 0:
                            answer_parts.append(text)
            
            # Join with newlines to preserve structure
            if answer_parts:
                return "\n\n".join(answer_parts)
            else:
                # Fallback to element.text
                return element.text.strip()
                
        except Exception as e:
            # Fallback to simple text extraction
            return element.text.strip()
    
    def extract_answer_from_page(self):
        """Extract answer content from current page"""
        try:
            time.sleep(1)
            
            # Try multiple selectors for answer content
            selectors = [
                ".faq-answer",
                ".answer-content",
                "[class*='answer']",
                ".accordion-content",
                ".eand-paragraph p",
                "article p",
                ".faq-content p",
                "main p"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        paragraphs = []
                        for e in elements:
                            text = e.text.strip()
                            if text and len(text) > 20:
                                # Filter out junk
                                if not any(skip in text.lower()[:50] for skip in ['©', '2026', 'consumer', 'small & medium', 'home', 'back']):
                                    paragraphs.append(text)
                        
                        if paragraphs:
                            return " ".join(paragraphs[:5])
                except:
                    continue
            
            # Fallback: try to get text from containers
            containers = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='answer'], [class*='content'], article, main")
            for container in containers:
                text = container.text.strip()
                if text and len(text) > 100:
                    lines = [line.strip() for line in text.split('\n') 
                            if line.strip() and len(line.strip()) > 20]
                    
                    # Filter out navigation/footer content
                    clean_lines = [line for line in lines 
                                  if not any(skip in line.lower()[:30] for skip in ['©', '2026', 'home', 'back', 'consumer'])]
                    
                    if clean_lines:
                        return " ".join(clean_lines[:5])
                
        except Exception as e:
            print(f"        Error extracting answer: {str(e)[:50]}")
        
        return None

    def save_to_json(self, filename: str = 'eand_support.json', verbose: bool = False):
        """Save scraped data"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        if verbose:
            print(f"\n{'='*60}")
            print(f"Data saved to {filename}")
            print(f"{'='*60}")

    def run(self):
        """Execute the scraper"""
        print("="*60)
        print("E& B2B Support Portal Scraper")
        print("Strategy: Click 'SEE MORE' for each category")
        print("="*60)
        
        try:
            self.setup_driver()
            
            print(f"\nLoading main support page: {self.main_url}")
            self.driver.get(self.main_url)
            time.sleep(5)  # Wait for page to fully load
            
            print("✓ Page loaded")
            print(f"Current URL: {self.driver.current_url}")
            
            # Check if redirected to login
            if 'login' in self.driver.current_url.lower():
                print("\n❌ ERROR: Page redirected to login!")
                print("The support page requires authentication.")
                return
            
            print("\nStarting category extraction...")
            
            for category_name in self.categories:
                self.scrape_category(category_name)
                
                # Go back to main page for next category
                print(f"\nReturning to main page...")
                self.driver.get(self.main_url)
                time.sleep(3)
                
                print(f"Total FAQs so far: {len(self.articles)}")
                time.sleep(1)
            
            print(f"\n{'='*60}")
            print(f"SCRAPING COMPLETE!")
            print(f"Total FAQs extracted: {len(self.articles)}")
            print(f"Categories processed: {len(self.categories)}")
            
            # Print summary by category and subcategory
            print(f"\nSummary by category:")
            for category_name in self.categories:
                category_faqs = [a for a in self.articles if a['category'] == category_name]
                print(f"\n  {category_name}: {len(category_faqs)} FAQs")
                
                # Group by subcategory
                subcategories = {}
                for faq in category_faqs:
                    subcat = faq.get('subcategory', 'Unknown')
                    if subcat not in subcategories:
                        subcategories[subcat] = 0
                    subcategories[subcat] += 1
                
                for subcat, count in subcategories.items():
                    print(f"    - {subcat}: {count} FAQs")
            
            # Final save
            self.save_to_json(verbose=True)
            print(f"{'='*60}")
            
        except Exception as e:
            print(f"\n❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close_driver()
            print("\n✓ Browser closed")


if __name__ == "__main__":
    scraper = EandCategoryScraper()
    scraper.run()
