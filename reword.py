import os
import sys
import hashlib

homeDir = "/home/kal/jet/"
commDict = {}


def parse_line(inString):
    line = inString.replace("\t", ' ').replace(" (initial)", '(initial)')
    line = line.split(' ')
    if line[6] == "merge":
        line[8] = " ".join(line[8::])
    else:
        line[7] = " ".join(line[7::])
    return line


def parse_commit(file_name):
    commit = []
    parents = []
    author = ''
    committer = []
    message = ''
    for _l in f.readlines():
        line = _l.split(' ')
        if line[0] == "commit":
            commit.append(line[1])
            commit.append(line[2])
        if line[0] == "parent":
            parents.append(line[1])
        if line[0] == "author":
            author = _l[6::]
        if line[0] == "committer":
            author = _l[6::]
            break
    message = f.readlines()[-1]
    return commit, parents, author, committer, message


def hash_file(file_name):
    BLOCK_SIZE = 65536
    hash = hashlib.sha1()  # Create the hash object, can use something other than `.sha256()` if you wish
    with open(file_name, 'rb') as f:  # Open the file to read it's bytes
        fb = f.read(BLOCK_SIZE)  # Read from the file. Take in the amount declared above
        while len(fb) > 0:  # While there is still data being read from the file
            hash.update(fb)  # Update the hash
            fb = f.read(BLOCK_SIZE)
    return hash.hexdigest()


def make_new_file(file, commit, parents, author, committer, message):  # could replace with commit class
    f = open("temp", "w")
    f.write("commit " + commit)
    for p in parents:
        f.write("parent " + p)
    f.write("author " + author)
    f.write("committer " + committer)
    f.write("\n")
    f.write(message)
    f.close()
    hash = hash_file(homeDir + file)
    os.rename(homeDir + file, homeDir + "object/" + hash[0:2] + "/" + hash[3::])
    return hash


def modify_file_message(hash, newMessage):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[3::]
    commit, parents, author, committer, message = parse_commit(path)
    commDict[hash] = make_new_file(path, commit, parents, author, committer, newMessage)


def modify_file_parent(hash):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[3::]
    commit, parents, author, committer, message = parse_commit(path)
    changed = False
    for i in range(len(parents)):
        if parents[i] in commDict:
            parents[i] = commDict[parents[i]]
            changed = True
    if changed:
        commDict[hash] = make_new_file(path, commit, parents, author, committer, message)


logHEAD = homeDir + ".git/logs/HEAD"
# inHash = sys.argv[1]
# newMes = sys.argv[2]
newMes = " "
inHash = " "
# print(inHash)
f = open(logHEAD, 'r')
lineNum = 0
for line in f.readlines():
    line = parse_line(line)
    if line[1] == inHash:
        modify_file_message(inHash, newMes)
    if line[0] in commDict.values():
        modify_file_parent(line[0])
