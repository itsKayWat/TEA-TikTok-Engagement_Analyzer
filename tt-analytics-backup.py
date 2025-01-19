import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import psutil
import os
from selenium.webdriver.common.keys import Keys

class TikTokAnalyzer:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("TikTok Engagement Analyzer")
        self.root.geometry("1000x800")
        
        # TikTok Colors
        self.TIKTOK_BLACK = "#121212"
        self.TIKTOK_RED = "#FE2C55"
        self.TIKTOK_GRAY = "#2F2F2F"
        self.TIKTOK_WHITE = "#E6E6E6"
        self.TIKTOK_LIGHT_GRAY = "#3A3A3A"
        
        # Fixed column widths (in pixels)
        self.column_widths = {
            0: 50,   # #
            1: 200,  # Caption
            2: 80,   # URL
            3: 100,  # Views
            4: 100,  # Likes
            5: 100,  # Comments
            6: 80,   # Saves
            7: 80,   # Shares
            8: 80    # ER Rate
        }
        
        # Initialize variables
        self.headless_var = tk.BooleanVar(value=False)
        self.posts_data = []
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure styles for all ttk widgets
        self.style.configure("TFrame", background=self.TIKTOK_BLACK)
        self.style.configure("TLabel", 
                            background=self.TIKTOK_BLACK, 
                            foreground=self.TIKTOK_WHITE,
                            font=('Segoe UI', 10))
        self.style.configure("TButton", 
                            background=self.TIKTOK_LIGHT_GRAY,
                            foreground=self.TIKTOK_WHITE,
                            padding=10,
                            font=('Segoe UI', 11, 'bold'))
        self.style.configure("TEntry",
                            fieldbackground=self.TIKTOK_LIGHT_GRAY,
                            foreground=self.TIKTOK_WHITE,
                            padding=5)
        self.style.configure("Accent.TButton",
                            background=self.TIKTOK_RED,
                            foreground=self.TIKTOK_WHITE)
        self.style.configure("TNotebook",
                            background=self.TIKTOK_BLACK,
                            tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab",
                            background=self.TIKTOK_LIGHT_GRAY,
                            foreground=self.TIKTOK_WHITE,
                            padding=[10, 5])
        
        # Map dynamic styles
        self.style.map("TButton",
                      background=[('active', self.TIKTOK_RED)],
                      foreground=[('active', self.TIKTOK_WHITE)])
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.TIKTOK_RED)],
                      foreground=[("selected", self.TIKTOK_WHITE)])
        
        # Add hover style
        self.style.configure('Hover.TFrame', background=self.TIKTOK_LIGHT_GRAY)
        
        # Set window background
        self.root.configure(bg=self.TIKTOK_BLACK)
        
        # Setup GUI
        self.setup_gui()
        
        # Add table styles
        self.style.configure('Header.TFrame', 
                            background=self.TIKTOK_GRAY,
                            relief='solid',
                            borderwidth=1)
        self.style.configure('Cell.TFrame',
                            background=self.TIKTOK_BLACK,
                            relief='solid',
                            borderwidth=1)
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="TikTok Analytics",
                               font=('Segoe UI', 24, 'bold'),
                               foreground=self.TIKTOK_RED)
        title_label.pack(pady=(0, 20))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create input fields with default values
        def create_entry_frame(parent, label_text, default_value=None):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            label = ttk.Label(frame, text=label_text)
            label.pack(side=tk.LEFT, padx=(0, 10))
            entry = ttk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT, ipady=5)
            if default_value:
                entry.insert(0, default_value)
            return entry
        
        self.username_entry = create_entry_frame(input_frame, "TikTok Username:")
        self.engagement_entry = create_entry_frame(input_frame, "Desired Engagement Rate (%):", "13")
        self.posts_entry = create_entry_frame(input_frame, "Posts to Analyze:", "5")
        
        # Headless mode checkbox
        headless_frame = ttk.Frame(input_frame)
        headless_frame.pack(fill=tk.X, pady=5)
        headless_check = ttk.Checkbutton(headless_frame,
                                        text="Headless Mode",
                                        variable=self.headless_var,
                                        style="TCheckbutton")
        headless_check.pack(side=tk.LEFT)
        
        # Analyze button
        analyze_button = ttk.Button(main_frame,
                                   text="Analyze Profile",
                                   command=self.analyze_profile,
                                   style="Accent.TButton")
        analyze_button.pack(pady=(0, 15))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Create tabs
        posts_frame = ttk.Frame(self.notebook)
        comments_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(posts_frame, text="Posts Analysis")
        self.notebook.add(comments_frame, text="Comments Analysis")
        
        # Posts tab content - create table-like view
        table_frame = ttk.Frame(posts_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15,0))
        
        # Headers
        headers = ["#", "Caption", "URL", "👁️ Views", "❤️ Likes", "💬 Comments", "⭐ Saves", "↪️ Shares", "📊 ER Rate"]
        
        # Create header cells
        for i, header in enumerate(headers):
            cell_frame = ttk.Frame(table_frame, style='Header.TFrame', width=self.column_widths[i])
            cell_frame.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
            cell_frame.grid_propagate(False)
            
            label = ttk.Label(cell_frame, 
                             text=header,
                             font=('Segoe UI', 10, 'bold'),
                             foreground=self.TIKTOK_WHITE,
                             anchor='center')
            label.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Configure grid weights
        for i in range(len(headers)):
            table_frame.grid_columnconfigure(i, weight=1, minsize=self.column_widths[i])
        
        # Create scrollable frame for posts
        canvas = tk.Canvas(table_frame, bg=self.TIKTOK_BLACK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        self.posts_container = ttk.Frame(canvas)
        
        # Configure scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, columnspan=len(headers), sticky='nsew')
        scrollbar.grid(row=1, column=len(headers), sticky='ns')
        
        # Create a window inside the canvas for the posts container
        canvas.create_window((0, 0), window=self.posts_container, anchor="nw")
        self.posts_container.bind('<Configure>', configure_scroll_region)
        
        # Configure posts container grid
        for i in range(len(headers)):
            self.posts_container.grid_columnconfigure(i, weight=1, minsize=self.column_widths[i])
        
        # Comments tab - create split view
        paned_window = ttk.PanedWindow(comments_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Posts list
        posts_list_frame = ttk.Frame(paned_window)
        posts_label = ttk.Label(posts_list_frame, text="Posts", font=('Segoe UI', 11, 'bold'))
        posts_label.pack(pady=(0, 5))
        
        self.posts_list = tk.Text(posts_list_frame,
                                 height=20,
                                 width=35,
                                 bg=self.TIKTOK_GRAY,
                                 fg=self.TIKTOK_WHITE,
                                 insertbackground=self.TIKTOK_WHITE,
                                 font=('Consolas', 11),
                                 relief="flat",
                                 padx=15,
                                 pady=15)
        self.posts_list.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Comments view
        comments_view_frame = ttk.Frame(paned_window)
        comments_label = ttk.Label(comments_view_frame, text="Comments", font=('Segoe UI', 11, 'bold'))
        comments_label.pack(pady=(0, 5))
        
        self.comments_text = tk.Text(comments_view_frame,
                                    height=20,
                                    width=35,
                                    bg=self.TIKTOK_GRAY,
                                    fg=self.TIKTOK_WHITE,
                                    insertbackground=self.TIKTOK_WHITE,
                                    font=('Consolas', 11),
                                    relief="flat",
                                    padx=15,
                                    pady=15)
        self.comments_text.pack(fill=tk.BOTH, expand=True)
        
        # Add both frames to paned window
        paned_window.add(posts_list_frame)
        paned_window.add(comments_view_frame)
        
        # Add scrollbars
        for text_widget, frame in [(self.posts_list, posts_list_frame),
                                 (self.comments_text, comments_view_frame)]:
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Now add the example data after all widgets are created
        example_post = {
            'url': 'https://www.tiktok.com/@example/video/1234567890',
            'caption': 'This is an example TikTok post! Click to see comments.',
            'views': 100000,
            'likes': 50000,
            'comments': 500,
            'saves': 1000,
            'shares': 2500,
            'er_rate': 53.50,
            'comments_data': [
                "This is example comment #1!",
                "Here's another example comment!",
                "Click Analyze Profile to see real comments!",
                "Example comment #4 showing formatting",
                "Last example comment demonstrating layout"
            ]
        }
        
        # Add "EXAMPLE" label above the example row
        example_label = ttk.Label(
            self.posts_container,
            text="EXAMPLE DATA - Click 'Analyze Profile' to see real data",
            font=('Segoe UI', 10, 'italic'),
            foreground=self.TIKTOK_RED
        )
        example_label.grid(row=0, column=0, columnspan=len(headers), pady=(5,2), sticky='w', padx=5)
        
        # Add the example row
        self.add_post_to_table(example_post)

    def kill_chrome_processes(self):
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            time.sleep(2)  # Give more time for Chrome to fully close
        except Exception as e:
            print(f"Error killing Chrome processes: {str(e)}")

    def setup_browser(self):
        self.kill_chrome_processes()  # Make sure to close existing Chrome instances
        
        chrome_options = Options()
        if self.headless_var.get():
            chrome_options.add_argument('--headless=new')  # Updated headless argument
        
        # Your specific profile path
        user_data_dir = r"C:\Users\xlkay\AppData\Local\Google\Chrome\User Data"
        profile_directory = "Default"  # This is your Person 1 profile
        
        # Add profile arguments
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        chrome_options.add_argument(f'--profile-directory={profile_directory}')
        
        # Anti-detection measures
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional preferences to maintain login state
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute CDP commands to prevent detection
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Additional stealth scripts
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Overwrite the `plugins` property to use a custom getter.
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Overwrite the `languages` property to use a custom getter.
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Pass the Permissions Test.
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            return driver
            
        except Exception as e:
            print(f"Error setting up browser: {str(e)}")
            raise e

    def analyze_profile(self):
        try:
            username = self.username_entry.get().strip()
            desired_rate = float(self.engagement_entry.get())
            posts_to_analyze = int(self.posts_entry.get())
            
            if not username:
                messagebox.showerror("Error", "Please enter a username")
                return
            
            # Clear existing posts
            for widget in self.posts_container.winfo_children():
                widget.destroy()
            self.posts_data = []
            
            driver = self.setup_browser()
            
            try:
                # Add random delay before navigation
                time.sleep(random.uniform(2, 4))
                
                # Navigate to profile
                driver.get(f"https://www.tiktok.com/@{username}")
                
                # Wait for videos to load with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-e2e="user-post-item"]'))
                        )
                        break
                    except Exception:
                        if attempt == max_retries - 1:
                            raise
                        time.sleep(2)
                    
                # Get video links first
                video_links = []
                video_elements = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="user-post-item"] a')[:posts_to_analyze]
                
                for video in video_elements:
                    try:
                        href = video.get_attribute('href')
                        if href:
                            video_links.append(href)
                    except:
                        continue
                    
                # Now process each video URL directly
                for idx, video_url in enumerate(video_links, 1):
                    try:
                        # Navigate directly to video URL
                        driver.get(video_url)
                        time.sleep(2)  # Wait for page load
                        
                        # Wait for and get engagement metrics with retry
                        def get_metric(selector):
                            for _ in range(3):
                                try:
                                    element = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                    )
                                    return element.text
                                except:
                                    time.sleep(1)
                            return "0"
                        
                        likes = get_metric('[data-e2e="like-count"]')
                        comments = get_metric('[data-e2e="comment-count"]')
                        shares = get_metric('[data-e2e="share-count"]')
                        
                        # Convert metrics
                        def convert_metric(metric):
                            try:
                                metric = metric.lower().strip()
                                if not metric or metric == '':
                                    return 0
                                if 'k' in metric:
                                    return float(metric.replace('k', '')) * 1000
                                elif 'm' in metric:
                                    return float(metric.replace('m', '')) * 1000000
                                return float(metric)
                            except:
                                return 0
                        
                        likes_count = convert_metric(likes)
                        comments_count = convert_metric(comments)
                        shares_count = convert_metric(shares)
                        saves_count = 0  # TikTok doesn't show saves publicly
                        views_count = likes_count * 1.5  # Estimated views based on likes
                        
                        # Calculate engagement
                        engagement = ((likes_count + comments_count + shares_count) / views_count) * 100 if views_count > 0 else 0
                        
                        # Create post data dictionary
                        post_data = {
                            'url': video_url,
                            'views': int(views_count),
                            'likes': int(likes_count),
                            'comments': int(comments_count),
                            'saves': int(saves_count),
                            'shares': int(shares_count),
                            'er_rate': engagement,
                            'comments_data': []  # Will be populated when viewing comments
                        }
                        
                        # Add to table
                        self.add_post_to_table(post_data)
                        
                    except Exception as e:
                        print(f"Error analyzing post {idx}: {str(e)}")
                    
                    # Small delay between videos
                    time.sleep(random.uniform(1, 2))
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_comments_for_selected_post(self, event=None):
        try:
            # Get selected post
            selection = self.posts_list.tag_ranges("sel")
            if selection:
                start = selection[0]
                end = selection[1]
                selected_text = self.posts_list.get(start, end)
                
                # Clear current comments
                self.comments_text.delete(1.0, tk.END)
                
                # Show comments for selected post
                # This will be populated when we implement comment scraping
                self.comments_text.insert(tk.END, f"Loading comments for selected post...\n{selected_text}")
        except Exception as e:
            print(f"Error showing comments: {str(e)}")

    def show_comments_for_post(self, post_data):
        """Display comments for the selected post"""
        # Switch to comments tab
        self.notebook.select(1)  # Select the comments tab
        
        # Clear current comments
        self.comments_text.delete(1.0, tk.END)
        
        # Update posts list selection
        self.posts_list.delete(1.0, tk.END)
        self.posts_list.insert(tk.END, f"Post URL: {post_data['url']}\n")
        self.posts_list.insert(tk.END, f"Views: {post_data['views']:,}\n")
        self.posts_list.insert(tk.END, f"Likes: {post_data['likes']:,}\n")
        self.posts_list.insert(tk.END, f"Comments: {post_data['comments']:,}\n")
        self.posts_list.insert(tk.END, f"Saves: {post_data['saves']:,}\n")
        self.posts_list.insert(tk.END, f"Shares: {post_data['shares']:,}\n")
        self.posts_list.insert(tk.END, f"ER Rate: {post_data['er_rate']:.2f}%\n")
        
        # Show comments
        if 'comments_data' in post_data and post_data['comments_data']:
            for i, comment in enumerate(post_data['comments_data'], 1):
                self.comments_text.insert(tk.END, f"{i}. {comment}\n")
        else:
            self.comments_text.insert(tk.END, "No comments available for this post.\n")

    def add_post_to_table(self, post_data):
        """Add a post row to the table"""
        row = len(self.posts_data)
        self.posts_data.append(post_data)
        
        # Create cells for each column
        cells = [
            (f"#{row + 1}", 'center'),
            (post_data.get('caption', '')[:30] + "..." if len(post_data.get('caption', '')) > 30 else post_data.get('caption', ''), 'w'),
            ("Copy URL", 'center'),
            (f"{post_data['views']:,}", 'center'),
            (f"{post_data['likes']:,}", 'center'),
            (f"{post_data['comments']:,}", 'center'),
            (f"{post_data['saves']:,}", 'center'),
            (f"{post_data['shares']:,}", 'center'),
            (f"{post_data['er_rate']:.2f}%", 'center')
        ]
        
        def copy_url():
            self.root.clipboard_clear()
            self.root.clipboard_append(post_data['url'])
        
        def view_comments(pd=post_data):
            self.show_comments_for_post(pd)
        
        # Calculate if ER rate meets desired rate
        desired_rate = float(self.engagement_entry.get() or "13")
        er_color = "#4CAF50" if post_data['er_rate'] >= desired_rate else self.TIKTOK_RED
        
        # Create cell frames with fixed widths
        for i, (text, alignment) in enumerate(cells):
            cell_frame = ttk.Frame(self.posts_container, style='Cell.TFrame', width=self.column_widths[i])
            cell_frame.grid(row=row + 1, column=i, sticky='nsew', padx=1, pady=1)
            cell_frame.grid_propagate(False)
            
            if i == 2:  # URL column
                button = ttk.Button(cell_frame, text=text, command=copy_url, width=8)
                button.pack(expand=True, padx=2, pady=1)
            else:
                label = ttk.Label(
                    cell_frame,
                    text=text,
                    foreground=er_color if i == 8 else self.TIKTOK_WHITE,
                    font=('Segoe UI', 10),
                    anchor=alignment
                )
                label.pack(expand=True, fill='both', padx=5, pady=2)
            
            # Make the entire row clickable for comments
            cell_frame.bind('<Button-1>', lambda e, pd=post_data: view_comments(pd))

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = TikTokAnalyzer()
    app.run()

if __name__ == "__main__":
    main() 