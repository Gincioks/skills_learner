def writeFile(filename, contents):
    with open(f"./workspace/{filename}", "w") as f:
        f.write(contents)
    return True
