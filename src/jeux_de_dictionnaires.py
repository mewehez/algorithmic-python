import re
import pydot
import matplotlib.pyplot as plt
from time import perf_counter


def extract_words(corpus):
    """Removes punctuation from corpus and split it using spaces. 
    Returns the list of the words from the split. All words are lowercased."""
    corpus = corpus.lower()
    corpus = re.sub('[\n\']', ' ', corpus)
    corpus = re.sub('[!?,.;:]', '', corpus)
    corpus = re.sub(' +', ' ', corpus).strip()
    return corpus.split(' ')


def build_trie(words):
    """Builds a trie structure from list of words"""
    trie = {}
    for word in words:
        node = trie
        for character in word[::-1]:
            # if trie containes character, node is set to character
            # else a new dic is created for the node
            if character not in node:
                node[character] = {}
            node = node[character]
        node['END'] = 0  # the parent of the first character
    return trie


def build_dot(trie, graph=None, predecessor=None, root_name=None, depth=0):
    # if no graph, create one
    if graph is None:
        graph = pydot.Dot('trie', graph_type='digraph')
    
    # if first node (no predecessor), add root node
    if predecessor is None:
        node_label = root_name or 'ROOT'
        node_name = '%s%d' % (node_label, id(trie))
        root_node = pydot.Node(node_name, label=node_label, shape='circle')
        graph.add_node(root_node)
        # recurcive call to build the rest of the graph
        build_dot(trie, graph, node_name, depth=depth)
    # if trie contains data (trie is not 0)
    elif isinstance(trie, dict):
        for key, val in trie.items():
            node_label = key
            node_name = '%s%d' % (node_label, id(val))
            node = pydot.Node(node_name, label=node_label, shape='circle')
            graph.add_node(node)
            # add edge
            edge = pydot.Edge(predecessor, node_name, color='black')
            graph.add_edge(edge)
            # recurcive call to build the rest of the graph
            build_dot(val, graph, node_name, depth=depth+1)
    return graph


def common_suffix(first_word, second_word):
    """Returns the greatest suffix shared between two words."""
    if len(first_word) == 0 or len(second_word) == 0:
        return ''
    if first_word == second_word:
        return first_word
    
    suffix = ''
    p = -1
    while (-p <= len(first_word)) and (-p <= len(second_word)):
        if first_word[p] == second_word[p]:
            suffix = first_word[p] + suffix
            p -= 1
        else:
            break
    return suffix



def largest_common_suffix(words):
    """Returns the couple of different words that share the longuest suffix."""
    best_pair = None
    largest_suffix = ''
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            if words[i] == words[j]:
                continue
            suffix = common_suffix(words[i], words[j])
            # update best result so far
            if len(suffix) > len(largest_suffix):
                largest_suffix = suffix
                best_pair = (words[i], words[j])
    return largest_suffix, best_pair


def last_char_map(words):
    """Groups words that have the same last character."""
    word_map = {}
    for word in words:
        char = word[-1]
        if word_map.get(char) is None:
            word_map[char] = [word]
        else:
            word_map[char].append(word)
    return word_map


def largest_common_suffix2(words):
    """Returns the couple of different words that share the longuest suffix.
    Words are groupped by the last character and suffix search is performed 
    on each group."""
    word_map = last_char_map(words)
    best_pair = None
    largest_suffix = ''

    for (_, values) in word_map.items():
        suffix, couple = largest_common_suffix(values)
        if len(suffix) > len(largest_suffix):
            largest_suffix, best_pair = suffix, couple
    return largest_suffix, best_pair


def largest_common_suffix3(words):
    """Returns the couple of different words that share the longuest suffix 
    using trie data structure."""
    global_trie = build_trie(words)

    def walk(trie):
        best = []
        for key, val in trie.items():
            # if END continue
            if isinstance(val, int):
                continue
            r = walk(val)
            if len(r) > 0 and len(r) + 1 > len(best):
                best = [key] + r
        if len(best) > 0:
            return best
        if len(trie) >= 2:
            return ['END']
        return []

    return walk(global_trie)


if __name__ == '__main__':
    poeme = """
    A noir, E blanc, I rouge, U vert, O bleu, voyelles,
    Je dirai quelque jour vos naissances latentes.
    A, noir corset velu des mouches éclatantes
    Qui bombillent autour des puanteurs cruelles,

    Golfe d'ombre; E, candeur des vapeurs et des tentes,
    Lance des glaciers fiers, rois blancs, frissons d'ombelles;
    I, pourpres, sang craché, rire des lèvres belles
    Dans la colère ou les ivresses pénitentes;

    U, cycles, vibrements divins des mers virides,
    Paix des pâtis semés d'animaux, paix des rides
    Que l'alchimie imprime aux grands fronts studieux;

    O, suprême clairon plein de strideurs étranges,
    Silences traversés des Mondes et des Anges:
    —O l'Oméga, rayon violet de Ses Yeux!
    """
    
    # print(extract_words(poeme))
    # print(common_suffix('abcd', 'ifgabcd'))
    words = extract_words(poeme)
    # print(largest_common_suffix(words))
    # print(largest_common_suffix2(words))

    # use tries
    # trie = build_trie(words)
    # graph = build_dot(trie['s']['e']['t'])
    # graph.write_png('output.png')
    
    # compare the all algorithms
    start = perf_counter()
    for i in range(100):
        largest_common_suffix(words)
    perf = perf_counter() - start

    start = perf_counter()
    for i in range(100):
        largest_common_suffix2(words)
    perf2 = perf_counter() - start

    start = perf_counter()
    for i in range(100):
        largest_common_suffix3(words)
    perf3 = perf_counter() - start

    print(f'first method: {perf:.4f} sec | second method: {perf2:.4f} | ratio: {perf/perf2:.4f}')
    print(f'second method: {perf2:.4f} sec | third method: {perf3:.4f} | ratio: {perf2/perf3:.4f}')
