import sys
import os.path
import StringIO
from Crypto.Cipher import AES

from constituency_tree.tree_readers import read_trees_oneperline_file,read_trees_file

KIV = "DIFF"*4
OUT_FILE_PATH = "PTB.ext"

def usage():
    return "Usage: run.py <path>"

def decrypt(file_path):
    obj = AES.new(KIV, AES.MODE_CBC, KIV)
    content = open(file_path,'rb').read()
    data = obj.decrypt(content)
    data = data[:-int(data[-1])]
    return data

# read parameters
if len(sys.argv) != 2:
    print usage()
    exit(0)

if os.path.isfile(sys.argv[1]) != True and os.path.isdir(sys.argv[1]) != True:
    print "ERROR: File/Directory does not exists."
    #print usage()
    exit(0)

INPUT_PATH = sys.argv[1]
SINGLEFILE = True if os.path.isfile(INPUT_PATH) else False

# read input trees to objects
if SINGLEFILE:
    inp_trees = list(read_trees_oneperline_file(open(INPUT_PATH)))
else:
    inp_trees = []
    for file_name in sorted(os.listdir(INPUT_PATH)):
        inp_trees += list(read_trees_file(open(os.path.join(INPUT_PATH,file_name))))


# read diff files
diff_meta_data = decrypt(os.path.join("data","diff_meta_data.en")).split("\n")
diff = list(read_trees_oneperline_file(StringIO.StringIO(decrypt(os.path.join("data","diff.en"))),extra_bracket=False))

# apply changes
for i,meta_data_row in enumerate(diff_meta_data):
    sent_id,b,e = meta_data_row.strip().split("\t")
    tree = inp_trees[int(sent_id)]
    ext_subtree = diff[i]
    node_index = int(b)
    for l in ext_subtree.collect_leaves(ignore_empties=False):
        l.id = node_index
        node_index+=1
    subtree = tree.get_subtree(int(b),int(e))
    head = subtree.parent
    if not head:
        inp_trees[int(sent_id)] = ext_subtree
        continue
    index = subtree.parent.childs.index(subtree)
    subtree.parent.childs = subtree.parent.childs[:index] + [ext_subtree] + subtree.parent.childs[index+1:]
    ext_subtree.parent = head

# write output
out = open(OUT_FILE_PATH,'w')
for i,tree in enumerate(inp_trees):
    out.write("("+tree.__str__()+")\n")
out.close()
