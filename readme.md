# Fruity - A simple chatbot
### Student name: Martin Veltman
### Student number: 709341
## Description
The chatbot is designed to answer questions related to fruits. It has knowledge about various fruits, their characteristics, and nutrients. It uses this knowledge to provide informative responses to user questions.

To build the chatbot, several NLP techniques were used:

1. Knowledge Graph: The chatbot's knowledge is represented as a graph structure called a knowledge graph. Each fruit is represented as a node in the graph, and relationships between fruits are represented as edges. For example, if the relationship between "apple" and "red color" is known, there will be an edge connecting the "apple" node to the "red color" node in the graph.

2. Fuzzy Matching: Fuzzy matching is used to find the best matching fruit based on user input. When the chatbot receives a question, it compares the user input with the list of known fruits using a fuzzy matching algorithm. This allows the chatbot to handle variations and minor misspellings in the user's query.

3. Synonym Matching: The chatbot uses synonym matching to handle different ways users might refer to the same concept. It leverages word similarity techniques to identify synonyms or related words. For example, if a user asks about the "taste" of a fruit, the chatbot recognizes synonyms like "flavor" or "flavour" to provide relevant responses.

4. Named Entity Recognition (NER): The chatbot uses a library called SpaCy for named entity recognition. NER helps in extracting useful information from the user's query, such as colors mentioned in the question. It identifies entities like colors and fruit names in the input and processes them accordingly.

5. WordNet: WordNet is a lexical database that provides information about word relationships. The chatbot uses WordNet to check if two words are synonyms or have a semantic similarity. This helps in identifying if a user's query is related to a particular fruit or concept.

6. FuzzyWuzzy: The FuzzyWuzzy library is used to calculate the similarity between two strings. It helps in finding the best match between user input and known fruits or relationships in the knowledge graph. Fuzzy matching allows the chatbot to handle queries even if there are minor differences or variations in the wording.

The chatbot categorizes user questions into different types, such as growth-related questions, taste-related questions, color-related questions, and ingredient-related questions. It then uses the appropriate techniques and the knowledge graph to generate informative responses based on the category of the question.

For example, if a user asks, "What nutrients does an apple contain?", the chatbot recognizes it as an ingredient-related question and retrieves the relevant information from the knowledge graph to provide an answer.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/MartinVeltman/fruitychat
```
2. Install the required packages:
```bash
pip install -r requirements.txt
```
3. Run the chatbot:
```bash
python chatbot.py
```