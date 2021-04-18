# From https://github.com/arosh/BM25Transformer/blob/master/bm25.py
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings
from typing import Dict, Tuple

import numpy as np
import scipy.sparse as sp
import spacy
from loguru import logger
from sklearn import feature_extraction, metrics, pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import _document_frequency
from sklearn.metrics.pairwise import cosine_distances
from sklearn.utils.validation import check_is_fitted
from tqdm import tqdm


class BM25Transformer(BaseEstimator, TransformerMixin):
    """
  Parameters
  ----------
  use_idf : boolean, optional (default=True)
  k1 : float, optional (default=2.0)
  b : float, optional (default=0.75)
  References
  ----------
  Okapi BM25: a non-binary model - Introduction to Information Retrieval
  http://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html
  """

    def __init__(self, use_idf=True, k1=2.0, b=0.75):
        self.use_idf = use_idf
        self.k1 = k1
        self.b = b

    def fit(self, X):
        """
        Parameters
        ----------
        X : sparse matrix, [n_samples, n_features]
            document-term matrix
        """
        if not sp.issparse(X):
            X = sp.csc_matrix(X)
        if self.use_idf:
            n_samples, n_features = X.shape
            df = _document_frequency(X)
            idf = np.log((n_samples - df + 0.5) / (df + 0.5))
            self._idf_diag = sp.spdiags(idf, diags=0, m=n_features, n=n_features)
        return self

    def transform(self, X, copy=True):
        """
        Parameters
        ----------
        X : sparse matrix, [n_samples, n_features]
            document-term matrix
        copy : boolean, optional (default=True)
        """
        X = sp.csr_matrix(X, dtype=np.float64, copy=copy)

        n_samples, n_features = X.shape

        # Document length (number of terms) in each row
        # Shape is (n_samples, 1)
        dl = X.sum(axis=1)
        # Number of non-zero elements in each row
        # Shape is (n_samples, )
        sz = X.indptr[1:] - X.indptr[0:-1]
        # In each row, repeat `dl` for `sz` times
        # Shape is (sum(sz), )
        # Example
        # -------
        # dl = [4, 5, 6]
        # sz = [1, 2, 3]
        # rep = [4, 5, 5, 6, 6, 6]
        rep = np.repeat(np.asarray(dl), sz)
        # Average document length
        # Scalar value
        avgdl = np.average(dl)
        # Compute BM25 score only for non-zero elements
        data = (
            X.data
            * (self.k1 + 1)
            / (X.data + self.k1 * (1 - self.b + self.b * rep / avgdl))
        )
        X = sp.csr_matrix((data, X.indices, X.indptr), shape=X.shape)

        if self.use_idf:
            check_is_fitted(self, "_idf_diag", "idf vector is not fitted")

            expected_n_features = self._idf_diag.shape[0]
            if n_features != expected_n_features:
                raise ValueError(
                    "Input has n_features=%d while the model"
                    " has been trained with n_features=%d"
                    % (n_features, expected_n_features)
                )
            # *= doesn't work
            X = X * self._idf_diag

        return X


class MyBM25Transformer(BM25Transformer):
    """
  To be used in sklearn pipeline, transformer.fit()
  needs to be able to accept a "y" argument
  """

    def fit(self, x, y=None):
        super().fit(x)


def dummy(doc):
    return doc


class BM25Vectorizer(feature_extraction.text.TfidfVectorizer):
    """
  Drop-in, slightly better replacement for TfidfVectorizer
  Best results if text has already gone through stopword removal and lemmatization
  """

    def __init__(self):
        self.vec = pipeline.make_pipeline(
            feature_extraction.text.CountVectorizer(
                preprocessor=dummy, tokenizer=dummy, binary=True
            ),
            MyBM25Transformer(),
        )
        super().__init__()

    def fit(self, raw_documents, y=None):
        return self.vec.fit(raw_documents)

    def transform(self, raw_documents, copy=True):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            return self.vec.transform(raw_documents)


class BM25Fit:
    def run(self, text_input: Dict):
        logger.info("Fitting BM25 search engine")
        corpus = list(text_input.values())
        ids = list(text_input.keys())
        vectorizer = BM25Vectorizer().fit(corpus)
        transformed_corpus = vectorizer.transform(corpus)
        return (vectorizer, transformed_corpus, ids)


class BM25Search:
    def run(self, query_input: Dict, ix, limit=300):
        vectorizer, transformed_corpus, ids = ix
        query_output = {}
        for id, query in tqdm(query_input.items(), "Querying"):
            transformed_query = vectorizer.transform([query])
            TFIDF_dist = cosine_distances(transformed_query, transformed_corpus)
            res = {}

            sorted_val = np.argsort(TFIDF_dist)[0]

            for index in sorted_val[: limit if limit is not None else len(sorted_val)]:
                t_id = ids[index]
                score = 1 - TFIDF_dist[0][index]
                res[t_id] = score
            query_output[id] = res
        return query_output
