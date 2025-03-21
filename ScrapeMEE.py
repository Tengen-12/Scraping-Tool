import tkinter as tk
from tkinter import ttk, messagebox, filedialog, PhotoImage  # Added for image preview
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
import time  # Added for delay
import threading  # Added for threading
import random  # Added for random user-agent selection
from urllib.robotparser import RobotFileParser  # Added for robots.txt checking
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd  # Added for table extraction and CSV/Excel export
import re  # Added for email and phone number extraction
from PIL import Image, ImageTk  # Added for image gallery and resizing
from io import BytesIO  # Added for handling image data
import pdfkit  # Added for exporting data to PDF
import platform  # Added for system theme detection
import ctypes  # Added for Windows theme detection
import logging  # Added for logging
from requests.sessions import Session  # Added for session handling

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScrapeMEE")
        self.root.geometry("1000x800")
        
        self.dark_mode = False  # Track dark mode state
        self.style = ttk.Style()  # Add ttk style for enhanced GUI
        self.style.theme_use("clam")  # Use a modern theme
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)  # Define dark_mode_var
        self.create_styles()  # Create styles for dark mode
        
        self.create_menu()
        self.create_widgets()
        self.create_status_bar()
        self.scraped_data = {}
        self.scraping_thread = None  # Track the scraping thread
        self.stop_scraping_flag = False  # Flag to stop scraping

        self.proxies = [
            # Add your proxy list here
            {"http": "http://proxy1.com", "https": "https://proxy1.com"},
            {"http": "http://proxy2.com", "https": "https://proxy2.com"}
        ]
        self.user_agents = [
            # Add a list of user-agent strings here
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        self.max_retries = 3  # Maximum number of retries for failed requests
        self.delay_between_requests = 2  # Delay in seconds between requests
        self.selenium_driver = None  # Selenium WebDriver instance
        self.session = Session()  # Initialize a session for authentication
        self.setup_logging()  # Initialize logging
        
    def create_styles(self):
        self.style.configure("TFrame", background="#F0F0F0")
        self.style.configure("TLabel", background="#F0F0F0", foreground="#000000")
        self.style.configure("TButton", background="#F0F0F0", foreground="#000000")
        self.style.configure("TCheckbutton", background="#F0F0F0", foreground="#000000")
        self.style.configure("DarkMode.TFrame", background="#2E2E2E")
        self.style.configure("DarkMode.TLabel", background="#2E2E2E", foreground="#FFFFFF")
        self.style.configure("DarkMode.TButton", background="#2E2E2E", foreground="#FFFFFF")
        self.style.configure("DarkMode.TCheckbutton", background="#2E2E2E", foreground="#FFFFFF")

    def toggle_dark_mode(self):
        """Toggle between light and dark modes with a fade animation."""
        self.dark_mode = not self.dark_mode
        bg_color_start = "#F0F0F0" if self.dark_mode else "#2E2E2E"
        bg_color_end = "#2E2E2E" if self.dark_mode else "#F0F0F0"
        fg_color_start = "#000000" if self.dark_mode else "#FFFFFF"
        fg_color_end = "#FFFFFF" if self.dark_mode else "#000000"

        steps = 20  # Number of animation steps
        for i in range(steps + 1):
            ratio = i / steps
            bg_color = self.interpolate_color(bg_color_start, bg_color_end, ratio)
            fg_color = self.interpolate_color(fg_color_start, fg_color_end, ratio)
            self.root.configure(bg=bg_color)
            self.status_bar.configure(background=bg_color, foreground=fg_color)
            self.text_content.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)
            self.links_list.configure(bg=bg_color, fg=fg_color)
            self.images_list.configure(bg=bg_color, fg=fg_color)
            self.tables_list.configure(bg=bg_color, fg=fg_color)  # Update tables tab
            self.image_canvas.configure(bg=bg_color)  # Update image preview tab
            self.style.configure("TNotebook", background=bg_color)
            self.style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color)
            self.style.map("TNotebook.Tab", background=[("selected", fg_color)], foreground=[("selected", bg_color)])
            self.root.update_idletasks()
            time.sleep(0.02)  # Delay for smooth animation

    def interpolate_color(self, start_color, end_color, ratio):
        """Interpolate between two hex colors."""
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        interpolated_rgb = tuple(
            int(start + (end - start) * ratio) for start, end in zip(start_rgb, end_rgb)
        )
        return self.rgb_to_hex(interpolated_rgb)

    def hex_to_rgb(self, hex_color):
        """Convert a hex color to an RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        """Convert an RGB tuple to a hex color."""
        return f"#{''.join(f'{value:02x}' for value in rgb_color)}"

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Clear Results", command=self.clear_results)
        file_menu.add_command(label="Copy to Clipboard", command=self.copy_to_clipboard)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Settings Menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)  # Updated menu option
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="GDPR Disclaimer", command=self.show_gdpr_disclaimer)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
    def create_widgets(self):
        # URL Input
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)
        ttk.Label(input_frame, text="Website URL:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.url_entry = ttk.Entry(input_frame, width=70, font=("Arial", 10))
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Scrape Website", command=self.start_scraping_thread).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Stop Scraping", command=self.stop_scraping).pack(side=tk.LEFT, padx=5)
        
        # Results Notebook
        self.notebook = ttk.Notebook(self.root, padding="10")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Text Content Tab
        self.text_tab = ttk.Frame(self.notebook)
        self.text_content = tk.Text(self.text_tab, wrap=tk.WORD, font=("Arial", 10))
        text_scroll = ttk.Scrollbar(self.text_tab, command=self.text_content.yview)
        self.text_content.configure(yscrollcommand=text_scroll.set)
        self.text_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(self.text_tab, text="Text Content")
        
        # Links Tab
        self.links_tab = ttk.Frame(self.notebook)
        self.links_list = tk.Listbox(self.links_tab, font=("Arial", 10))
        links_scroll = ttk.Scrollbar(self.links_tab, command=self.links_list.yview)
        self.links_list.configure(yscrollcommand=links_scroll.set)
        self.links_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        links_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(self.links_tab, text="Links")
        
        # Images Tab
        self.images_tab = ttk.Frame(self.notebook)
        self.images_list = tk.Listbox(self.images_tab, font=("Arial", 10))
        images_scroll = ttk.Scrollbar(self.images_tab, command=self.images_list.yview)
        self.images_list.configure(yscrollcommand=images_scroll.set)
        self.images_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        images_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(self.images_tab, text="Images")

        # Tables Tab
        self.tables_tab = ttk.Frame(self.notebook)
        self.tables_list = tk.Text(self.tables_tab, wrap=tk.WORD, font=("Arial", 10))
        tables_scroll = ttk.Scrollbar(self.tables_tab, command=self.tables_list.yview)
        self.tables_list.configure(yscrollcommand=tables_scroll.set)
        self.tables_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tables_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notebook.add(self.tables_tab, text="Tables")

        # Search Bar
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text="Search:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self.search_results).pack(side=tk.LEFT, padx=5)

        # Image Preview Tab
        self.image_preview_tab = ttk.Frame(self.notebook)
        self.image_canvas = tk.Canvas(self.image_preview_tab, bg="white")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(self.image_preview_tab, text="Image Preview")

        # Add depth input for recursive scraping
        depth_frame = ttk.Frame(self.root, padding="10")
        depth_frame.pack(fill=tk.X)
        ttk.Label(depth_frame, text="Depth:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.depth_entry = ttk.Entry(depth_frame, width=10, font=("Arial", 10))
        self.depth_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(depth_frame, text="Recursive Scrape", command=lambda: self.start_recursive_scraping_thread(int(self.depth_entry.get()))).pack(side=tk.LEFT, padx=5)
        
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self, message):
        self.status_bar.config(text=message)
        
    def start_scraping_thread(self):
        """Start scraping in a separate thread."""
        if self.scraping_thread and self.scraping_thread.is_alive():
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
        self.stop_scraping_flag = False
        self.scraping_thread = threading.Thread(target=self.start_scraping)
        self.scraping_thread.start()

    def stop_scraping(self):
        """Stop the ongoing scraping process."""
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_scraping_flag = True
            self.update_status("Scraping stopped.")
        else:
            messagebox.showinfo("Info", "No scraping process to stop.")

    def setup_selenium_driver(self):
        """Set up the Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.selenium_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def scrape_dynamic_content(self, url):
        """Scrape JavaScript-rendered content using Selenium with retries."""
        if not self.selenium_driver:
            self.setup_selenium_driver()
        retries = 0
        while retries < self.max_retries:
            try:
                self.selenium_driver.get(url)
                WebDriverWait(self.selenium_driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.selenium_driver.page_source
            except Exception as e:
                retries += 1
                self.update_status(f"Retry {retries}/{self.max_retries} failed: {str(e)}")
                time.sleep(self.delay_between_requests)
        raise Exception("Max retries exceeded. Failed to load the page.")

    def handle_pagination(self, url, max_pages=5):
        """Scrape multiple pages by handling pagination."""
        if not self.selenium_driver:
            self.setup_selenium_driver()
        self.selenium_driver.get(url)
        all_pages_content = []
        for _ in range(max_pages):
            WebDriverWait(self.selenium_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            all_pages_content.append(self.selenium_driver.page_source)
            try:
                next_button = self.selenium_driver.find_element(By.LINK_TEXT, "Next")
                next_button.click()
                time.sleep(2)  # Allow time for the next page to load
            except Exception:
                break  # Exit if no "Next" button is found
        return all_pages_content

    def handle_form_submission(self, url, form_data):
        """Automate form filling and submission."""
        if not self.selenium_driver:
            self.setup_selenium_driver()
        self.selenium_driver.get(url)
        for field_name, value in form_data.items():
            input_element = self.selenium_driver.find_element(By.NAME, field_name)
            input_element.clear()
            input_element.send_keys(value)
        submit_button = self.selenium_driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        WebDriverWait(self.selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return self.selenium_driver.page_source

    def handle_infinite_scroll(self, url, scroll_pause_time=2, max_scrolls=10):
        """Scrape websites with infinite scroll functionality."""
        if not self.selenium_driver:
            self.setup_selenium_driver()
        self.selenium_driver.get(url)
        last_height = self.selenium_driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_scrolls):
            self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.selenium_driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        return self.selenium_driver.page_source

    def start_scraping(self):
        url = self.url_entry.get()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Bypass robots.txt check
        # if not self.is_allowed_by_robots_txt(url):
        #     self.update_status("Scraping blocked by robots.txt.")
        #     messagebox.showwarning("Warning", "Scraping is not allowed for this website as per robots.txt.")
        #     return

        self.update_status("Scraping in progress...")
        try:
            # Use session scraping if authenticated
            page_source = self.scrape_with_session(url) if self.session.cookies else self.scrape_dynamic_content(url)
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract data
            self.scraped_data = {
                'text': self.get_clean_text(soup),
                'links': self.get_all_links(soup, url),
                'images': self.get_all_images(soup, url),
                'metadata': self.get_metadata(soup),
                'tables': self.get_all_tables(soup),
                'emails': self.extract_emails(self.scraped_data.get('text', '')),
                'phone_numbers': self.extract_phone_numbers(self.scraped_data.get('text', '')),
                'social_media_links': self.extract_social_media_links(self.scraped_data.get('links', []))
            }

            # Check if scraping was stopped
            if self.stop_scraping_flag:
                self.update_status("Scraping stopped.")
                return

            # Update GUI
            self.update_text_content()
            self.update_links_list()
            self.update_images_list()
            self.update_tables_list()
            self.update_image_preview()
            self.update_status("Scraping completed successfully.")

        except Exception as e:
            self.update_status("Scraping failed.")
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
        finally:
            if self.selenium_driver:
                self.selenium_driver.quit()

    def make_request_with_retries(self, url):
        """Make a request with retries, proxy rotation, and user-agent rotation."""
        for attempt in range(self.max_retries):
            try:
                headers = {"User-Agent": random.choice(self.user_agents)}  # Rotate user-agent
                proxy = random.choice(self.proxies)  # Rotate proxy
                response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
                time.sleep(self.delay_between_requests)  # Rate limiting
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.update_status(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return None

    def is_allowed_by_robots_txt(self, url):
        """Check if scraping is allowed by robots.txt."""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch("*", url)
        except Exception:
            return True  # Assume allowed if robots.txt cannot be fetched

    def get_clean_text(self, soup):
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        return soup.get_text(separator='\n', strip=True)
    
    def get_all_links(self, soup, base_url):
        links = set()
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(base_url, link['href'])
            links.add(absolute_url)
        return list(links)
    
    def get_all_images(self, soup, base_url):
        images = set()
        for img in soup.find_all('img', src=True):
            absolute_url = urljoin(base_url, img['src'])
            images.add(absolute_url)
        return list(images)
    
    def get_metadata(self, soup):
        meta_data = {}
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs:
                meta_data[meta['name']] = meta.get('content', '')
            elif 'property' in meta.attrs:
                meta_data[meta['property']] = meta.get('content', '')
        return meta_data

    def get_all_tables(self, soup):
        """Extract all HTML tables and return them as a list of DataFrames."""
        tables = []
        for table in soup.find_all("table"):
            df = pd.read_html(str(table))[0]
            tables.append(df)
        return tables

    def extract_emails(self, text):
        """Extract email addresses using regex."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, text)

    def extract_phone_numbers(self, text):
        """Extract phone numbers using regex."""
        phone_pattern = r'\+?\d[\d -]{8,}\d'
        return re.findall(phone_pattern, text)

    def extract_social_media_links(self, links):
        """Extract social media profile links."""
        social_media_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com"]
        social_links = [link for link in links if any(domain in link for domain in social_media_domains)]
        return social_links
    
    def update_text_content(self):
        self.text_content.delete(1.0, tk.END)
        self.text_content.insert(tk.END, self.scraped_data.get('text', ''))
        
    def update_links_list(self):
        self.links_list.delete(0, tk.END)
        for link in self.scraped_data.get('links', []):
            self.links_list.insert(tk.END, link)
            
    def update_images_list(self):
        self.images_list.delete(0, tk.END)
        for img in self.scraped_data.get('images', []):
            self.images_list.insert(tk.END, img)

    def update_tables_list(self):
        """Update the tables tab with extracted tables."""
        self.tables_list.delete(1.0, tk.END)
        tables = self.scraped_data.get('tables', [])
        for i, table in enumerate(tables):
            self.tables_list.insert(tk.END, f"Table {i + 1}:\n")
            self.tables_list.insert(tk.END, table.to_string(index=False))
            self.tables_list.insert(tk.END, "\n\n")

    def update_image_preview(self):
        """Display previews of all image links shown in the Images tab."""
        self.image_canvas.delete("all")
        images = self.scraped_data.get('images', [])
        x, y = 10, 10
        self.image_canvas.images = []  # Store references to avoid garbage collection
        for img_url in images:  # Iterate through all image links
            try:
                response = requests.get(img_url, stream=True, timeout=5)
                response.raise_for_status()
                img_data = Image.open(BytesIO(response.content))
                img_data.thumbnail((100, 100))  # Resize for preview
                img = ImageTk.PhotoImage(img_data)
                self.image_canvas.create_image(x, y, anchor=tk.NW, image=img)
                self.image_canvas.images.append(img)  # Keep a reference
                x += 110
                if x > self.image_canvas.winfo_width() - 100:
                    x = 10
                    y += 110
            except Exception as e:
                self.update_status(f"Failed to load image: {str(e)}")

    def search_results(self):
        """Search for specific keywords in text or links."""
        query = self.search_entry.get().lower()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return

        # Search in text content
        text_results = [line for line in self.scraped_data.get('text', '').splitlines() if query in line.lower()]

        # Search in links
        link_results = [link for link in self.scraped_data.get('links', []) if query in link.lower()]

        # Display results
        result_message = (
            "Text Matches:\n" + "\n".join(text_results[:5]) +
            "\n\nLinks Matches:\n" + "\n".join(link_results[:5])
        )
        messagebox.showinfo("Search Results", result_message)
            
    def clear_results(self):
        self.scraped_data = {}
        self.update_text_content()
        self.update_links_list()
        self.update_images_list()
        self.update_tables_list()
        self.update_status("Results cleared.")
        
    def save_data(self):
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            try:
                if file_path.endswith(".json"):
                    with open(file_path, 'w') as f:
                        json.dump(self.scraped_data, f, indent=2)
                elif file_path.endswith(".csv"):
                    pd.DataFrame(self.scraped_data).to_csv(file_path, index=False)
                elif file_path.endswith(".xlsx"):
                    pd.DataFrame(self.scraped_data).to_excel(file_path, index=False)
                elif file_path.endswith(".pdf"):
                    # Specify the path to wkhtmltopdf if not in PATH
                    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
                    pdfkit.from_string(json.dumps(self.scraped_data, indent=2), file_path, configuration=pdfkit_config)

                # Save tables as separate CSV files
                for i, table in enumerate(self.scraped_data.get('tables', [])):
                    table.to_csv(f"{file_path}_table_{i + 1}.csv", index=False)

                messagebox.showinfo("Success", f"Data saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copy the scraped data to the clipboard."""
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to copy!")
            return
        clipboard_content = json.dumps(self.scraped_data, indent=2)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_content)
        self.root.update()  # Keep the clipboard content
        messagebox.showinfo("Success", "Scraped data copied to clipboard.")
        
    def show_about(self):
        messagebox.showinfo("About", "ScrapeMEE\nVersion 1.0\nDeveloped by Kakashi Hatake(APB)")

    def setup_logging(self):
        """Set up logging for the application."""
        logging.basicConfig(
            filename="scraping.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info("Application started.")

    def login(self, login_url, credentials):
        """Log in to a website and store the session cookies."""
        try:
            response = self.session.post(login_url, data=credentials)
            response.raise_for_status()
            if response.ok:
                logging.info("Login successful.")
                messagebox.showinfo("Success", "Login successful.")
            else:
                logging.warning("Login failed.")
                messagebox.showwarning("Warning", "Login failed.")
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            messagebox.showerror("Error", f"Login error: {str(e)}")

    def scrape_with_session(self, url):
        """Scrape a website using the authenticated session."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            logging.info(f"Scraped URL: {url}")
            return response.text
        except Exception as e:
            logging.error(f"Error scraping URL {url}: {str(e)}")
            messagebox.showerror("Error", f"Error scraping URL {url}: {str(e)}")
            return None

    def generate_report(self):
        """Generate a detailed report with scraping statistics."""
        if not self.scraped_data:
            messagebox.showwarning("Warning", "No data to generate a report!")
            return

        report = {
            "Number of Links": len(self.scraped_data.get("links", [])),
            "Number of Images": len(self.scraped_data.get("images", [])),
            "Number of Tables": len(self.scraped_data.get("tables", [])),
            "Number of Emails": len(self.scraped_data.get("emails", [])),
            "Number of Phone Numbers": len(self.scraped_data.get("phone_numbers", [])),
            "Number of Social Media Links": len(self.scraped_data.get("social_media_links", [])),
        }

        report_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if report_path:
            try:
                with open(report_path, "w") as report_file:
                    for key, value in report.items():
                        report_file.write(f"{key}: {value}\n")
                logging.info(f"Report saved to {report_path}")
                messagebox.showinfo("Success", f"Report saved to {report_path}")
            except Exception as e:
                logging.error(f"Failed to save report: {str(e)}")
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")

    def show_gdpr_disclaimer(self):
        """Show a GDPR compliance disclaimer."""
        disclaimer = (
            "This application is intended for educational purposes only. "
            "Ensure that your scraping activities comply with GDPR and other data protection laws. "
            "Do not scrape personal or sensitive data without proper authorization."
        )
        messagebox.showinfo("GDPR Compliance", disclaimer)

    def recursive_scrape(self, url, depth, visited=None):
        """Recursively scrape all linked pages up to a specified depth."""
        if visited is None:
            visited = set()

        if depth == 0 or url in visited:
            return

        visited.add(url)
        self.update_status(f"Scraping: {url} (Depth: {depth})")
        logging.info(f"Scraping: {url} (Depth: {depth})")

        try:
            # Use session scraping if authenticated
            page_source = self.scrape_with_session(url) if self.session.cookies else self.scrape_dynamic_content(url)
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract data for the current page
            self.scraped_data.setdefault('text', []).append(self.get_clean_text(soup))
            self.scraped_data.setdefault('links', []).extend(self.get_all_links(soup, url))
            self.scraped_data.setdefault('images', []).extend(self.get_all_images(soup, url))
            self.scraped_data.setdefault('metadata', []).append(self.get_metadata(soup))
            self.scraped_data.setdefault('emails', []).extend(self.extract_emails(self.scraped_data.get('text', '')[-1]))
            self.scraped_data.setdefault('phone_numbers', []).extend(self.extract_phone_numbers(self.scraped_data.get('text', '')[-1]))
            self.scraped_data.setdefault('social_media_links', []).extend(self.extract_social_media_links(self.scraped_data.get('links', [])))

            # Recursively scrape linked pages
            for link in self.scraped_data['links']:
                if link not in visited:
                    self.recursive_scrape(link, depth - 1, visited)

        except Exception as e:
            logging.error(f"Error scraping {url}: {str(e)}")
            self.update_status(f"Error scraping {url}: {str(e)}")

    def start_recursive_scraping_thread(self, depth):
        """Start recursive scraping in a separate thread."""
        if self.scraping_thread and self.scraping_thread.is_alive():
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
        self.stop_scraping_flag = False
        self.scraping_thread = threading.Thread(target=self.start_recursive_scraping, args=(depth,))
        self.scraping_thread.start()

    def start_recursive_scraping(self, depth):
        """Start the recursive scraping process."""
        url = self.url_entry.get()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        self.update_status("Recursive scraping in progress...")
        try:
            self.recursive_scrape(url, depth)
            self.update_status("Recursive scraping completed successfully.")
            self.update_text_content()
            self.update_links_list()
            self.update_images_list()
            self.update_tables_list()
            self.update_image_preview()
        except Exception as e:
            self.update_status("Recursive scraping failed.")
            messagebox.showerror("Error", f"Recursive scraping failed: {str(e)}")
        finally:
            if self.selenium_driver:
                self.selenium_driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()