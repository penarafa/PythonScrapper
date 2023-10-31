from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import csv
import os

api_id = 28900883
api_hash = 'c637ff2157e86ef30eab9695f8e8f107'
phone = '+51907300205'
client = TelegramClient(phone, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Enter the code: '))

chats = []
last_date = None
chunk_size = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup:
            groups.append(chat)
    except:
        continue

print('Choose a group to scrape members from:')
i = 0
for g in groups:
    print(str(i) + '- ' + g.title)
    i += 1

g_index = input("Enter a Number: ")
target_group = groups[int(g_index)]

print('Fetching Members...')
all_participants = client.get_participants(target_group, aggressive=True)

def is_duplicate(user, existing_data):
    # Check if a user is a duplicate based on user ID
    for row in existing_data:
        if user.id == int(row[1]):
            return True
    return False

file_exists = os.path.isfile("members.csv")
existing_data = []

if file_exists:
    with open("members.csv", "r", encoding='UTF-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        existing_data = list(reader)

with open("members.csv", "a", encoding='UTF-8', newline='') as f:
    writer = csv.writer(f, delimiter=",")
    if not file_exists:
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])

    for user in all_participants:
        if not is_duplicate(user, existing_data):
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

print('Members scraped successfully.')