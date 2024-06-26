def fetch_data(url, params):
    response = requests.get(url, params)
    data = response.json()
    return data
