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
        del line[9:]
    else:
        line[7] = " ".join(line[7::])
        del line[8:]
    if line[6] == "commit(initial):":
        line[6] = "commit (initial):"
    return line

def parsed_to_string(line):
    str = ''
    for i in range(5):
        str = str + line[i] + ' '
    str = str + line[5]
    str = str + '\t'
    for i in range(6, len(line)):
        str = str + line[i] + ' '
    return str[0:-1]


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


def remove_file(hash):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[2:]
    os.remove(path)


def modify_file_message(hash, newMessage):
    path = homeDir + "object/" + hash[0:2] + "/" + hash[2:]
    commit, parents, author, committer, message = parse_commit(path)
    commDict[hash] = make_new_file(commit, parents, author, committer, newMessage)
    remove_file(hash)


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
logTemp = homeDir + "logs/temp"
# inHash = sys.argv[1]
# newMes = sys.argv[2]
newMes = " "
inHash = " "
# print(inHash)
#print(parse_commit(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))
#commit, parents, author, committer, message = (parse_commit(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))

#print(make_new_file(commit, parents, author, committer, message))

#print(make_new_file(decompress("/home/kal/jet/.git/objects/1b/24e58ce94a37cea752c0a83e64c238d0d6b772")))

log = open(logHEAD, 'r')
newlog = open(logTemp, 'w')
lineNum = 0

Ended = False
# /logs/head
for _line in log.readlines():

    line = parse_line(_line)

    if line[1] == inHash and not (line[1] in commDict):
        if newMes == line[-1][:-1]:
            print("nothing to modify")
            Ended = True
            break
        line[1] = modify_file_message(inHash, newMes)
        line[-1] = newMes + '\n'

    if line[0] in commDict:
        line[1] = modify_file_parent(line[1])
        line[0] = commDict[line[0]]

    newlog.write(parsed_to_string(line))
newlog.close()
log.close()

if not Ended:
    os.remove(logHEAD)
    os.rename(logTemp, logHEAD)

# change orig_head if needed
with open(homeDir + "ORIG_HEAD") as f:
    if f.read() in commDict:
        g = open(homeDir + "temp", 'w')
        g.write(commDict[f.read()])
        g.close()
        os.remove(homeDir + "ORIG_HEAD")
        os.rename(homeDir + "temp", homeDir + "ORIG_HEAD")

for ref in os.listdir(homeDir + "refs/heads/"):
   with open(homeDir + "refs/heads/" + ref) as f:
       if f.read() in commDict:
           g = open(homeDir + "refs/heads/" + "temp", 'w')
           g.write(commDict[f.read()])
           g.close()
           os.remove(homeDir + "refs/heads/" + ref)
           os.rename(homeDir + "refs/heads/" + "temp", homeDir + "refs/heads/" + ref)