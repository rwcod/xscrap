import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

class ConfigManager:
    def __init__(self, use_gui=True):
         self.use_gui = use_gui
         if use_gui:
             self.setup_gui()
         try:
            if use_gui:
                self.root = tk.Tk()
                self.root.attributes('-topmost', 1)  # Force window on top
                self.root.after(100, lambda: self.root.attributes('-topmost', 0))
                self.root.title("XScraper Config")
                self.setup_gui()
                self.root.mainloop()
            else:
                self.create_config_cli()
        except tk.TclError as e:
            print(f"GUI failed: {str(e)}")
            self.use_gui = False
            self.create_config_cli()

    def setup_gui(self):
        # Remove variants checkbox
        fields = [
            ('Search Keyword (BTC/#BTC/$BTC):', 'TARGET_KEYWORD'),
            ('Min Profile Followers:', 'MIN_PROFILE_FOLLOWERS'),
            ('Min Post Likes:', 'MIN_POST_LIKES'),
            ('Unique Profiles Target:', 'UNIQUE_PROFILES'),
        ]

        self.entries = {}
        
        for i, (label, key) in enumerate(fields):
            ttk.Label(self.root, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(self.root)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[key] = entry
            
        # Add save button
        ttk.Button(self.root, text="Generate Config",
        ttk.Button(self.root, text="Generate Config", 
                 command=self.save_config).grid(row=6, columnspan=2, pady=10)

    def validate_inputs(self):
        try:
            int(self.entries['MIN_PROFILE_FOLLOWERS'].get())
            int(self.entries['MIN_POST_LIKES'].get())
            int(self.entries['UNIQUE_PROFILES'].get())
            keyword = self.entries['TARGET_KEYWORD'].get().strip()
            if not keyword:
                messagebox.showerror("Error", "Keyword cannot be empty")
            if not keyword or keyword not in ['BTC', '#BTC', '$BTC']:
                messagebox.showerror("Error", "Keyword must be 'BTC', '#BTC', or '$BTC'")
                return False
            return True
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers in numeric fields")
            return False

    def save_config(self):
        if not self.validate_inputs():
            return
            
        config = f"""# Core Parameters
TARGET_KEYWORD={self.entries['TARGET_KEYWORD'].get().strip()}
MIN_PROFILE_FOLLOWERS={self.entries['MIN_PROFILE_FOLLOWERS'].get()}
MIN_POST_LIKES={self.entries['MIN_POST_LIKES'].get()}
UNIQUE_PROFILES={self.entries['UNIQUE_PROFILES'].get()}

# Execution Settings
HEADLESS=True
LOG_LEVEL=INFO
MAX_CONCURRENT=5
"""
        with open('.env', 'w') as f:
            f.write(config)
            
        messagebox.showinfo("Success", "Configuration file (.env) created successfully")
        self.root.destroy()

    def create_config_cli(self):
        """Command-line config creation"""
        print("XScraper Configuration Setup")
        config = {
            'TARGET_KEYWORD': input("Exact Keyword (BTC/#BTC/$BTC): ").strip(),
            'MIN_PROFILE_FOLLOWERS': self._get_number("Min Profile Followers: "),
            'MIN_POST_LIKES': self._get_number("Min Post Likes: "),
            'UNIQUE_PROFILES': self._get_number("Unique Profiles Target: "),
        }

        self._write_config(config)
        print(".env file created successfully")

    def _get_number(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a valid number")

    def _write_config(self, config):
        content = f"""# Core Parameters
TARGET_KEYWORD={config['TARGET_KEYWORD']}
MIN_PROFILE_FOLLOWERS={config['MIN_PROFILE_FOLLOWERS']}
MIN_POST_LIKES={config['MIN_POST_LIKES']}
UNIQUE_PROFILES={config['UNIQUE_PROFILES']}

# Execution Settings
HEADLESS=False  # Default to visible browser
LOG_LEVEL=DEBUG
MAX_CONCURRENT=3
"""
        with open('.env', 'w') as f:
            f.write(content)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        ConfigManager(use_gui=False)
    else:
        try:
            ConfigManager(use_gui=True)
            target_keyword = input("Exact Keyword (BTC/#BTC/$BTC): ").strip()
            if target_keyword not in ['BTC', '#BTC', '$BTC']:
                raise ValueError("Invalid keyword. Please enter 'BTC', '#BTC', or '$BTC'.")
            
            min_profile_followers = self._get_number("Min Profile Followers: ")
            if min_profile_followers < 0:
                raise ValueError("Minimum profile followers must be a positive integer.")
                
            min_post_likes = self._get_number("Min Post Likes: ")
            if min_post_likes < 0:
                raise ValueError("Minimum post likes must be a positive integer.")
            
            unique_profiles_target = self._get_number("Unique Profiles Target: ")
            if unique_profiles_target < 1:
                raise ValueError("Unique profiles target must be at least 1.")

            config = {
                'TARGET_KEYWORD': target_keyword,
                'MIN_PROFILE_FOLLOWERS': min_profile_followers,
                'MIN_POST_LIKES': min_post_likes,
                'UNIQUE_PROFILES': unique_profiles_target,
            }
            
            self._write_config(config)
            print(".env file created successfully")
        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Falling back to CLI config")
            print(f"An error occurred: {e}")

    def _get_number(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a valid number")

    def _write_config(self, config):
        content = f"""# Core Parameters
TARGET_KEYWORD={config['TARGET_KEYWORD']}
MIN_PROFILE_FOLLOWERS={config['MIN_PROFILE_FOLLOWERS']}
MIN_POST_LIKES={config['MIN_POST_LIKES']}
UNIQUE_PROFILES={config['UNIQUE_PROFILES']}

# Execution Settings
HEADLESS=False  # Default to visible browser
LOG_LEVEL=DEBUG
MAX_CONCURRENT=3
"""
        with open('.env', 'w') as f:
            f.write(content)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
            ConfigManager(use_gui=False) 
    else:
        try:
            ConfigManager(use_gui=True)
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Falling back to CLI config")
            ConfigManager(use_gui=False) 