def read_file(filename):
    with open(f"./workspace/{filename}", "r") as f:
        return f.read()
