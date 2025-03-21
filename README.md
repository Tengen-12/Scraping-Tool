# ScrapeMEE - Advanced Web Scraping Tool

## Overview
ScrapeMEE is a powerful **GUI-based web scraping tool** designed to extract text, images, links, tables, and metadata from websites. It features **dynamic content rendering, automation with Selenium, recursive scraping**, and data export to multiple formats. The tool includes a **dark mode**, proxy support, and **user-agent rotation** for ethical and flexible web scraping.

## Screenshots
![Screenshot 2025-03-21 114239](https://github.com/user-attachments/assets/0ac96499-4c17-46e3-a329-b120ff2113f9)

## Features
- 🌐 **GUI-Based Scraper** – Built with **Tkinter** for an interactive experience.
- ⚡ **Dynamic Content Extraction** – Uses **Selenium** to handle JavaScript-rendered pages.
- 🔍 **Recursive Scraping** – Scrape multiple pages up to a defined depth.
- 🛡️ **Proxy & User-Agent Rotation** – Avoids detection and blocks.
- 📋 **Extracts:**
  - Text Content
  - Links & Social Media Links
  - Images (Preview & Download)
  - HTML Tables (Convert to CSV/Excel)
  - Metadata (Title, Description, Keywords, etc.)
  - Emails & Phone Numbers
- 🏷 **Automated Form Submission** – Interacts with login & input forms.
- 📜 **Handles Pagination & Infinite Scroll** – Collects data from multi-page websites.
- 🎭 **Dark Mode Support** – Toggle between light and dark themes.
- 📤 **Export Options:** JSON, CSV, Excel, PDF.
- 📑 **GDPR Disclaimer** – Ensures ethical scraping.

## Technologies Used
- **Python 3.x** – Core programming language.
- **Tkinter** – GUI framework.
- **BeautifulSoup** – HTML parsing and scraping.
- **Requests & Selenium** – Handling dynamic content.
- **Pandas** – Data manipulation (tables, CSV/Excel export).
- **Pillow (PIL)** – Image handling & previews.
- **PDFKit** – Data export to PDF.

## Installation
1. Install **Python 3.x** on your system.
2. Clone or download the repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install **wkhtmltopdf** (for PDF export, if required):
   - Windows: [Download](https://wkhtmltopdf.org/downloads.html)
   - Linux: `sudo apt install wkhtmltopdf`

## Usage
1. **Run the application:**
   ```bash
   python ScrapeMEE.py
   ```
2. Enter a **website URL** and click **Scrape Website**.
3. View extracted **text, images, links, and tables** in the respective tabs.
4. Export data to **JSON, CSV, Excel, or PDF**.

## Ethical Considerations & Disclaimer
- Ensure compliance with **robots.txt** and **GDPR regulations** before scraping.
- Do **NOT** scrape personal or sensitive data without permission.
- This tool is for **educational and research purposes** only.

## Future Improvements
- 📌 Multi-threaded scraping for faster data retrieval.
- 📌 More scraping depth levels.
- 📌 Browser automation for interactive sites.

## Author
Developed by **[Kakashi Hatake]** 🚀
