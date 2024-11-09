import os
import subprocess
import configparser

# Path to configuration file
CONFIG_FILE = "brew_packages.conf"

# Check if Homebrew is installed
def check_homebrew():
    if subprocess.run(["which", "brew"], capture_output=True).returncode != 0:
        print("Homebrew not found. Installing Homebrew...")
        subprocess.run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True
        )
    else:
        pass#print("Homebrew is installed.")

def update_homebrew():
    """display_menu: Update Homebrew"""
    check_homebrew()
    print("Updating Homebrew...")
    subprocess.run(["brew", "update"])

def get_packages(section):
    """Helper function to read package lists from config file"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config[section].get("packages", "").split(",") if section in config else []

def install_packages():
    """display_menu: Install/Update packages from config file"""
    check_homebrew()
    packages = get_packages("install")
    if packages == ['']:
        print("No packages to Install.")
        return
    for package in packages:
        print(f"Installing/updating {package}...")
        subprocess.run(["brew", "install", package])
        subprocess.run(["brew", "upgrade", package])

def remove_packages():
    """display_menu: Remove packages from config file"""
    check_homebrew()
    packages = get_packages("remove")
    if packages == ['']:
        print("No packages to remove.")
        return
    for package in packages:
        print(f"Removing {package}...")
        subprocess.run(["brew", "uninstall", package])

def check_outdated():
    """display_menu: Check for outdated packages"""
    check_homebrew()
    print("Checking for outdated packages...")
    
    # Run brew outdated and capture the output
    result = subprocess.run(["brew", "outdated"], capture_output=True, text=True)
    
    # Split output by lines to get package names
    outdated_packages = result.stdout.strip().splitlines()
    
    if outdated_packages:
        # Join the list into a comma-separated string
        outdated_str = ",".join(outdated_packages)
        print(f"Outdated packages: {outdated_str}")
        choice = input(f"\nHomebrew Outdated Packages Menu\n1. Update All Packages\n2. Update Select Packages\n3. Main Menu\nEnter your choice: ")
        if choice == '1':
            update_outdated_packages(select_packages=None)
        elif choice == '2':
            update_select_packages = config.get("update", "update_select_packages", fallback="").split(",")
            #print(update_select_packages)
            update_outdated_packages(select_packages=update_select_packages)
    else:
        print("All packages are up to date.")

def list_installed_packages():
    """display_menu: List currently installed packages"""
    check_homebrew()

    print("Currently installed Homebrew packages:")
    subprocess.run(["brew", "list"])
    
    # Get the list of formulae
    #formulae_result = subprocess.run(["brew", "list", "--formula"], capture_output=True, text=True)
    #formulae_packages = formulae_result.stdout.strip().splitlines()
    
    # Get the list of casks
    #casks_result = subprocess.run(["brew", "list", "--cask"], capture_output=True, text=True)
    #cask_packages = casks_result.stdout.strip().splitlines()
    
    

def update_outdated_packages(select_packages=None):
    """outdated_menu: Update selected or all outdated packages"""
    check_homebrew()

    # If select_packages is None, update all outdated packages
    if select_packages is None:
        print("Updating all outdated packages...")
        subprocess.run(["brew", "upgrade"])
    else:
        # Update only the specified packages
        print(f"Updating selected packages: {', '.join(select_packages)}")
        if select_packages == ['']:
            print("No Packages to Update.")
            return
        for package in select_packages:
            subprocess.run(["brew", "upgrade", package])

# Load config settings
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Determine which functions should be displayed in the menu
def get_menu_functions(func_doc_keyword):
    # Retrieve display menu settings from the config file
    display_menu_services = config.get("menu", "display_menu_services", fallback="all")
    display_menu_exceptions = config.get("menu", "display_menu_exceptions", fallback="").split(",")
    

    # Get all functions with "display_menu:" in the docstring
    functions = {
        name: func for name, func in globals().items()
        if callable(func) and func_doc_keyword in (func.__doc__ or "")
    }

    # Apply display menu settings
    if display_menu_services == "all":
        return functions
    elif display_menu_services == "all_except":
        return {name: func for name, func in functions.items() if name not in display_menu_exceptions}
    elif display_menu_services == "none_except":
        return {name: func for name, func in functions.items() if name in display_menu_exceptions}
    else:
        print("Invalid display_menu_services setting in config. Defaulting to 'all'.")
        return functions

# Display the menu dynamically
def display_menu(func_doc_keyword):
    menu_functions = get_menu_functions(func_doc_keyword)
    print("\nHomebrew Command Line Menu")
    for idx, (name, func) in enumerate(menu_functions.items(), start=1):
        print(f"{idx}. {func.__doc__.split(': ')[1]}")  # Displaying function description

    print(f"{len(menu_functions) + 1}. Exit")

# Main function
def main():
    menu_functions = list(get_menu_functions("display_menu:").items())  # Convert to list for index-based access
    while True:
        display_menu("display_menu:")
        choice = input("Enter your choice: ")
        print("\n",end="\r")
        # Check for valid integer choice
        try:
            choice = int(choice)
            if choice == len(menu_functions) + 1:
                print("Exiting program.")
                break
            elif 1 <= choice <= len(menu_functions):
                func = menu_functions[choice - 1][1]
                func()  # Call the selected function
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

        input("\n(Hit [Enter] to go back to Menu)")

if __name__ == "__main__":
    main()
