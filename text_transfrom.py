import requests
import json
import re

def get_hot_words(blob):

    if len(blob.split(' ')) > 500:
        return set([]), set([]), set([]), set([])
    resp = requests.post("http://text-processing.com/api/tag/", data = {'text':blob})

    jj = re.compile('([A-Za-z]+)/JJ')
    adjs = set(jj.findall(resp.text))

    rb = re.compile('([A-Za-z]+)/RB')
    advs = set(rb.findall(resp.text))

    nn = re.compile('([A-Za-z]+)/NN\\\\')
    nns = re.compile('([A-Za-z]+)/NNS\\\\')
    nouns = set(nn.findall(resp.text) + nns.findall(resp.text))

    vb = re.compile('([A-Za-z]+)/VB\\\\')
    vbd = re.compile('([A-Za-z]+)/VBD\\\\')
    vbn = re.compile('([A-Za-z]+)/VBN\\\\')
    verbs = set(vb.findall(resp.text) + vbd.findall(resp.text) + vbn.findall(resp.text))

    return adjs, advs, nouns, verbs

def get_apt_rep(word, type):
    ffs = re.compile('f:([-+]?\d*\.\d+|\d+)')
    resp = requests.get("https://api.datamuse.com/words?ml={}&md=f".format(word))
    rep_words = json.loads(resp.text)

    if type == "v":
        rep_words = [rep_word for rep_word in rep_words if "v" in rep_word["tags"]]

    if type == "adj":
        rep_words = [rep_word for rep_word in rep_words if "adj" in rep_word["tags"]]

    if type == "n":
        rep_words = [rep_word for rep_word in rep_words if "n" in rep_word["tags"]]

    if len(rep_words) > 10:
        rep_words = rep_words[:10]

    if len(rep_words) == 0:
        return word

    best_rep = rep_words[0]
    best_feq = float(ffs.findall(str(rep_words[0]))[0])

    for rep_word in rep_words:
        feq = float(ffs.findall(str(rep_word))[0])
        if feq < best_feq:
            best_rep = rep_word
            best_feq = feq

    return best_rep['word']



def rep_hot_words(blob):
    adjs, advs, nouns, verbs = get_hot_words(blob)
    for adj in adjs:
        blob = blob.replace(adj, get_apt_rep(adj, "adj"))
    for adv in advs:
        blob = blob.replace(adv, get_apt_rep(adv, "adv"))
    for noun in nouns:
        blob = blob.replace(noun, get_apt_rep(noun, "n"))
    for verb in verbs:
        blob = blob.replace(verb, get_apt_rep(verb, "v"))
    return blob

if __name__=="__main__":
    print rep_hot_words(raw_input())