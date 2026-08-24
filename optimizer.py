import bpy

def shorten_chain(chain, segments):
    """
    chain: list of bone names, root first, tip last.
    segments: how many segments the user wants (NOT bone count —
              segments = gaps between kept bones, so result has
              segments + 1 bones total, always keeping root and tip).
    """
    N = len(chain)
    kept_indices = [round(i * (N - 1) / segments) for i in range(segments + 1)]
    return [chain[i] for i in kept_indices]
