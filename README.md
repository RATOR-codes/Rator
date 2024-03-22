# Detecting Fine-grained Semantic Code Clones via Tree Encoding based on Node Degrees of Freedom
Rator is a tree-based code clone detector with scalability and fine-grained analysis capabilities while effectively detecting semantic clones. We split the complex AST into different types of subtrees and encode them using node degrees of freedom. This can simplify the complex tree structure while preserving the structure details and achieve fine-grained clone detection.

Rator consists of five main phases: AST generation and splitting, Tree encoding, Feature Extraction, Classification, Fine-grained detection.

1. AST Generation and Splitting: this phase is to generate the AST by static analysis and split the AST into different types of subtrees.

2. Tree Encoding: this phase is to encode the features of different types of subtrees and construct the subtree DOF matrix. 

3. Feature Extraction: this phase is to construct a subtree similarity matrix by calculating the similarity between DOF matrices.

4. Clone Detection: this phase is to train the clone detector using the subtree similarity matrix and determine whether two code fragments are semantically similar.

5. Localization: this phase is to locate similar code blocks in the clone pairs.

# Project Structure
```
Rator 
|-- get_dofcode.py     	// implement the first two phases:  AST Generation and Splitting, Tree Encoding
|-- get_similarity.py   // implement the Feature Extraction phase and Fine-grained detection
|-- classification.py   // implement the Classification phase  
```
## Step1: Get degrees of freedom matrices
get_dofcode.py: The input is a folder containing the source code files and the output is the degrees of freedom matrices of source codes.
```
python get_dofcode.py
```
## Step2: Get similarity scores between two DOF matrice
```
python get_similarity.py
```
## Step3: Classification
classification.py: The file is used to train the clone detector and predict the clones using each of the six machine learning algorithms.
```
python classification.py
```

