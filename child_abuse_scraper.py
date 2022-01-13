from bs4 import BeautifulSoup as bsoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import requests
import smtplib
import time

### Websites
websites = ['https://atlfmnews.com/news/news/',
            'https://pinkfmonlinegh.com/category/news/',
            'http://www.lorlornyofm.com/category/news/', 
            'https://otecfmghana.com/',
            'https://spiritfmonline.com/category/ghanaian-news/', 
            'https://zaaradio.com/news/',
            'https://www.myjoyonline.com', 
            'https://citinewsroom.com/news/',
            'https://www.a1radioonline.com/category/news',
            'https://anapuafm.com/local-news/',
            'https://focusnewsroom.com/news/',
            'http://agoofmonline.com/category/local/',
            'https://beachfmonline.com/category/news/',
            'https://skyypowerfm.com/news/',
            'https://www.ghanaweb.com/GhanaHomePage/crime/'
           ]
header = {
    "User-Agent":"Mozilla/5.0 (X11; Linux x84_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

### Keywords
ages = [f'{num}-year old' for num in range(1, 19)] + [f'{num}-year-old' for num in range(1, 19)] + \
         [f'{num}-month old' for num in range(1, 24)] + [f'{num}-month-old' for num in range(1, 24)] +\
         [f'{num}-yr old' for num in range(1, 19)] + [f'{age}-year' for age in age_words] +\
         [f'{age} year' for age in age_words] + [f'{age} month' for age in age_words]

acts = ['sex', 'sexual', 'sexually', 'defile', 'defiled', 'defilement', 'defiling', 'rape', 'raped', 'raping', 'abuse',
        'abused', 'abusing', 'beating', 'beat', 'assault', 'assaulting', 'assaulted', 'burn', 'burnt', 'burned', 'burning',
        'harass', 'harassed', 'harassment', 'harassing', 'hurt', 'hurting', 'impregnate', 'impregnating', 'impregnated',
        'traffick', 'trafficked', 'trafficking', 'killed', 'killing', 'kill', 'molest', 'molestation', 'molesting',
        'slaughter', 'slaughtering', 'slaughtered', 'spank', 'spanked', 'massacre', 'massacred', 'caning', 'cane', 'slap',
        'slapped', 'slapping', 'abduct', 'abduction', 'abducting', 'abducted', 'inflict', 'inflicted', 'infliction', 
        'inflicting', 'murder', 'murdered', 'murdering', 'murderer', 'rapist', 'sell', 'selling', 'sold', 'lash', 'lashed',
        'poison', 'poisoning', 'poisoned', 'sodomy', 'sodomized', 'sodomizing', 'incest', 'sodomy', 'abandon', 'abandoned',
        'abandoning']

id_words = ['police', 'arrest', 'arresting', 'arrested', 'court', 'bail', 'bailed', 'jail', 'jailed', 'jailing', 'catch', 
            'catching', 'caught', 'remand', 'remanded', 'prosecute', 'prosecutor', 'prosecuted', 'victim', 'victimized',
           'complainant', 'alleged', 'inform', 'informed', 'suspect', 'suspected', 'convict', 'convicted']

victim = ['child', 'children', 'baby', 'babies', 'boy', 'boys', 'girl', 'girls', 'son', 'sons', 'daughter', 'daughters',
          'student', 'students', 'pupil', 'pupils', 'minors', 'minor', 'niece', 'nephew', 'teenage', 'stepson', 'grandson']

keywords = acts + id_words + victim + ages

### Retrieve Urls
def detect_child_abuse():
    new_link = []
    for website in websites:
        website_content = requests.get(website, headers=header).content
        website_soup = bsoup(website_content, 'lxml')
        if website == 'https://www.ghanaweb.com/GhanaHomePage/crime/':
            website_links = ['https://www.ghanaweb.com' + str(a['href']) for a in website_soup.find_all('a') if 'crime' in str(a)]
        else:
            website_links = set([str(a['href']) for a in website_soup.find_all('a') if 'href' in str(a)])
        for link in website_links:
            if any(key in link for key in keywords):
                try:
                    link_soup_ = bsoup(requests.get(link, headers=header).content, 'lxml')
                except:
                    pass
                link_soup = ''.join([p.text for p in link_soup_.find_all('p')])
                link_soup = link_soup.lower()
                link_soup = re.split('\. |  |, |, |\s', link_soup)
                if any(key in link_soup for key in acts) and any(id_ in link_soup for id_ in id_words) and any(_key in link_soup for _key in victim):
                    new_link.append(link)
    return new_link
  
 links_scraped = detect_child_abuse()

### Determine New articles
with open('all_links.txt', 'r') as all_links:   # open a file which contains old articles
    all_links_scraped = all_links.readlines()
    
all_links_scraped = [link.strip() for link in all_links_scraped]

with open('all_links.txt', 'a') as all_links:                     # appends the new links to the end of the old file and adds the time they were generated
    new_links = list(set(links_scraped) - set(all_links_scraped))
    all_links.write('\n\n' + time.ctime() + '\n\n')
    for content in new_links:
        all_links.write(content+'\n')
        
### Sending Email
mail_content = '\n\n'.join(list(new_links))
mail_content = f'''Hi *****,
Kindly find below some links to possible child abuse cases. These links were scraped today at {time.ctime()}. 
The links are from 15 websites. The keywords used in detecting the cases are many so as to capture all the cases. 
This may lead to the presence of other cases which may not be directly child abuse related. 
Kindly ignore such links.


''' + mail_content + \
'\n\n Best regards,\n PDA Web Scraper'

sender_address = ********** # sender email
sender_pass = **********    # sender email password
receiver_add = *********    # receiver email address
message = MIMEMultipart()
message['From'] = sender_address
message['To'] = receiver_add
message['Subject'] = 'Links to Child Abuse Cases'
message.attach(MIMEText(mail_content, 'plain'))
session = smtplib.SMTP('smtp.gmail.com', 587)
session.starttls()
session.login(sender_address, sender_pass)
text = message.as_string()
session.sendmail(sender_address, receiver_add, text)
session.quit()
print('MAIL SENT')
