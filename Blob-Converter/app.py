import requests
import os
import time

DATA_SOURCE_NETWORK_URL = os.getenv("DATA_SOURCE_NETWORK_URL")
if DATA_SOURCE_NETWORK_URL is None:
    raise

def main():   
    while True:     
        time.sleep(10)
        try:
            url = DATA_SOURCE_NETWORK_URL + "/fx/get/sensorreadings"
            print(url)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print("Received data:")
            print(data)
            # Add conversion logic here if needed
        except Exception as e:
            print(f"Error fetching data: {e}")


if __name__ == "__main__":
    main()