from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

def extract_semantic_triplets(text):
    doc = nlp(text)
    triplets = []
    for sent in doc.sents:
        for token in sent:
            subject = ""
            predicate = ""
            objects = []

            # Find subject
            if "subj" in token.dep_:
                subject = token.text
                # Find predicate (verb related to the subject)
                for child in token.head.children:
                    if child.pos_ == "VERB":
                        predicate = child.lemma_
                        # Find objects related to the predicate
                        for grandchild in child.children:
                            if "obj" in grandchild.dep_ or "pobj" in grandchild.dep_:
                                objects.append(grandchild.text)
                        if subject and predicate and objects:
                            for obj in objects:
                                triplets.append((subject, predicate, obj))

            # More robust object finding for verbs
            elif token.pos_ == "VERB":
                predicate = token.lemma_
                subject_found = False
                for child in token.children:
                    if "subj" in child.dep_:
                        subject = child.text
                        subject_found = True
                    elif "obj" in child.dep_ or "pobj" in child.dep_:
                        objects.append(child.text)
                if subject_found and predicate and objects:
                    for obj in objects:
                        triplets.append((subject, predicate, obj))

            # Handling adjectival modifiers as potential relationships
            elif token.pos_ == "ADJ":
                amod_target = token.head
                if amod_target.pos_ in ["NOUN", "PROPN"]:
                    triplets.append((amod_target.text, "is", token.text))

            # Handling prepositional phrases for relationships
            elif token.dep_ == "prep":
                head = token.head
                for child in token.children:
                    if child.pos_ in ["NOUN", "PROPN"]:
                        triplets.append((head.text, token.lemma_, child.text))

    return list(set(triplets))

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    data = request.get_json()
    text = data['text']
    triplets = extract_semantic_triplets(text)
    G = nx.DiGraph()
    for head, relation, tail in triplets:
        G.add_edge(head, tail, label=relation)

    # More aggressive layout adjustments
    pos = nx.spring_layout(G, k=1.2, iterations=200) # Increased k and iterations further

    # Increase figure size
    plt.figure(figsize=(18, 14)) # Increased figure dimensions again

    # Slightly reduce node size
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=2500, font_weight='bold', arrows=True, connectionstyle='arc3,rad=0.1')
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    plt.axis('off')
    plt.tight_layout(pad=3) # Increased padding further

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close()

    return jsonify({'image': image_base64})

@app.route('/test-connection', methods=['GET'])
def test_connection():
    return jsonify({'message': 'Backend is alive from India (as of May 7, 2025)!'})

if __name__ == '__main__':
    app.run(debug=True)