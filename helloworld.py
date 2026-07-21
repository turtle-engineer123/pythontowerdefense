import numpy as np

target = np.array([
    72,
    101,
    108,
    108,
    111,
    44,
    32,
    87,
    111,
    114,
    108,
    100,
    33
], dtype=float)

A = np.eye(len(target))
x = np.linalg.solve(A, target)

print("".join(chr(round(i)) for i in x))