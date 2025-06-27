import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import csv
import json

class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        # URL Input
        self.url_label = tk.Label(master, text="URLs (one per line):")
        self.url_label.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.url_entry = scrolledtext.ScrolledText(master, width=50, height=5, wrap=tk.WORD)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # Selector Input
        self.selector_label = tk.Label(master, text="CSS Selectors (one per line):")
        self.selector_label.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.selector_entry = scrolledtext.ScrolledText(master, width=50, height=5, wrap=tk.WORD)
        self.selector_entry.grid(row=1, column=1, padx=5, pady=5)

        # Scrape Buttons
        self.scrape_button = tk.Button(master, text="Scrape Single", command=self.scrape_single_website)
        self.scrape_button.grid(row=2, column=0, pady=5)

        self.batch_scrape_button = tk.Button(master, text="Batch Scrape", command=self.batch_scrape_website)
        self.batch_scrape_button.grid(row=2, column=1, pady=5)

        # Export Buttons
        self.export_csv_button = tk.Button(master, text="Export to CSV", command=self.export_to_csv)
        self.export_csv_button.grid(row=3, column=0, pady=5)

        self.export_json_button = tk.Button(master, text="Export to JSON", command=self.export_to_json)
        self.export_json_button.grid(row=3, column=1, pady=5)

        # Proxy Input
        self.proxy_address_label = tk.Label(master, text="Proxy Address:")
        self.proxy_address_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.proxy_address_entry = tk.Entry(master, width=50)
        self.proxy_address_entry.grid(row=4, column=1, padx=5, pady=5)

        self.proxy_port_label = tk.Label(master, text="Proxy Port:")
        self.proxy_port_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.proxy_port_entry = tk.Entry(master, width=50)
        self.proxy_port_entry.grid(row=5, column=1, padx=5, pady=5)

        # User-Agent Input
        self.user_agent_label = tk.Label(master, text="User-Agent:")
        self.user_agent_label.grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.user_agent_entry = tk.Entry(master, width=50)
        self.user_agent_entry.grid(row=6, column=1, padx=5, pady=5)
        self.user_agent_entry.insert(0, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

        # Results Display
        self.results_label = tk.Label(master, text="Results:")
        self.results_label.grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.results_text = scrolledtext.ScrolledText(master, width=70, height=20, wrap=tk.WORD)
        self.results_text.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        self.scraped_data = [] # To store scraped results for export (list of dicts)

    def scrape_single_website(self):
        url = self.url_entry.get("1.0", tk.END).strip()
        selector = self.selector_entry.get("1.0", tk.END).strip()
        self.scraped_data = [] # Clear previous results for single scrape
        self.results_text.delete(1.0, tk.END) # Clear results display
        self._perform_scrape(url, selector)

    def batch_scrape_website(self):
        urls = [u.strip() for u in self.url_entry.get("1.0", tk.END).splitlines() if u.strip()]
        selectors = [s.strip() for s in self.selector_entry.get("1.0", tk.END).splitlines() if s.strip()]

        if not urls or not selectors:
            messagebox.showerror("Error", "URLs and CSS Selectors cannot be empty for batch scraping.")
            return

        if len(urls) != len(selectors):
            messagebox.showwarning("Warning", "Number of URLs and CSS Selectors do not match. Processing pairs until one list runs out.")
        
        self.scraped_data = [] # Clear previous results for batch scrape
        self.results_text.delete(1.0, tk.END) # Clear results display

        max_iterations = min(len(urls), len(selectors))
        for i in range(max_iterations):
            url = urls[i]
            selector = selectors[i]
            self.results_text.insert(tk.END, f"Scraping URL: {url} with Selector: {selector}\n")
            self._perform_scrape(url, selector)
            self.results_text.insert(tk.END, f"Finished scraping {url}.\n\n")

    def _perform_scrape(self, url, selector):
        try:
            user_agent = self.user_agent_entry.get().strip()
            headers = {'User-Agent': user_agent if user_agent else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

            proxy_address = self.proxy_address_entry.get().strip()
            proxy_port = self.proxy_port_entry.get().strip()
            
            proxies = {}
            if proxy_address and proxy_port:
                try:
                    proxy_port = int(proxy_port)
                    proxy_url = f"http://{proxy_address}:{proxy_port}"
                    proxies = {
                        "http": proxy_url,
                        "https": proxy_url,
                    }
                except ValueError:
                    messagebox.showerror("Proxy Error", "Invalid proxy port. Please enter a number.")
                    return

            response = requests.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            elements = soup.select(selector)
            
            if not elements:
                self.results_text.insert(tk.END, f"No elements found with selector '{selector}' on {url}.\n")
                return

            for i, element in enumerate(elements):
                text = element.get_text(strip=True)
                self.scraped_data.append({'url': url, 'selector': selector, 'text': text})
                self.results_text.insert(tk.END, f"Result {i+1} from {url}:\n{text}\n\n")

        except requests.exceptions.RequestException as e:
            self.results_text.insert(tk.END, f"Network Error for {url}: {e}\n")
            messagebox.showerror("Network Error", f"Could not connect to URL: {e}")
        except Exception as e:
            self.results_text.insert(tk.END, f"Scraping Error for {url}: {e}\n")
            messagebox.showerror("Scraping Error", f"An error occurred during scraping: {e}")

    def export_to_csv(self):
        if not self.scraped_data:
            messagebox.showinfo("Info", "No data to export. Please scrape a website first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    for item in self.scraped_data:
                        csv_writer.writerow([item])
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting to CSV: {e}")

    def export_to_json(self):
        if not self.scraped_data:
            messagebox.showinfo("Info", "No data to export. Please scrape a website first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(self.scraped_data, jsonfile, indent=4, ensure_ascii=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting to JSON: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()