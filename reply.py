#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import mastodon
import os, random, re, json
import create
from bs4 import BeautifulSoup
import sqlite3

cfg = json.load(open('config.json', 'r'))

client = mastodon.Mastodon(
  client_id=cfg['client']['id'],
  client_secret=cfg['client']['secret'], 
  access_token=cfg['secret'], 
  api_base_url=cfg['site'])

def extract_toot(toot):
	#copied from main.py, see there for comments
	soup = BeautifulSoup(toot, "html.parser")
	for lb in soup.select("br"):
		lb.insert_after("\n")
		lb.decompose()
	for p in soup.select("p"):
		p.insert_after("\n")
		p.unwrap()
	for ht in soup.select("a.hashtag"):
		ht.unwrap()
	for link in soup.select("a"):
		link.insert_after(link["href"])
		link.decompose()
	text = map(lambda a: a.strip(), soup.get_text().strip().split("\n"))
	text = "\n".join(list(text))
	text = re.sub("https?://([^/]+)/(@[^ ]+)", r"\2@\1", text) #put mentions back in
	text = re.sub("^@[^@]+@[^ ]+ *", r"", text) #...but remove the initial one
	text = text.lower() #for easier matching
	return text

class ReplyListener(mastodon.StreamListener):
	def on_notification(self, notification):
		db = sqlite3.connect("haunt.db")
		c = db.cursor()
		visibility = notification['status']['visibility']
		post_id = notification['status']['id']
		mention = extract_toot(notification['status']['content'])
		if notification['type'] == 'mention':
			acct = "@" + notification['account']['acct']
			c.execute('SELECT * FROM the_damned WHERE acct = ?', acct)
			if c.fetchone():
				toot_stuff = create.make_toot()
				toot = toot_stuff['toot']
				cw = toot_stuff['cw']
			else:
				if re.search('the power of crust compells you', mention.lower().strip()):
					toot = "AAAAAAA!!!! I AM BEING EXORCISED!!!"
					cw = None
					c.execute('DELETE FROM the_damned WHERE acct = ?', acct)
				else:
					toot = "You have been haunted by Mastoghost! (say \"the power of crust compells you\" at any point to exorcise me)"
					cw = None
					c.execute('INSERT INTO the_damned VALUES (?)', acct)
			print(acct + " says " + mention)
			if visibility == "public":
				visibility = "unlisted"
		elif notification['type'] == 'follow':
			cw = None
			toot = create.make_ooo(random.randint(10, 500))
		if cw:
			client.status_post(toot, post_id, visibility=visibility, spoiler_text=cw)
		else:
			client.status_post(toot, post_id, visibility=visibility)
		print("replied with " + toot)

rl = ReplyListener()
client.stream_user(rl)
