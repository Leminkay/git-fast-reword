import os
import sys
import hashlib
import zlib


homeDir = "/home/kal/jet/.git/"
commDict = {}


def parse_line(inString):
    line = inString.replace("\t", ' ').replace(" (initial)", '(initial)')
    line = line.split(' ')
    if line[6] == "merge":
        line[8] = " ".join(line[8::])
    else:
        line[7] = " ".join(line[7::])
    return line


def decompress(path):
    file = open(path, 'rb')
    fileData = zlib.decompress(file.read()).decode('utf-8')
    return fileData # returns string


def compress(fileData):
    return zlib.compress(fileData.encode('utf-8')) # return bytes of compressed data


def parse_commit(fileData):
    fileData = fileData.split('\n')
    commit = ''
    parents = []
    author = ''
    committer = ''
    message = ''
    for _l in fileData:
        line = _l.split(' ')
        if line[0] == "commit":
            commit = _l[7::]
        if line[0] == "parent":
            parents.append(line[1])
        if line[0] == "author":
            author = _l[7::]
        if line[0] == "committer":
            committer = _l[10::]
            break
    message = fileData[-2]
    return commit, parents, author, committer, message


def hash_string(fileData):
    return hashlib.sha1(fileData.encode('utf-8')).hexdigest()


def make_new_file( commit, parents, author, committer, message):  # could replace with commit class
    fileData = ''
    fileData = fileData + "commit " + commit + "\n"
    for p in parents:
        fileData = fileData + "parent " + p + "\n"
    fileData = fileData + "author " + author + "\n"
    fileData = fileData + "committer " + committer + "\n"
    fileData = fileData + "\n"
    fileData = fileData + message +"\n"
    hash = hash_string(fileData)

    pathHash = homeDir + "object/" + hash[0:2] + "/" + hash[2:]

    if not os.path.exists(os.path.dirname(pathHash)):
        os.makedirs(os.path.dirname(pathHash))

    with open(pathHash, "wb") as f:
        f.write(compress(fileData))

    return hash


def modify_file_message(hash, newMessage):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[3::]
    commit, parents, author, committer, message = parse_commit(path)
    commDict[hash] = make_new_file(commit, parents, author, committer, newMessage)


def modify_file_parent(hash):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[3::]
    commit, parents, author, committer, message = parse_commit(path)
    changed = False
    for i in range(len(parents)):
        if parents[i] in commDict:
            parents[i] = commDict[parents[i]]
            changed = True
    if changed:
        commDict[hash] = make_new_file(commit, parents, author, committer, message)


logHEAD = homeDir + "logs/HEAD"
# inHash = sys.argv[1]
# newMes = sys.argv[2]
newMes = " "
inHash = " "
# print(inHash)
f = open(logHEAD, 'r')
#lineNum = 0
#print(parse_commit(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))
#commit, parents, author, committer, message = (parse_commit(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))

#print(make_new_file(commit, parents, author, committer, message))

#print(make_new_file(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))
#for line in f.readlines():
#    line = parse_line(line)
#    if line[1] == inHash:
#        modify_file_message(inHash, newMes)
#    if line[0] in commDict.values():
#        modify_file_parent(line[0])
#