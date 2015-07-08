import django
import os
import json
import md5
import re

os.environ["DJANGO_SETTINGS_MODULE"] = "mockingsite.settings"
django.setup()

import mocktest.DAOUtil

nonspace = re.compile(r'\S')
companyName = 'All Company'
positionName = 'Software Developer'
hashDict = {}


def isEmpty(content):
    if len(content.strip()) == 0:
        return True
    return False


def iterparse(j):
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        matched = nonspace.search(j, pos)
        if not matched:
            break
        pos = matched.start()
        decoded, pos = decoder.raw_decode(j, pos)
        yield decoded


def run():
    data = open("items.json").read()
    for decoded in iterparse(data):
        for _dict in decoded:
            if isEmpty(_dict['question']) or isEmpty(_dict['answer']):
                continue
            # insert into hashDict
            md5Hash = md5.new()
            md5Hash.update(_dict['question'].encode('utf-8'))
            digest = md5Hash.digest()
            if digest not in hashDict:
                hashDict[digest] = _dict['question']
                mocktest.DAOUtil.addQuestion(
                    companyName,
                    positionName,
                    _dict['question'],
                    _dict['answer'],
                    timeToSolve=30)


if __name__ == '__main__':
    run()
