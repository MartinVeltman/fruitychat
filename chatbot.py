from typing import Dict
from fuzzywuzzy import fuzz
import networkx as nx
from nltk.corpus import wordnet


class FruitChatbot:
    def __init__(self):
        self.knowledge_graph, self.fruit_grow_info = self.build_knowledge_graph()

    def build_knowledge_graph(self):
        graph = nx.Graph()

        fruits = ["apple", "banana", "orange", "grape"]
        graph.add_nodes_from(fruits)

        relationships = [
            ("apple", "is", "a fruit"),
            ("banana", "is", "a fruit"),
            ("orange", "is", "a fruit"),
            ("apple", "is", "red or green"),
            ("banana", "is", "yellow"),
            ("orange", "is", "orange"),
            ("apple", "has", "vitamin C"),
            ("apple", "has", "fiber"),
            ("apple", "has", "sugar"),
            ("banana", "has", "vitamin B6"),
            ("banana", "has", "potassium"),
            ("orange", "has", "vitamin C and fiber")
        ]

        fruit_grow_info: Dict[str, str] = {
            "apple": "on a tree",
            "banana": "on a banana plant",
            "orange": "on an orange tree",
            "grape": "on a grapevine"
        }

        # Add the relationships as edges to the graph
        graph.add_edges_from((r[0], r[2], {'relation': r[1]}) for r in relationships)

        # Return the built knowledge graph
        return graph, fruit_grow_info

    def fuzzy_match(self, query, entities):
        # Find the best match for the query among the list of entities
        best_match = None
        max_score = 0

        for entity in entities:
            score = fuzz.partial_ratio(query, entity)
            if score > max_score:
                max_score = score
                best_match = entity

        return best_match

    @staticmethod
    def are_words_similar(word1, word2):
        # Check if two words are similar by comparing their WordNet synsets
        synsets_word1 = wordnet.synsets(word1)
        synsets_word2 = wordnet.synsets(word2)

        for synset1 in synsets_word1:
            for synset2 in synsets_word2:
                similarity = synset1.path_similarity(synset2)
                if similarity is not None and similarity > 0.7:
                    return True

        return False

    def is_synonym(self, word1, word2):
        return self.are_words_similar(word1, word2)

    def is_synonym_of_list(self, word, word_list):
        # Check if a word is a synonym of any word in a given list
        return any(self.is_synonym(word, w) for w in word_list)

    def answer_question(self, question):
        greetings_list = [
            "hi", "hey", "hello", "good morning", "good afternoon", "good evening",
            "greetings", "salutations", "howdy", "hola", "bonjour", "ciao", "namaste",
            "yo", "what's up", "hi there", "good day", "how's it going", "sup"
        ]
        grow_list = ["grow", "grows", "growing", "grew", "growed", "growen"]
        location_list = ["where", "place", "location", "country", "countries", "how"]
        is_list = ["has", "contains", "have"]

        if any(greeting in question.lower() or self.is_synonym_of_list(question.lower(), greeting.split()) for greeting
               in greetings_list):
            return "Hello! How can I assist you with fruits today?"

        fruit = self.fuzzy_match(question, self.knowledge_graph.nodes)

        if fruit:  # If a fruit was found
            # Get the relationships of the fruit in the knowledge graph
            relationships = self.knowledge_graph.edges(fruit, data=True)

            if any(word in question for word in
                   grow_list or self.is_synonym_of_list(question.lower(), grow_list)) or any(
                    word in question for word in
                    location_list or self.is_synonym_of_list(question.lower(), location_list)):
                return f"a {fruit} grows {self.fruit_grow_info[fruit]}."

            if relationships:
                if any(word in question for word in is_list):
                    # Extract the nutrient from the question
                    keywords = [word for word in is_list if word in question]
                    nutrient = question.split(keywords[0])[1].strip()

                    # Find relationships matching the nutrient
                    nutrient_relationships = [r for r in relationships if
                                              fuzz.partial_ratio(r[2]['relation'], "has") > 80 and nutrient in r[1]]
                    if nutrient_relationships:
                        return f"Yes, {fruit} contains {nutrient}."
                    else:
                        return f"No, I'm not aware of {fruit} containing {nutrient}."
                else:
                    # Generate the response with the known relationships of the fruit
                    response = f"Here's what I know about {fruit}:"
                    for relationship in relationships:
                        response += f"\n- {fruit} {relationship[2]['relation']} {relationship[1]}"
                    return response
            else:
                return f"I'm sorry, I don't have information about {fruit}."
        else:
            return "I'm sorry, I couldn't understand your query or find a matching fruit."

    def chat(self):
        while True:
            user_input = input("User: ")

            if user_input.lower() == "exit":
                print("Chatbot: Goodbye!")
                break

            try:
                response = self.answer_question(user_input)
                print("Chatbot:", response)
            except Exception as e:
                print("Chatbot: An error occurred:", str(e))


chatbot = FruitChatbot()
chatbot.chat()
