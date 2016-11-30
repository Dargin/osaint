# o-saint
OSINT Tool

1) Install python 3</br>
    sudo apt-get install python3
    
2) Install dnsrecon (kali already has this)</br>
    https://github.com/darkoperator/dnsrecon/wiki/Installation-Instructions
    Once downloaded you'll need to create a link dnsrecon.py file in the /usr/local/bin and name it just dnsrecon (i.e. if you cloned dnsrecon to /home/user -- ln -s /home/user/dnsrecon/dnsrecon.py /usr/local/bin/dnsrecon). Verify it's working by typing in a command prompt "dnsrecon" to ensure it can run from the commandline properly.

3) Install whois (kali already has this)</br>
    sudo apt-get install whois
    
4) Install python3-pip</br>
  sudo apt-get install python3-pip
  
5) Install requirements</br>
    pip3 install -r requirements.txt

6) Copy o_saint/config_example.py to o_saint/config.py

7) setup api keys in the config.py</br>
    email hunter = https://hunter.io/api</br>
    Builtwith = https://api.builtwith.com/</br>
    fullcontact = https://www.fullcontact.com/developer/docs/</br>
	Click on "Sign up" and create your account. Once done, got to https://api.fullcontact.com again</br>    
	Click on "Sign In" then developer portal. activate your account for the API function and get your API key.
    Shodan = https://www.shodan.io - setup an account, once logged in click "show api key" on the top right of the screen.

8) setup database by running these three commands:</br>
    python3 manage.py migrate</br>
    python3 manage.py makemigrations site_scan</br>
    python3 manage.py migrate site_scan
    
9) run the server</br>
    python3 manage.py runserver
    
10) ready to go, browse to http://127.0.0.1:8000/o_saint
