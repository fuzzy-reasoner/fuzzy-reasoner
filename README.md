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

This library is pure Python, and is not highly optimized code. If you need a high-performance solver this package is likely not a great fit. However, pull requests are welcome if there are any improvements you'd like to make!

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

knowledge = [
    # base facts
    Rule(parent_of(homer, bart)),
    Rule(father_of(abe, homer)),
    # theorems
    Rule(grandpa_of(X, Y), (father_of(X, Z), parent_of(Z, Y)))
]

reasoner = SLDReasoner(knowledge=knowledge)

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

### Working with proof results

The `reasoner.prove()` method will return a `Proof` object if a successful proof is found. This object contains a graph of all the unifications, subgoals, and similarity calculations that went into proving the goal.

```python
proof = reasoner.prove(goal)

proof.variable_bindings # => a map of all variables in the goal to their bound values
proof.similarity_score # => the min similarity of all `unify` operations in this proof
proof_node = proof.head # => the root node of the proof graph

# each proof node represents a unification
proof_node.goal # => the goal of the unification
proof_node.rule # => the rule unified against
proof_node.unification_similarity # => the similarity score of the unification
proof_node.children # => the child nodes representing subgoals of this unification
```

The `Proof` object also has a `pretty_print()` method which allows you to get a visual overview of the proof

```python
X = Variable("X")
Y = Variable("Y")
father_of = Predicate("father_of")
parent_of = Predicate("parent_of")
is_male = Predicate("is_male")
bart = Constant("bart")
homer = Constant("homer")

knowledge = [
    parent_of(homer, bart),
    is_male(homer),
    Rule(father_of(X, Y), (parent_of(X, Y), is_male(X))),
]

prover = SLDProver(knowledge=knowledge)
goal = father_of(homer, X)

proof = prover.prove(goal)

print(proof.pretty_print())
# | goal: father_of(CONST:homer,VAR:X)
# | rule: father_of(VAR:X,VAR:Y):-[parent_of(VAR:X,VAR:Y), is_male(VAR:X)]
# | unification similarity: 1.0
# | overall similarity: 1.0
# | goal subs: X->bart
# | rule subs: X->homer, Y->bart
# | subgoals: parent_of(VAR:X,VAR:Y), is_male(VAR:X)
#   ║
#   ╠═ | goal: parent_of(VAR:X,VAR:Y)
#   ║  | rule: parent_of(CONST:homer,CONST:bart):-[]
#   ║  | unification similarity: 1.0
#   ║  | overall similarity: 1.0
#   ║  | goal subs: X->homer, Y->bart
#   ║
#   ╠═ | goal: is_male(VAR:X)
#   ║  | rule: is_male(CONST:homer):-[]
#   ║  | unification similarity: 1.0
#   ║  | overall similarity: 1.0
#   ║  | goal subs: X->homer
```

### Finding all possible proofs

The `reasoner.prove()` method will return the proof with the highest similarity score among all possible proofs, if one exists. If you want to get a list of all the possible proofs in descending order of similarity score, you can call `reasoner.prove_all()` to return a list of all proofs.

### Custom matching functions and similarity thresholds

By default, the reasoner will use cosine similarity for unification. If you'd like to use a different similarity function, you can pass in a function to the reasoner to perform the similarity calculation however you wish.

```python

def fancy_similarity(item1, item2):
    norm = np.linalg.norm(item1.embedding) + np.linalg.norm(item2.embedding)
    return np.linalg.norm(item1.embedding - item2.embedding) / norm

reasoner = SLDReasoner(knowledge=knowledge, similarity_func=fancy_similarity)
```

By default, there is a minimum similarity threshold of `0.5` for a unification to success. You can customize this as well when creating a `SLDReasoner` instance

```python
reasoner = SLDReasoner(knowledge=knowledge, min_similarity_threshold=0.9)
```

### Working with Tensors (Pytorch, Tensorflow, etc...)

By default, the similarity calculation assumes that the embeddings supplied for constants and predicates are numpy arrays. If you want to use tensors instead, this will work as long as you provide a `similarity_func` which can work with the tensor types you're using and return a float.

For example, if you're using Pytorch, it might look like the following:

```python
import torch

def torch_cosine_similarity(item1, item2):
    similarity = torch.nn.functional.cosine_similarity(
        item1.embedding,
        item2.embedding,
        0
    )
    return similarity.item()

reasoner = SLDReasoner(knowledge=knowledge, similarity_func=torch_cosine_similarity)

# for pytorch you may want to wrap the proving in torch.no_grad()
with torch.no_grad():
    proof = reasoner.prove(goal)
```

### Max proof depth

By default, the SLDReasoner will abort proofs after a depth of 10. You can customize this behavior by passing `max_proof_depth` when creating the reasoner

```python
reasoner = SLDReasoner(knowledge=knowledge, max_proof_depth=10)
```

## Contributing

Contributions are welcome! Please leave an issue in the Github repo if you find any bugs, and open a pull request with and fixes or improvements that you'd like to contribute.

## Happy solving!
