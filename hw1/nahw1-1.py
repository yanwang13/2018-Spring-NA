import requests
import sys
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from PIL import Image, ImageEnhance
import pytesseract
import getpass

def main():
    """"usage: main.py [-h] username

        Web crawler for NCTU class schedule.

        positional arguments:
          username    username of the NCTU portal

        optinal arguments: 
          -h, --help show this help message and exit
    """
    if len(sys.argv)!=2:
        print("usage: main.py [-h] username")
        sys.exit(0)

    if sys.argv[1] in ('-h', '--help'):
        print("usage: main.py [-h] username\n")
        print("Web crawler for NCTU class schedule.\n")
        print("positional arguments:\n  username\tusername of the NCTU portal\n")
        print("optinal arguments:\n  -h, --help show this help message and exit")
        sys.exit(0)

    student_number = sys.argv[1]
    passwd = getpass.getpass("Portal Password:")

    s_req = requests.session()
    resp = s_req.get("https://portal.nctu.edu.tw/portal/login.php")

    #pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
    #tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata"'
    guest = ""

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
    }

    count = 0
    while True:
        while True:
            if guest.isdigit() and len(guest)==4:
                break
            else:
                img_url = "https://portal.nctu.edu.tw/captcha/pic.php"
                img_resp = s_req.get(img_url, stream=True) #get the safecode img
                safe_code_img = img_resp.content

                with open("code.jpg", "wb") as jpg:
                       jpg.write(safe_code_img)
                jpg.close

                img = Image.open("code.jpg")
                img = ImageEnhance.Brightness(img).enhance(2.0)
                img = ImageEnhance.Contrast(img).enhance(2.0)
                img = img.convert('L')
                for i in range(img.size[0]):
                    for j in range(img.size[1]):
                        if(img.getpixel((i,j))>150):
                            img.putpixel((i,j), 255)
                        else:
                            img.putpixel((i,j), 0)

                #guest = pytesseract.image_to_string(img, config = tessdata_dir_config)
                guest = pytesseract.image_to_string(img)
                
        code = guest #the guset code is 4 digit number
        data= {
            "username": student_number,
            "Submit2": "Login",
            "pwdtype": "static",
            "password": passwd,
            "seccode": code,    
        }
        response = s_req.post("https://portal.nctu.edu.tw/portal/chkpas.php?", data=data, headers=headers)
        response = s_req.get("https://portal.nctu.edu.tw/LifeRay/PortalMain.php")
        response = s_req.get("https://portal.nctu.edu.tw/portal/relay.php?D=cos")
        response.encoding = 'UTF-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        temp = soup.find(id="txtId")
        if temp==None:
            count = count +1
            if count >=5:
                print("wrong password! please try again.")
                sys.exit(0)
        else:
            txtId = temp.get('value')
            break
        #txtId = soup.find(id="txtId").get('value')
        #if txtId == None: #wrong guset of the safe code
        #    continue
        #else:
        #    break
        

    #get the jwt datas
    txtPw = soup.find(id="txtPw").get('value')
    ldapDN = soup.find(id="ldapDN").get('value')
    idno = soup.find(id="idno").get('value')
    s = soup.find(id="s").get('value')
    t = soup.find(id="t").get('value')
    txtTimestamp = soup.find(id="txtTimestamp").get('value')
    hashKey = soup.find(id="hashKey").get('value')
    jwt = soup.find(id="jwt").get('value')
    Button1 = soup.find(id="Button1").get('value')


    data_jwt = {
        "txtId": txtId,
        "txtPw": txtPw,
        "ldapDN": ldapDN,
        "idno":idno,
        "s": s,
        "t": t,
        "txtTimestamp": txtTimestamp,
        "hashKey": hashKey,
        "jwt": jwt,
        "Chk_SSO": "on",
        "Button1": Button1
    }

    response = s_req.post("https://course.nctu.edu.tw/jwt.asp", data=data_jwt, headers=headers)
    response = s_req.get("https://course.nctu.edu.tw/index.asp")
    response = s_req.get("https://course.nctu.edu.tw/adSchedule.asp")
    response.encoding = 'big5'
    soup = BeautifulSoup(response.text, 'html.parser')
    #print(soup)

    temp = soup.find_all("table") #get the schedule table from temp[1]
    sch = temp[1].find_all("tr")

    def deal_with_txt(txt):
        if type(txt) == str:
            txt = txt.strip()
            txt = txt.replace("\r", "").replace("\n", "").replace("\t", "")
        return txt

    for i in range(1,18):
        temp_row = []
        cls = sch[i].find_all("td")
        for c in cls:
            temp_row.append(deal_with_txt(c.text))
        if i==1:
            table = PrettyTable(temp_row)
        else:
            table.add_row(temp_row)
    print(table)

if __name__ == '__main__':
    main()