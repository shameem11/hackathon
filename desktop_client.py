import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from gmail_service import authenticate_gmail, get_emails
from openai_phishing import detect_phishing

# Create the main GUI window
class GmailPhishingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Phishing Detector")
        self.root.geometry("600x500")

        # Title Label
        tk.Label(root, text="Gmail Phishing Detector", font=("Arial", 16, "bold")).pack(pady=10)

        # Button to fetch emails
        self.fetch_btn = tk.Button(root, text="Fetch Unread Emails", command=self.fetch_emails)
        self.fetch_btn.pack(pady=5)

        # Listbox to display email subjects
        self.email_listbox = tk.Listbox(root, width=70, height=10)
        self.email_listbox.pack(pady=10)
        self.email_listbox.bind("<<ListboxSelect>>", self.show_email_details)

        # Text area for email body
        self.email_body = scrolledtext.ScrolledText(root, width=70, height=10, wrap=tk.WORD)
        self.email_body.pack(pady=10)

        # Phishing detection button
        self.detect_btn = tk.Button(root, text="Check for Phishing", command=self.detect_phishing)
        self.detect_btn.pack(pady=5)

        # Status Label
        self.status_label = tk.Label(root, text="", font=("Arial", 12), fg="red")
        self.status_label.pack(pady=5)

        self.emails = []  # Store fetched emails

    def fetch_emails(self):
        """Fetch unread emails and display subjects in the listbox."""
        self.status_label.config(text="Fetching emails...")
        self.email_listbox.delete(0, tk.END)
        self.emails = []
        
        try:
            service = authenticate_gmail()
            self.emails = get_emails(service)
            
            if not self.emails:
                self.status_label.config(text="No unread emails.")
                return
            
            for idx, email in enumerate(self.emails):
                self.email_listbox.insert(idx, f"From: {email['from']}")
            
            self.status_label.config(text=f"Fetched {len(self.emails)} unread emails.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {e}")

    def show_email_details(self, event):
        """Display the selected email's body in the text area."""
        selected_idx = self.email_listbox.curselection()
        if not selected_idx:
            return
        email = self.emails[selected_idx[0]]
        self.email_body.delete(1.0, tk.END)
        self.email_body.insert(tk.END, email['body'])

    def detect_phishing(self):
        """Analyze the displayed email for phishing threats."""
        email_text = self.email_body.get(1.0, tk.END).strip()
        if not email_text:
            messagebox.showwarning("Warning", "No email selected.")
            return
        
        self.status_label.config(text="Analyzing for phishing...")
        is_phishing = detect_phishing(email_text)

        if is_phishing:
            self.status_label.config(text="⚠️ Phishing detected!", fg="red")
        else:
            self.status_label.config(text="✅ Email seems safe.", fg="green")

# Run the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = GmailPhishingApp(root)
    root.mainloop()
