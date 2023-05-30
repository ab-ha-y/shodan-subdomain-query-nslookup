import requests
from bs4 import BeautifulSoup
import re
import sys
import subprocess
import csv
import concurrent.futures

domain = sys.argv[1]

URL = 'https://www.shodan.io/domain/' + domain

response_page = requests.get(URL)
my_soup = BeautifulSoup(response_page.content, 'html.parser')
subs = my_soup.find_all('div', 'card card-padding card-light-blue')

def perform_nslookup(subdomain):
    domain = subdomain + ".inmobi.com"
    command = f"nslookup {domain}"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    result = {
        "Subdomain": domain,
        "Result": output.decode().strip() if output else "",
    }
    return result

results = []

with concurrent.futures.ThreadPoolExecutor() as executor:
    subdomains = []
    for sub in subs:
        find = re.findall('<li>.*?</li>', str(sub))
        match = [re.sub('<li>|</li>', '', s) for s in find]
        subdomains.extend(match)

    futures = [executor.submit(perform_nslookup, subdomain) for subdomain in subdomains]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        results.append(result)

filename = "nslookup_results.csv"

if results:
    keys = results[0].keys()
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"Results saved to '{filename}'.")
else:
    print("No subdomains found. No results to save.")
