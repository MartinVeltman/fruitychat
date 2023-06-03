from typing import Dict
from fuzzywuzzy import fuzz
import networkx as nx
from nltk.corpus import wordnet


class FruitChatbot:
    def __init__(self):
        self.knowledge_graph, self.fruit_grow_info = self.build_knowledge_graph()
        self.greetings_list = [
            "hi", "hey", "hello", "good morning", "good afternoon", "good evening",
            "greetings", "salutations", "howdy", "hola", "bonjour", "ciao", "namaste",
            "yo", "what's up", "hi there", "good day", "how's it going", "sup"
        ]
        self.grow_list = ["grow", "grows", "growing", "grew", "growed", "growen"]
        self.location_list = ["where", "place", "location", "country", "countries", "how"]
        self.is_list = ["has", "contains", "have"]
        self.tastes_list = ["taste", "tastes", "tasting", "tasted", "tasteing", "tasteen", "flavor", "flavors",
                            "flavour", "flavours", "flavoring", "flavouring", "flavorings", "flavourings", "like",
                            "savour", "bite", "savor", "sapidity", "savouriness", "tang", "tanginess", "tangy", ]
        self.color_list = ["color", "colors", "colour", "colours", "coloring", "colouring", "colorings", "colourings",
                           "look", "looks", "looking", "looked", "looken",
                           "appearance", "appearances", "appearing", "appeared", "appearen", "appearence",
                           "appearences", "appearencing", "appearenced", "appearencen", ]

    def build_knowledge_graph(self):
        graph = nx.Graph()

        fruits = [
            "apple", "banana", "orange", "grape", "strawberry", "mango", "pineapple", "watermelon",
            "pear", "kiwi", "blueberry", "raspberry", "peach", "cherry", "lemon", "lime", "plum",
            "pomegranate", "blackberry", "avocado", "apricot", "coconut", "fig", "grapefruit",
            "guava", "melon", "papaya", "passion fruit"
        ]
        graph.add_nodes_from(fruits)

        relationships = []
        with open("fruit_relationships.txt", "r") as file:
            for line in file:
                relationship = line.strip().split(":")
                relationships.append(relationship)

        fruit_grow_info: Dict[str, str] = {}
        with open("fruit_grow_info.txt", "r") as file:
            for line in file:
                fruit, growth_info = line.strip().split(":")
                fruit_grow_info[fruit] = growth_info

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
        if any(greeting in question.lower() or self.is_synonym_of_list(question.lower(), greeting.split()) for greeting
               in self.greetings_list):
            return "Hello! How can I assist you with fruits today?"

        fruit = self.get_fruit_type(question)

        if fruit:  # If a fruit was found
            # Get the relationships of the fruit in the knowledge graph
            relationships = self.knowledge_graph.edges(fruit, data=True)

            if any(word in question for word in
                   self.grow_list or self.is_synonym_of_list(question.lower(), self.grow_list)) or any(
                word in question for word in
                self.location_list or self.is_synonym_of_list(question.lower(), self.location_list)):
                return f"a {fruit} grows {self.fruit_grow_info[fruit]}."

            if relationships:
                if any(word in question for word in
                       self.is_list or self.is_synonym_of_list(question.lower(), self.is_list)):
                    # Extract the nutrient from the question
                    keywords = [word for word in self.is_list if word in question]
                    nutrient = question.split(keywords[0])[1].strip()

                    # Find relationships matching the nutrient
                    nutrient_relationships = [r for r in relationships if
                                              fuzz.partial_ratio(r[2], "has") > 80 and nutrient in r[1]]
                    if nutrient_relationships:
                        return f"Yes, {fruit} contains {nutrient}."
                    else:
                        return f"No, I'm not aware of {fruit} containing {nutrient}."
                elif any(word in question for word in
                         self.tastes_list or self.is_synonym_of_list(question.lower(), self.tastes_list)):
                    # Extract the taste from the question
                    keywords = [word for word in self.tastes_list if word in question]
                    taste = question.split(keywords[0])[1].strip()

                    # Find relationships matching the taste
                    taste_relationships = [r for r in relationships if
                                           fuzz.partial_ratio(r[2], "tastes") > 80 and taste in r[1]]
                    if taste_relationships:
                        fruits_with_taste = [r[0] for r in taste_relationships]
                        return f"Yes, {fruit} tastes {taste}. Other fruits with similar taste are: {', '.join(fruits_with_taste)}."
                    else:
                        return f"No, I'm not aware of the taste of {fruit} being {taste}."
                elif any(word in question for word in
                         self.color_list or self.is_synonym_of_list(question.lower(), self.color_list)):
                    # Extract the color from the question
                    keywords = [word for word in self.color_list if word in question]
                    color = question.split(keywords[0])[1].strip()

                    # Find relationships matching the color
                    color_relationships = [r for r in relationships if
                                           fuzz.partial_ratio(r[2], "is") > 80 and color in r[1]]
                    if color_relationships:
                        fruits_with_color = [r[0] for r in color_relationships]
                        return f"Yes, {fruit} is {color}. Other fruits with the same color are: {', '.join(fruits_with_color)}."
                    else:
                        return f"No, I'm not aware of {fruit} being {color} in color."
                else:
                    # Generate the response with the known relationships of the fruit
                    response = f"Here's what I know about {fruit}:"
                    for relationship in relationships:
                        response += f"\n- {fruit} {relationship[1]} {relationship[2]}"
                    return response
            else:
                return f"I'm sorry, I don't have information about {fruit}."

    def get_fruit_type(self, question):
        return self.fuzzy_match(question, self.knowledge_graph.nodes)

    def chat(self):
        while True:
            user_input = input("User: ")

            if user_input.lower() == "exit" or user_input.lower() == "quit":
                print("Chatbot: Goodbye!")
                break

            try:
                response = self.answer_question(user_input)
                print("Chatbot:", response)
            except Exception as e:
                print("Chatbot: An error occurred:", str(e))


chatbot = FruitChatbot()
chatbot.chat()
