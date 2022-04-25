# Fuzzy Reasoner

[![ci](https://img.shields.io/github/workflow/status/chanind/fuzzy-reasoner/CI/main)](https://github.com/chanind/fuzzy-reasoner)
[![Codecov](https://img.shields.io/codecov/c/github/chanind/fuzzy-reasoner/main)](https://codecov.io/gh/chanind/fuzzy-reasoner)
[![PyPI](https://img.shields.io/pypi/v/fuzzy-reasoner?color=blue)](https://pypi.org/project/fuzzy-reasoner/)


A simple symbolic reasoner which allows fuzzy unification based on embedding comparisons.

This projects takes ideas and inspiration from the following papers:

- [End-to-End Differentiable Proving](https://arxiv.org/abs/1705.11040) by Rocktäschel et al.
- [Braid - Weaving Symbolic and Neural Knowledge into Coherent Logical Explanations](https://arxiv.org/abs/2011.13354) by Kalyanpur et al.

Thank you so much to the authors of these papers!

## Installation

```
pip install fuzzy-reasoner
```

## Limitations and issues

This library is still very much in beta and may change its public API at any time before reaching version 1.0, so it's recommended to pin the exact version before then.

This library is currently limited to only use a rule once in a proof as a way to avoid cycles in the proof graph. This restriction should be fixed soon though, as this restriction does limit the usefulness of the library.

This library is pure Python, and is not highly optimized code. If you need a high-performance mature solver this package is likely not a great fit. However, pull requests are welcome if you'd like to contribute and help make this library higher-performance!

## Usage

fuzzy-reasoner can be used either as a standard symbolic reasoner, or it can be used with fuzzy unification.

The setup works similar to prolog, except with python objects representing each component. A simple example of how this works is shown below:

```python
import numpy as np
from fuzzy_reasoner import SLDProver, Atom, Rule, Constant, Predicate, Variable

X = Variable("X")
Y = Variable("Y")
Z = Variable("Z")
# predicates and constants can be given an embedding array for fuzzy unification
grandpa_of = Predicate("grandpa_of", np.array([1.0, 1.0, 0.0, 0.3, ...]))
grandfather_of = Predicate("grandfather_of", np.array([1.01, 0.95, 0.05, 0.33, ...]))
parent_of = Predicate("parent_of", np.array([ ... ]))
father_of = Predicate("father_of", np.array([ ... ]))
bart = Constant("bart", np.array([ ... ]))
homer = Constant("homer", np.array([ ... ]))
abe = Constant("abe", np.array([ ... ]))

rules = [
    # base facts
    Rule(parent_of(homer, bart)),
    Rule(father_of(abe, homer)),
    # theorems
    Rule(grandpa_of(X, Y), (father_of(X, Z), parent_of(Z, Y)))
]

reasoner = SLDReasoner(rules=rules)

# query the reasoner to find who is bart's grandfather
proof = reasoner.prove(grandfather_of(X, bart))

# even though `grandpa_of` and `grandfather_of` are not identical symbols,
# their embedding is close enough that the reasoner can still find the answer
print(proof.variable_bindings[X]) # abe

# the reasoner will return `None` if the proof could not be solved
failed_proof = reasoner.prove(grandfather_of(bart, homer))
print(failed_proof) # None

```

If you don't want to use fuzzy unification, you can just not pass in an embedding array when creating a `Predicate` or `Constant`, and the reasoner will just do a plain string equality comparison for unification.

```python
# constants and predicates can be defined without an embedding array for strict (non-fuzzy) unification
grandpa_of = Predicate("grandpa_of")
bart = Constant("bart")
```

### Custom matching functions and similarity thresholds

By default, the reasoner will use cosine similarity for unification. If you'd like to use a different similarity function, you can pass in a function to the reasoner to perform the similarity calculation however you wish.

```python

def fancy_similarity(item1, item2):
    norm = np.linalg.norm(item1.vector) + np.linalg.norm(item2.vector)
    return np.linalg.norm(item1.vector - item2.vector) / norm

reasoner = SLDReasoner(rules=rules, similarity_func=fancy_similarity)
```

By default, there is a minimum similarity threshold of `0.5` for a unification to success. You can customize this as well when creating a `SLDReasoner` instance

```python
reasoner = SLDReasoner(rules=rules, min_similarity_threshold=0.9)
```

### Max proof depth

By default, the SLDReasoner will abort proofs after a depth of 10. You can customize this behavior by passing `max_proof_depth` when creating the reasoner

```python
reasoner = SLDReasoner(rules=rules, max_proof_depth=10)
```

## Contributing

Contributions are welcome! Please leave an issue in the Github repo if you find any bugs, and open a pull request with and fixes or improvements that you'd like to contribute.

## Happy solving!
