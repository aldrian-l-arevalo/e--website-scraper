# E& Support Portal Scraper

A Python web scraper for extracting FAQ Q&A content from the E& B2B Business Online Portal support section.

## Features

- Automated browser-based scraping using Selenium WebDriver
- Navigates through category pages and expands accordion-style FAQs
- **Complete answer extraction** including bullet points, numbered lists, and multiple paragraphs
- **Flexible category matching** with alternative URL navigation for robust scraping
- Extracts questions and answers organized by category and subcategory
- Real-time progress saving after each FAQ extraction
- Exports data to JSON format with hierarchical structure
- Headless Chrome execution for background processing

## Categories Scraped

- Getting Started
- Accounts
- Bills & Payments
- Switching to e&
- Managing Existing Subscriptions
- Business Products & Services
- Digital Authorization
- Closing an Account

Each category contains multiple subcategories with their own FAQ items.

## Installation

1. Clone or download this repository

2. Install Chrome browser (required for Selenium WebDriver)

3. Create a virtual environment (recommended):
```bash
python -m venv venv
```

4. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.7+
- selenium>=4.15.0
- Chrome browser (latest version recommended)
- ChromeDriver (automatically managed by Selenium)

## Usage

Run the scraper:
```bash
python scraper.py
```

The scraper will:
1. Load the E& B2B support portal main page
2. Navigate through each category by clicking "See More" buttons (with fallback to direct URLs)
3. Extract all FAQ questions and answers from accordion elements
4. Save progress incrementally to `eand_support.json`
5. Display real-time progress in the console

## Output Format

The output JSON file contains an array of objects with the following structure:
```json
[
  {
    "category": "Getting Started",
    "subcategory": "About Business Online Portal",
    "question": "What is the Business Online Portal?",
    "answer": "As a business customer, the Business Online Portal equips you with complete control..."
  }
]
```

### Output Fields:
- **category**: Main category (e.g., "Getting Started", "Accounts")
- **subcategory**: Section within the category (e.g., "User Management", "Billing Details")
- **question**: The FAQ question text
- **answer**: The complete answer text

## How It Works

1. **Navigation**: Uses Selenium to load the main support page and interact with JavaScript-rendered content
2. **Category Selection**: 
   - Attempts flexible matching to find and click "See More" links for each category
   - Falls back to direct URL construction if button navigation fails
3. **FAQ Extraction**: On category pages, locates all accordion items (`.accordion-button`)
4. **Content Extraction**: 
   - Expands each accordion element
   - Extracts questions from the button text
   - Extracts answers from ALL `.eand-paragraph` divs in `.accordion-body`
   - Preserves formatting for bullet points, numbered lists, and multiple paragraphs
5. **Data Organization**: Groups FAQs by category and subcategory (h5 headings)
6. **Progress Saving**: Saves to JSON after each successful FAQ extraction

## Recent Fixes

- **Complete Answer Extraction**: Fixed issue where bullet points and list items were not captured. Now extracts all paragraph divs in the accordion body.
- **Category Navigation**: Improved category matching with flexible word-based matching and alternative URL navigation to handle all categories successfully.
- **List Formatting**: Properly formats bullet points (•) and numbered lists in extracted answers.

## Troubleshooting

### Chrome/ChromeDriver Issues
If you encounter ChromeDriver errors, ensure Chrome browser is installed and updated to the latest version. Selenium automatically downloads the matching ChromeDriver.

### No FAQs Extracted
- Check internet connection
- Verify the support portal URL is accessible: https://www.eand.ae/b2bportal/support-section.html
- Ensure the page structure hasn't changed

### Selenium Import Error
Make sure selenium is installed:
```bash
pip install selenium
```

## Notes

- The scraper runs in **headless mode** (no visible browser window)
- Includes delays between actions to ensure page content loads properly
- Automatically handles stale element references by re-finding elements
- Returns to main page after completing each category

## License

For internal use only.
