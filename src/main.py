import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
from bs4 import BeautifulSoup

class WebScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper")

        # URL Input
        self.url_label = tk.Label(master, text="URL:")
        self.url_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # Selector Input
        self.selector_label = tk.Label(master, text="CSS Selector:")
        self.selector_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.selector_entry = tk.Entry(master, width=50)
        self.selector_entry.grid(row=1, column=1, padx=5, pady=5)

        # Scrape Button
        self.scrape_button = tk.Button(master, text="Scrape", command=self.scrape_website)
        self.scrape_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Results Display
        self.results_label = tk.Label(master, text="Results:")
        self.results_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.results_text = scrolledtext.ScrolledText(master, width=70, height=20, wrap=tk.WORD)
        self.results_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def scrape_website(self):
        url = self.url_entry.get()
        selector = self.selector_entry.get()

        if not url or not selector:
            messagebox.showerror("Error", "URL and CSS Selector cannot be empty.")
            return

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            elements = soup.select(selector)
            
            if not elements:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "No elements found with the given selector.")
                return

            results = [element.get_text(strip=True) for element in elements]
            
            self.results_text.delete(1.0, tk.END)
            for i, result in enumerate(results):
                self.results_text.insert(tk.END, f"Result {i+1}:\n{result}\n\n")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Could not connect to URL: {e}")
        except Exception as e:
            messagebox.showerror("Scraping Error", f"An error occurred during scraping: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
