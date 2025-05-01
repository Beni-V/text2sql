#!/usr/bin/env python3
"""
Helper script to generate a .env file with default values.
All values can be customized, but defaults will be used if you just press Enter.
Only the OpenAI API key is required and has no default.
"""

import os
import sys

def generate_env_file():
    # Define the default values for all environment variables except OPENAI_API_KEY
    env_defaults = {
        "SQL_SERVER": "localhost",
        "SQL_DATABASE": "AdventureWorks2022",
        "SQL_USER": "sa",
        "SQL_PASSWORD": "YourNewStrong!Passw0rd123",
        "OPENAI_MODEL": "gpt-4.1-mini",
        "OPENAI_TEMPERATURE": "0"
    }
    
    # Create dictionary to store final values
    env_vars = {}
    
    # Print instructions
    print("=== Environment File Generator ===")
    print("This script will create a .env file with the needed configuration.")
    print("For each value, press Enter to use the default or type your custom value.")
    print("Only the OpenAI API key and the backup file path are required and has no default value.\n")
    print("In order to apply the default values, just press Enter.")

    # Ask for each environment variable
    for key, default in env_defaults.items():
        user_input = input(f"{key} [default: {default}]: ").strip()
        env_vars[key] = user_input if user_input else default

    # Get the OpenAI API key from the user (required)
    openai_api_key = input("OPENAI_API_KEY (required): ").strip()
    bak_file_path = input("BAK_FILE_PATH (required): ").strip()

    # Validate that an API key was provided
    if not openai_api_key or not bak_file_path:
        print("ERROR: OPENAI_API_KEY and BAK_FILE_PATH are required for the .env file to be created.")
        sys.exit(1)

    # Add the API key to the environment variables
    env_vars["OPENAI_API_KEY"] = openai_api_key
    env_vars["BAK_FILE_PATH"] = bak_file_path
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Path to the .env file
    env_file_path = os.path.join(project_root, ".env")
    
    # Check if .env file already exists
    if os.path.exists(env_file_path):
        overwrite = input(f".env file already exists at {env_file_path}. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
    
    # Write the .env file
    with open(env_file_path, 'w') as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")
    
    print(f"\n.env file successfully created at {env_file_path}")
    print("You can run the application now!")

if __name__ == "__main__":
    generate_env_file()
