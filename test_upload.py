import requests

url = "http://localhost:8000/predict/file"
file_path = "test_reasons.csv"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

if response.status_code == 200:
    with open("analyzed_test_reasons.csv", "wb") as f:
        f.write(response.content)
    print("Success! File saved as analyzed_test_reasons.csv")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
