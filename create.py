#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import markovify
import json
import re, random, multiprocessing, time, sqlite3, shutil, os

def make_ooo(length):
	return ''.join(['O' if bit == '1' else 'o' for bit in bin((1<<(length+1)) + random.randint(0,1<<length))[4:]])

def make_sentence(output):
	class nlt_fixed(markovify.NewlineText):
		def test_sentence_input(self, sentence):
			return True #all sentences are valid <3
	with open("poe.txt", encoding="utf-8") as fp:
		model = nlt_fixed(fp.read())
	sentence = None
	tries = 0
	while sentence is None and tries < 10:
		sentence = model.make_short_sentence(500, tries=10000)
		tries += 1
	sentence = re.sub("^@\u202B[^ ]* ", "", sentence)
	output.send(sentence)

def make_toot(force_markov = False, args = None):
	return make_toot_markov()

def make_toot_markov(query = None):
	tries = 0
	toot = None
	cw = make_ooo(random.randint(3, 10)) + '... (haunting)'
	while toot == None and tries < 25:
		pin, pout = multiprocessing.Pipe(False)
		p = multiprocessing.Process(target = make_sentence, args = [pout])
		p.start()
		p.join(10)
		if p.is_alive():
			p.terminate()
			p.join()
			toot = None
			tries = tries + 1
		else:
			toot = pin.recv()
	if toot == None:
		toot = "oOoOooo... Mistress @lynnesbian@fedi.lynnesbian.space, I was unable to generate a toot using the markov method! This probably means that my corpus wasn't big enough... I need them to be big, Mistress, otherwise I won't work... Can you, um, help me with that, somehow?"
	return {
			"toot":toot,
			"media":None,
			"cw":cw
		}
