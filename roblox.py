import requests

ROBLOSECURITY = input("enter your .ROBLOSECURITY cookie :")
login = requests.get("https://www.roblox.com/mobileapi/userinfo", cookies={".ROBLOSECURITY": ROBLOSECURITY})
get_user = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": ROBLOSECURITY})
print("logging in...")
print("account found")
print(f"logged in as {get_user.json()['name']} with id {get_user.json()['id']}")

password = input("would you like to change your password? :"
()
