I needed a script that would automatically get all of the ip addresses for my stores and then uplaod them to Microsoft on a weekly basis and create a trusted location. I did this so that we wouldn't have to use MFA for all of the stores and they would be able to log in with just their username and password. Since all of the data was sitting in Meraki I decided to pull it from there and then upload it to Microsoft. Here is the script that goes through all of the wireless devices in my Meraki org and then updates Microsoft with that data and sends an email when it's been done successfully. I've posted the script for reference and anonymized the portions of the script that I didn't put into the cred.py.