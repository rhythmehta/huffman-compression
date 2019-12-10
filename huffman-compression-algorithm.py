#!/usr/bin/env python
# coding: utf-8

# In[1]:


###utility function for downloading a text file from a URL. 
from urllib.request import urlopen
import shutil
import gzip
import os


# Downloading the file:
def download_file(url, filename):
    if not os.path.exists(filename):
        response = urlopen(url + filename)
        shutil.copyfileobj(
            gzip.GzipFile(fileobj=response), open(filename+'.txt', 'wb'))

url = "http://www.gutenberg.org/ebooks/"
filename = "100.txt.utf-8"

download_file(url, filename)


# In[2]:


from bitarray import bitarray #https://pypi.org/project/bitarray/

class Node(object):
    """A node in a binary tree that represents a prefix code."""
    def __init__(self, freq, symb, parent = None, lchild = None, rchild = None):
        """
        - freq: float, frequency of the character
        - symb: string, a character in the file 
        - parent: a node, parent of the current node in the tree
        - lchild, rchild: left child node and right child node of the current node 
        in the tree.
        """
        self.freq = freq
        self.symb = symb
        self.parent = parent
        self.lchild = lchild
        self.rchild = rchild
    
    def __lt__(self, other):
        """
        nodeA < nodeB returns True if nodeA.freq < nodeB.freq. This enables
        us to use the module heapq on nodes. In other words, with this function,
        we can now push/insert a node into a heap as well as extract/pop the 
        minimum node from a heap. We studied the module heapq before. You can brush
        up your memory by visiting this link: 
        https://docs.python.org/3.0/library/heapq.html
        
        """
        return self.freq < other.freq
    
def get_bitarray(node):
    """
    Given a node in the tree, determines the corresponding codeword for character
    node.symb, using the rule in Cormen et al.: the binary codeword for a character 
    is the simple path from the root to that character, where 0 means “go to the 
    left child” and 1 means “go to the right child.
    
    Inputs:
    - node: a node, whose codeword represented by the tree is of interest
    
    Outputs:
    - a: a bit array that represents the codeword. For example, if the codeword is 
    01001, then a is bitarray('01001')
    
    """
    string = "" #empty string
    while  node.parent != None:  #running over parents unless root
        if node == node.parent.rchild:
            string += "1"
        else:
            string += "0"
        node = node.parent
    #string.reverse()
    string = string[::-1]
    return bitarray(string)


# In[3]:


###building Huffman code, making use of get_bitarray and the module heapq

import heapq

def encode(symb2freq):
    """
    Huffman encode the given dict mapping symbols to weights. 
    
    Inputs:
    - symb2freq: a dictionary that maps a symbol/character to
    the probability frequency in the text file. For example,
    {'a': .3, 'b':.6, 'c': .1}. This example symb2freq means 
    that symbol 'a' appears with frequency 30%, symbol 'b' 60%, 
    and symbol 'c' 10%.
    
    Outputs:
    - out: a dictionary that maps a symbol/charcater to a bitarray
    that represents the codeword for that symbol. For example,
    out = {'a': bitarray('01'), 'b': bitarray('11'), 'c': bitarray('101')}.
    """
    ln = len(symb2freq) #length of dictionary
    heap = [] #array for heap
    
    for key, value in symb2freq.items(): #add node
        heap.append(Node(freq = value, symb = key))
   
    heapq.heapify(heap) #heapifiy
    Q = heap.copy() #duplicate array
    
    for i in range(ln-1):
        x = heapq.heappop(Q) #get 2 min values
        y = heapq.heappop(Q)
        z = Node(x.freq + y.freq, x.symb+y.symb, lchild = x, rchild = y) #parent node
        heapq.heappush(Q,z) #push node to heap
        x.parent = z #update parents
        y.parent = z
    
    bitsmap = {}
    for n in heap:
        bitsmap[n.symb] = get_bitarray(n)
    return bitsmap


# In[4]:


from collections import defaultdict 
import pickle

# build a frequency table:
def build_freq(filename):
    freq = defaultdict(int)
    with open(filename, 'rb') as f:
        for line in f:
            for char in line:
                freq[char] += 1
    total = float(sum(freq.values()))
    return {char: count / total for (char, count) in freq.items()}

# Now compress the file:
def compress(filename, encoding, compressed_name=None):
    if compressed_name is None:
        compressed_name = filename + ".huff"
    output = bitarray()
    with open(filename, 'rb') as f:
        for line in f:
            for char in line:
                output.extend(encoding[char])
    N = len(output)
    with open(compressed_name, 'wb') as f:
        pickle.dump(N, f)
        pickle.dump(encoding, f)
        output.tofile(f)


# Now decompress the file:
def decompress(filename, decompressed_name=None):
    if decompressed_name is None:
        decompressed_name = filename + ".dehuff.txt"
    with open(filename, 'rb') as f:
        N = pickle.load(f)
        encoding = pickle.load(f)
        bits = bitarray()
        bits.fromfile(f)
        bits = bits[:N]

    # Totally cheating here and using a builtin method:
    output = bits.decode(encoding)
    with open(decompressed_name, 'wb') as f:
        f.write(bytes(output))


# In[5]:


###application

filename='100.txt.utf-8.txt'
frequency = build_freq(filename)
encoding = encode(frequency)
compress(filename, encoding, compressed_name="100.txt.utf-8.txt.huff")
decompress("100.txt.utf-8.txt.huff", decompressed_name="100.txt.utf-8.txt.huff.dehuff.txt")


# In[ ]:


# Original/Decompressed: 5.6MB
# Compressed: 3.3MB

