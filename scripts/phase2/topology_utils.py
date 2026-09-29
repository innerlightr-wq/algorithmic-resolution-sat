"""
Vectorized Hamming-cluster-spectrum utilities (STAGE B / analysis only --
this module is fine to import in Stage B or post-hoc analysis scripts, never
in Stage A, since it operates on revealed point sets).

For binary vectors, squared Euclidean distance equals Hamming distance
exactly ((a_i-b_i)^2 = |a_i-b_i| for a_i,b_i in {0,1}), so pairwise Hamming
distances for N points can be computed as a single N x N matrix via one
Gram-matrix matrix-multiplication (BLAS-backed, fast even for N in the
thousands), rather than an O(N^2) Python double loop.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


def pairwise_hamming_matrix(points):
    """points: (N, n) array of 0/1 (int). Returns (N,N) integer Hamming distance matrix."""
    P = np.asarray(points, dtype=np.float64)
    G = P @ P.T
    norms = np.diag(G)
    D = norms[:, None] + norms[None, :] - 2 * G
    D = np.rint(D).astype(np.int64)
    np.fill_diagonal(D, 0)
    return D


def cluster_count_from_dist_matrix(D, r):
    """Number of connected components of the graph where edge iff D[i,j] <= r."""
    N = D.shape[0]
    if N == 0:
        return 0
    adj = (D <= r).astype(np.int8)
    np.fill_diagonal(adj, 0)
    sparse_adj = csr_matrix(adj)
    n_components, _ = connected_components(sparse_adj, directed=False)
    return n_components


def cluster_spectrum(points, r_values):
    """Returns dict r -> C(r) for the given point set, across all r in r_values."""
    D = pairwise_hamming_matrix(points)
    return {r: cluster_count_from_dist_matrix(D, r) for r in r_values}


def eps_hat_from_points(S, A):
    """max_{x in S} min_{y in A} d(x,y), via vectorized distance."""
    S = np.asarray(S, dtype=np.float64)
    A = np.asarray(A, dtype=np.float64)
    G = S @ A.T
    s_norm = (S ** 2).sum(axis=1)
    a_norm = (A ** 2).sum(axis=1)
    D = s_norm[:, None] + a_norm[None, :] - 2 * G
    D = np.rint(D).astype(np.int64)
    return int(D.min(axis=1).max())
