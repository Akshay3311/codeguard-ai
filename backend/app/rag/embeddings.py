import math
import re
from typing import List, Dict, Set
from collections import Counter


class SimpleVectorIndex:
    """
    Lightweight, dependency-free TF-IDF & Cosine Similarity Vector Index.
    Guarantees fast, reproducible knowledge search without external API dependencies.
    """

    def __init__(self):
        self.doc_ids: List[str] = []
        self.documents: List[Dict] = []
        self.term_freqs: List[Counter] = []
        self.doc_lengths: List[float] = []
        self.idf: Dict[str, float] = {}
        self.vocabulary: Set[str] = set()

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase and extract alphanumeric terms (including python keywords)
        clean = re.sub(r"[^\w\s-]", " ", text.lower())
        tokens = [t for t in clean.split() if len(t) > 2]
        return tokens

    def fit_and_index(self, docs: List[Dict]) -> None:
        self.documents = docs
        self.doc_ids = [d["doc_id"] for d in docs]
        self.term_freqs = []
        self.doc_lengths = []
        self.vocabulary = set()

        doc_count = len(docs)
        if doc_count == 0:
            return

        df: Counter = Counter()

        for doc in docs:
            full_text = f"{doc['title']} {doc['section']} {doc['content']}"
            tokens = self._tokenize(full_text)
            tf = Counter(tokens)
            self.term_freqs.append(tf)
            self.vocabulary.update(tf.keys())
            for term in tf.keys():
                df[term] += 1

        # Calculate IDF with smoothing
        self.idf = {}
        for term, freq in df.items():
            self.idf[term] = math.log((doc_count + 1) / (freq + 1)) + 1.0

        # Compute document vector L2 norms for cosine normalization
        for tf in self.term_freqs:
            sq_sum = 0.0
            for term, count in tf.items():
                tfidf = (count / sum(tf.values())) * self.idf.get(term, 1.0)
                sq_sum += tfidf * tfidf
            self.doc_lengths.append(math.sqrt(sq_sum) if sq_sum > 0 else 1.0)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
        if not self.documents:
            return []

        q_tokens = self._tokenize(query_text)
        if not q_tokens:
            return self.documents[:top_k]

        q_tf = Counter(q_tokens)
        q_norm = math.sqrt(sum((c * self.idf.get(t, 1.0)) ** 2 for t, c in q_tf.items())) or 1.0

        scores = []
        for idx, (doc, tf, doc_len) in enumerate(zip(self.documents, self.term_freqs, self.doc_lengths)):
            dot_product = 0.0
            for term, q_count in q_tf.items():
                if term in tf:
                    doc_tfidf = (tf[term] / sum(tf.values())) * self.idf.get(term, 1.0)
                    q_tfidf = q_count * self.idf.get(term, 1.0)
                    dot_product += doc_tfidf * q_tfidf

            cosine_sim = dot_product / (doc_len * q_norm) if (doc_len * q_norm) > 0 else 0.0
            scores.append((cosine_sim, doc))

        # Sort descending by similarity score
        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for sim, doc in scores[:top_k]:
            doc_copy = dict(doc)
            doc_copy["similarity_score"] = round(float(sim), 4)
            results.append(doc_copy)

        return results
