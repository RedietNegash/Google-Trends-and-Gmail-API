from ctypes import util
import os
import pickle
# Gmail API utils
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from mimetypes import guess_type as guess_mime_type
import sys
import codecs
from io import BytesIO
from base64 import urlsafe_b64decode
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'useremail@gmail.com'

def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
       
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


service = gmail_authenticate()





# ############ SEARCH ##############


def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages

# ############### GET CONTENT ##################

prompt = (
    "You are given the plain text content of more than one newsletter email. Your task is to extract and return only "
    "the title and the first paragraph of the main news content, ensuring that all ads and sponsored content are removed. "
    "Since the email contains more than one newsletter, you must extract all of them. Follow these steps:\n"
    "    1. Identify the title of the main news content.\n"
    "    2. Extract the first paragraph of the main news content.\n"
    "    3. Remove any ads, sponsored content, or unrelated promotional material.\n"
    "    4. Return a list of all news items with the output format for each news being:\n"
    "    {\n"
    '        "title": title,\n'
    '        "content": content\n'
    "    }"
)




def get_content(text):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([prompt, text])
    print(response.text)

   
# ############### PARSE ##################

def parse_parts(service, parts, message):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        text = ''
        for part in parts:
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            if part.get("parts"):
                parse_parts(service, part.get("parts"), message)
           
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    
                    
            elif mimeType == "text/html":
                 if data:
                     text=urlsafe_b64decode(data).decode()
                     text=urlsafe_b64decode(data).decode()
                     text = BeautifulSoup(text, "html.parser")
                     text =text.get_text()
        get_content(text)
        return text
    
           
             
            

# ############### READ ##################
def read_message(service, message):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    # parts can be the message body, or attachments
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")  #payload-> body & attachment 
    has_subject = False
    if headers:
        
        for header in headers:
            name = header.get("name")
            value = header.get("value")
        
   
    parse_parts(service, parts, message)
    print("="*50)


results = search_messages(service, "from: Microsoft")
print(f"Found {len(results)} results.")
for msg in results:
    read_message(service, msg)



