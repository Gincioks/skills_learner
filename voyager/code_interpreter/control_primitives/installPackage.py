def installPackage(package_name):
    import subprocess
    subprocess.call(['pip', 'install', package_name])
