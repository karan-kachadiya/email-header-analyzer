import os
import sys
import re
import datetime
from email import policy
from email.parser import BytesParser

# Function to extract email headers
def parse_email_headers(file_path):
    """
    Reads an email file and extracts key headers.
    :param file_path: Path to the email file (.eml format)
    :return: Dictionary containing extracted headers
    """

    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    # Open and parse email file
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract key headers
    headers = {
        "From": msg.get("From"),
        "To": msg.get("To"),
        "Subject": msg.get("Subject", "No Subject"),
        "Date": msg.get("Date"),
        "Return-Path": msg.get("Return-Path"),
        "Received": msg.get_all("Received", []),
        "SPF": extract_auth_result(msg, "spf="),
        "DKIM": extract_auth_result(msg, "dkim="),
        "DMARC": extract_auth_result(msg, "dmarc="),
    }

    return headers

# Function to extract SPF, DKIM, and DMARC results
def extract_auth_result(msg, auth_type):
    """
    Finds authentication results for SPF, DKIM, and DMARC.
    :param msg: Parsed email object
    :param auth_type: The authentication type to extract (spf, dkim, dmarc)
    :return: The authentication result (pass, fail, or Not Found)
    """

    auth_results = msg.get_all("Authentication-Results", [])
    
    for result in auth_results:
        match = re.search(rf"{auth_type}(\w+)", result, re.IGNORECASE)
        if match:
            return match.group(1)  # Extract result (e.g., pass, fail)
    
    return "Not Found"

# Function to save results to a log file
def save_to_log(headers):
    """
    Saves analyzed email headers to a log file with timestamps.
    :param headers: Dictionary of extracted email headers
    """

    log_folder = "logs"
    log_file_path = os.path.join(log_folder, "email_analysis_log.txt")

    # Create the logs folder if it doesn't exist
    os.makedirs(log_folder, exist_ok=True)

    # Get current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append results to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(f"\nEmail Header Report - {current_time}\n")
        log_file.write("=" * 80 + "\n")

        for key, value in headers.items():
            if isinstance(value, list):  # Handling multiple "Received" headers
                log_file.write(f"{key}:\n")
                for item in value:
                    log_file.write(f"  {item}\n")
            else:
                log_file.write(f"{key}: {value}\n")

        log_file.write("=" * 80 + "\n")

    print(f"Results saved to: {log_file_path}")

# Main function to handle user input and execute the script
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python email_header_analyzer.py <email_file>")
        sys.exit(1)

    email_file = sys.argv[1]

    # Run header extraction and save to log
    headers = parse_email_headers(email_file)
    save_to_log(headers)

    print("Processing completed. Check the 'logs' folder for the results.")

