import tkinter as tk
from tkinter import messagebox, scrolledtext
from panos import panorama, firewall
from panos.panorama import DeviceGroup
from panos.policies import PreRulebase, SecurityRule

def validate_fields():
    if not username_entry.get() or not password_entry.get() or not ip_entry.get():
        messagebox.showerror("Input Error", "All fields (Username, Password, IP Address) must be filled out.")
        return False
    return True

def connect_to_device():
    ip = ip_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    
    try:
        if device_type.get() == "Panorama":
            device = panorama.Panorama(ip, username, password)
        else:
            device = firewall.Firewall(ip, username, password)
        return device
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect: {e}")
        return None

def get_device_groups():
    if not validate_fields():
        return
    
    if device_type.get() != "Panorama":
        messagebox.showerror("Error", "Device groups can only be retrieved from Panorama.")
        return
    
    device = connect_to_device()
    if device is None:
        return
    
    try:
        device_groups = DeviceGroup.refreshall(device)
        device_groups_listbox.delete(0, tk.END)
        for group in device_groups:
            device_groups_listbox.insert(tk.END, group.name)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get device groups: {e}")

def show_pre_rules():
    if not validate_fields():
        return
    
    selected_group = device_groups_listbox.get(tk.ACTIVE)
    if not selected_group:
        messagebox.showerror("Selection Error", "No device group selected.")
        return

    device = connect_to_device()
    if device is None:
        return
    
    try:
        dg = DeviceGroup(device, selected_group)
        pre_rulebase = PreRulebase()
        dg.add(pre_rulebase)
        security_rules = SecurityRule.refreshall(pre_rulebase)
        pre_rules_text.delete(1.0, tk.END)
        for rule in security_rules:
            pre_rules_text.insert(tk.END, f"Name: {rule.name}, Source: {rule.source}, Destination: {rule.destination}, Action: {rule.action}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get pre-rules: {e}")

def check_jobs():
    if not validate_fields():
        return
    
    device = connect_to_device()
    if device is None:
        return
    
    try:
        jobs = device.op('show jobs all')
        jobs_text.delete(1.0, tk.END)
        jobs_text.insert(tk.END, jobs)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check jobs: {e}")

# GUI setup
root = tk.Tk()
root.title("Palo Alto Firewall Manager")

# Username label and entry
tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

# Password label and entry
tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

# IP Address label and entry
tk.Label(root, text="IP Address:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
ip_entry = tk.Entry(root)
ip_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

# Device type radio buttons
device_type = tk.StringVar(value="Panorama")
tk.Radiobutton(root, text="Panorama", variable=device_type, value="Panorama").grid(row=3, column=0, padx=10, pady=5, sticky='e')
tk.Radiobutton(root, text="Firewall", variable=device_type, value="Firewall").grid(row=3, column=1, padx=10, pady=5, sticky='w')

# Get Device Groups button
get_device_groups_button = tk.Button(root, text="Get Device Groups", command=get_device_groups)
get_device_groups_button.grid(row=4, column=0, columnspan=2, pady=10)

# Device Groups listbox
device_groups_listbox = tk.Listbox(root, height=10)
device_groups_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

# Show Pre-Rules button
show_pre_rules_button = tk.Button(root, text="Show Pre-Rules", command=show_pre_rules)
show_pre_rules_button.grid(row=6, column=0, columnspan=2, pady=10)

# Pre-Rules display
pre_rules_text = scrolledtext.ScrolledText(root, width=50, height=10)
pre_rules_text.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

# Check Jobs button
check_jobs_button = tk.Button(root, text="Check Jobs", command=check_jobs)
check_jobs_button.grid(row=8, column=0, columnspan=2, pady=10)

# Jobs display
jobs_text = scrolledtext.ScrolledText(root, width=50, height=10)
jobs_text.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()