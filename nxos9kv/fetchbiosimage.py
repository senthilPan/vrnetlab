import requests
import sys
import os

def download_file_from_index(url):
    """
    Downloads a file based on a link found in the index.html page at the given URL.
    
    Args:
        url (str): The URL of the index.html page.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print("URL not valid: ", url, ", code: ", response.status_code)
    start = response.text.find('a href="edk2.git-ovmf-x64-')
    end =  response.text.find('.rpm', start)
    start =  response.text.find('edk2', start)
    filename = response.text[start:end+4]
    fileurl = url + '/' + filename
    print(fileurl)

    # Download the file
    download_response = requests.get(fileurl, stream=True)
    if download_response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in download_response.iter_content(1024):
                f.write(chunk)
        print("File downloaded successfully: ", filename)
    else:
        print("Error downloading file: ", download_response.status_code)
        sys.exit(1)

    cmd = "rpm2cpio " + filename + " | cpio -idm"
    os.system(cmd)
    os.system("cp ./usr/share/edk2.git/ovmf-x64/OVMF-pure-efi.fd OVMF-pure-efi.fd") 
    sys.exit(0)

# main code
# exit, if bios already downloaded
if os.path.exists("./OVMF-pure-efi.fd"):
    sys.exit(0)

# fetch the x64 bios file
url = "https://www.kraxel.org/repos/jenkins/edk2/"
download_file_from_index(url)
