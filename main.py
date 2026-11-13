import requests

def ask(prompt):
    answer = input(f"\033[91mSHADOW-TOOLS>>\033[0m {prompt}")
    if answer.strip().casefold() == "exit":
        print("Exiting the program.")
        exit()
    return answer

print(r"  /$$$$$$  /$$                       /$$                        ")
print(r" /$$__  $$| $$                      | $$                        ")
print(r"| $$  \__/| $$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$  /$$  /$$  /$$    1# lookup")
print(r"|  $$$$$$ | $$__  $$ |____  $$ /$$__  $$ /$$__  $$| $$ | $$ | $$    2# spam")
print(r" \____  $$| $$  \ $$  /$$$$$$$| $$  | $$| $$  \ $$| $$ | $$ | $$    3# delete")
print(r" /$$  \ $$| $$  | $$ /$$__  $$| $$  | $$| $$  | $$| $$ | $$ | $$    4# edit")
print(r"|  $$$$$$/| $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/|  $$$$$/$$$$/.   5# raid")
print(r" \______/ |__/  |__/ \_______/ \_______/ \______/  \_____/\___/ ") 
print("                                                                 ")                                                                                                                               
print("              $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("              $$$     Shadow's python tools    $$$")
print("              $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
source = ask("enter your choice :")
if source == "1":
    webhook = ask("enter your webhook url :")
    discord_webhook = requests.get(webhook)
    webhook_data = discord_webhook.json()
    print(f"Webhook connected to {webhook_data['name']}")
    print(f"Webhook ID: {webhook_data['id']}")

elif source == "2":
    webhook = ask("enter your webhook url :")
    message = ask("enter your message :")
    count = int(ask("amount of messages to send :"))
    send = {"content": message}
    for i in range(count):
        requests.post(webhook, json=send)
        print(f"sent message {i+1} of {count}")

elif source == "3":
    webhook = ask("enter your webhook url :")
    requests.delete(webhook)
    print("webhook deleted successfully")

elif source == "4":
    webhook = ask("enter your webhook url :")
    new_name = ask("enter new name for the webhook :")
    edit_data = {"name": new_name,
    requests.patch(webhook, json=edit_data)
    print(webhook_data['name'] + " webhook edited successfully")

elif source == "5":
    webhooks = input("enter 5+ webhooks :")
    if webhooks == "":
        print("enter a valid webhook")

