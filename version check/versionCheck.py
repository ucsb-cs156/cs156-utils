import subprocess
import re

desired_versions = {
    'java': '17',
    'javac': '17',
    'maven': '3.8',
    'node': '16',
    'npm': '8',
    'git': 'any'
}

version_check_commands = {
    'java': 'java --version',
    'javac': 'javac --version',
    'maven': 'mvn --version',
    'node': 'node -v',
    'npm': 'npm -v',
    'git': 'git --version'
}

def get_version(command, regex):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(regex, result.stdout + result.stderr)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error running command {command}: {e}")
    return None

def check_versions():
    softwareMatch = 0
    maxMatch = len(desired_versions)  

    for software, desired_version in desired_versions.items():
        if software == 'git':
            regex = r'git version (\d+\.\d+\.\d+)'
        else:
            regex = r'(\d+\.\d+\.\d+)'
        
        current_version = get_version(version_check_commands[software], regex)
        
        if current_version:
            print(f"{software.capitalize()} version: {current_version}")
            
            if software == 'maven' and desired_version == '3.8':
                desired_version = '3.8.'  
            
            if current_version.startswith(desired_version) or (software == 'git' and desired_version == 'any'):
                print(f"{software.capitalize()} is ok.")
                softwareMatch += 1
            else:
                print(f"{software.capitalize()} version mismatch. Go to https://ucsb-cs156.github.io/s24/info/software.html to download the desired: {desired_version}, Current: {current_version}")
        else:
            print(f"Could not determine {software} version.")

    if softwareMatch == maxMatch:
    	print(f"You are good to go! All the best for CS156")

    else:
    	print(f"Missing softwares: {maxMatch - softwareMatch}")

if __name__ == "__main__":
    check_versions()
