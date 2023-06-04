from typing import Dict
from fuzzywuzzy import fuzz
import networkx as nx
from nltk.corpus import wordnet
import spacy


class FruitChatbot:
    def __init__(self):
        self.knowledge_graph, self.fruit_grow_info = self.build_knowledge_graph()
        self.nlp = spacy.load("en_core_web_sm")
        self.greetings_list = [
            "hi", "hey", "hello", "good morning", "good afternoon", "good evening",
            "greetings", "salutations", "howdy", "hola", "bonjour", "ciao", "namaste",
            "yo", "what's up", "hi there", "good day", "how's it going", "sup"
        ]
        self.grow_list = ["grow", "grows", "growing", "grew", "growed", "growen"]
        self.location_list = ["where", "place", "location", "country", "countries"]
        self.is_list = ["has", "contains", "have"]
        self.tastes_list = ["taste", "tastes", "tasting", "tasted", "tasteing", "tasteen", "flavor", "flavors",
                            "flavour", "flavours", "flavoring", "flavouring", "flavorings", "flavourings", "like",
                            "savour", "bite", "savor", "sapidity", "savouriness", "tang", "tanginess", "tangy", ]
        self.color_list = ["color", "colors", "colour", "colours", "coloring", "colouring", "colorings", "colourings",
                           "look", "looks", "looking", "looked", "looken",
                           "appearance", "appearances", "appearing", "appeared", "appearen", "appearence",
                           "appearences", "appearencing", "appearenced", "appearencen", ]

        self.color_relationships = self.get_color_relationships()

    def extract_colors(self, question):
        doc = self.nlp(question)
        colors = []

        for token in doc:
            if token.text.lower() in ['red', 'green', 'yellow', 'orange', 'blue', 'purple', 'pink']:
                colors.append(token.text.lower())
        print("Colors", colors)
        return colors

    def get_color_relationships(self):
        color_relationships = {}
        for fruit in self.knowledge_graph.nodes:
            colors = [r[1].strip() for r in self.knowledge_graph.edges(fruit, data=True) if
                      r[2]['relation'] == 'is color']
            color_relationships[fruit] = colors
        return color_relationships

    def answer_color_question(self, fruit, colors):
       #als colors nul is en er geen kleur opgeven is antwoord met bijv apple is rood
        if len(colors) == 0:
            return f"{fruit} can have the color {self.color_relationships[fruit][0]}"

        #als colors niet nul is en er is een kleur opgegeven is kijk of de kleur in de lijst van kleuren van de fruit zit of een synoniem is zo ja antwoord met bijv apple is rood
       #zo nee antwoord met bijv apple is niet rood
        for color in colors:
            if color in self.color_relationships[fruit] or self.is_synonym_of_list(color, self.color_relationships[fruit]):
                return f"{fruit} can have the color {color}"
        return f"{fruit} is not {colors[0]}"


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

    def is_color_question(self, question):
        print("Is color question", any(word in question for word in self.color_list))
        return any(word in question for word in self.color_list)

    def is_grow_question(self, question):
        return any(word in question for word in self.grow_list) or any(
            word in question for word in self.location_list)

    def is_ingredient_question(self, question):
        return any(word in question for word in self.is_list)

    def is_taste_question(self, question):
        print("Is taste question", any(word in question for word in self.tastes_list))
        return any(word in question for word in self.tastes_list)

    def answer_grow_question(self, fruit):
        return f"A {fruit} grows {self.fruit_grow_info[fruit]}."

    def answer_ingredient_question(self, fruit, nutrient):
        relationships = self.knowledge_graph.edges(fruit, data=True)
        # Find relationships matching the nutrient
        nutrient_relationships = [r for r in relationships if
                                  fuzz.partial_ratio(r[2]['relation'], "has") > 80 and nutrient in r[1]]
        if nutrient_relationships:
            return f"Yes, {fruit} contains {nutrient}."
        else:
            return f"No, I'm not aware of {fruit} containing {nutrient}."

    def answer_taste_question(self, fruit, taste):
        relationships = self.knowledge_graph.edges(fruit, data=True)
        # Find relationships matching the taste
        taste_relationships = [relation for relation in relationships if
                               fuzz.partial_ratio(relation[2]['relation'], "tastes") > 80 and taste in relation[1]]
        print(taste_relationships)
        if taste_relationships:
            taste = [r[1] for r in taste_relationships]
            taste = str(taste)[2:-2]
            return f"Yes, {fruit} tastes {taste}."
        else:
            return f"No, I'm not aware of the taste of {fruit} being {taste}."

    def answer_question(self, question):
        if any(greeting in question.lower() or self.is_synonym_of_list(question.lower(), greeting.split()) for greeting
               in self.greetings_list):
            return "Hello! How can I assist you with fruits today?"

        fruit = self.get_fruit_type(question)
        print("detected fruit ", fruit)
        colors = self.extract_colors(question)
        print("detected colors ", colors)

        if fruit:
            if self.is_grow_question(question):
                return self.answer_grow_question(fruit)

            if self.is_ingredient_question(question):
                # Extract the nutrient from the question
                keywords = [word for word in self.is_list if word in question]
                nutrient = question.split(keywords[0])[1].strip()
                return self.answer_ingredient_question(fruit, nutrient)

            if self.is_taste_question(question):
                # Extract the taste from the question
                keywords = [word for word in self.tastes_list if word in question]
                taste = question.split(keywords[0])[1].strip()
                return self.answer_taste_question(fruit, taste)

            if self.is_color_question(question):
                print("Is color question")
                print(colors)
                return self.answer_color_question(fruit, colors)

            if any(word in question.lower() for word in ["what", "define"]):
                return f"{fruit} is a type of fruit."

            relationships = self.knowledge_graph.edges(fruit, data=True)
            # Generate the response with the known relationships of the fruit
            if relationships:
                response = f"Here's what I know about {fruit}:"
                for relationship in relationships:
                    response += f"\n- {fruit} {relationship[2]['relation']} {relationship[1]}"
                return response
            else:
                print(fruit)
                return f"I'm sorry, I don't have information about {fruit}."

        # If no fruit was found in the question
        return "I'm sorry, I'm not sure which fruit you're referring to."

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
