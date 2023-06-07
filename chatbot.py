import re
from typing import Dict
from fuzzywuzzy import fuzz
import networkx as nx
from nltk.corpus import wordnet
import spacy
import wikipediaapi
import requests


class FruitChatbot:
    def __init__(self):
        self.knowledge_graph, self.fruit_grow_info = self.build_knowledge_graph()
        self.nlp = spacy.load("en_core_web_lg")

        self.greetings_list = [
            "hi", "hey", "hello", "good morning", "good afternoon", "good evening",
            "greetings", "salutations", "howdy", "hola", "bonjour", "ciao", "namaste",
            "yo", "what's up", "hi there", "good day", "how's it going", "sup"
        ]

        self.grow_list = ["grow", "grows", "growing", "grew", "growed", "growen"]

        self.location_list = ["where", "place", "location", "country", "countries"]

        self.is_list = ["has", "contains", "have", "nutrients", "nutrient", "vitamins", "vitamin", "minerals",
                        "ingredient", "ingredients", "contain"]

        self.flavor_list = ["sweet", "sour", "bitter", "salty", "savory", "sapidity", "savouriness", "tang",
                            "tanginess", "tangy", "savour"]

        self.tastes_list = ["taste", "tastes", "tasting", "tasted", "tasteing", "tasteen", "flavor", "flavors",
                            "flavour", "flavours", "flavoring", "flavouring", "flavorings", "flavourings",
                            "like"] + self.flavor_list

        self.color_list = ["color", "colors", "colour", "colours", "coloring", "colouring", "colorings", "colourings",
                           "look", "looks", "looking", "looked", "looken",
                           "appearance", "appearances", "appearing", "appeared", "appearen", "appearence",
                           "appearences", "appearencing", "appearenced", "appearencen", "yellow", "red", "green",
                           "orange", "blue", "purple", "pink"]
        self.nutrient_list = ["nutrient", "nutrients", "vitamins", "mineral", "minerals", "ingredient", "calcium",
                              "potassium", "iron", "magnesium", "phosphorus", "sodium", "zinc", "copper", "manganese",
                              "selenium", "vitamin a", "vitamin c", "vitamin b1", "vitamin b2", "vitamin b3",
                              "vitamin b5", "vitamin b6",
                              "vitamin b9", "vitamin b12", "vitamin", "vitamin d", "vitamin e", "vitamin k",
                              "vitamin b",
                              "vitamin b complex", "vitamin b17", "vitamin b3", "vitamin b5", "vitamin b6",
                              "vitamin b7", "vitamin"
                              ]

        self.color_relationships = self.get_color_relationships()

        self.add_fruit_to_knowledge_graph("Pitaya")

    def build_knowledge_graph(self):
        graph = nx.Graph()

        fruits = [
            "apple", "banana", "orange", "grape", "strawberry", "mango", "pineapple", "watermelon",
            "pear", "kiwi", "blueberry", "raspberry", "peach", "cherry", "lemon", "lime", "plum",
            "pomegranate", "blackberry", "avocado", "apricot", "coconut", "fig", "grapefruit",
            "guava", "melon", "papaya", "passion fruit", "pitaya"
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

        graph.add_edges_from((r[0], r[2], {'relation': r[1]}) for r in relationships)

        return graph, fruit_grow_info

    def fetch_wikipedia_content(self, page_title):
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(page_title)

        return page.text

    def add_fruit_to_knowledge_graph(self, page_title):
        content = self.fetch_wikipedia_content(page_title)

        color_section = "color"
        if color_section in content:
            color_content = content.split(color_section)[1].split("==")[0]
            color_info = [color.strip() for color in color_content.split("\n") if color.strip()]
            if color_info:
                self.knowledge_graph.add_node(page_title.lower())
                for color_sentence in color_info:
                    color_info = color_sentence.split(" ")
                    for color in color_info:
                        if color.lower() in self.color_list:
                            self.knowledge_graph.add_edge(page_title.lower(), color, relation="is color")
                            continue

        nutrient_section = "nutrient content"
        if nutrient_section in content:
            nutrient_content = content.split(nutrient_section)[1].split("nutrition facts")[0]
            nutrient_info = [nutrient.strip() for nutrient in nutrient_content.split(",") if nutrient.strip()]
            if nutrient_info:
                self.knowledge_graph.add_node(page_title.lower())
                for nutrient_sentence in nutrient_info:
                    nutrient_info = nutrient_sentence.split(" ")
                    for nutrient in nutrient_info:
                        if nutrient.lower() in self.nutrient_list:
                            self.knowledge_graph.add_edge(page_title.lower(), nutrient, relation="has")
                            continue

        taste_section = "taste"
        if taste_section in content:
            taste_content = content.split(taste_section)[1].split("==")[0]
            taste_info = [taste.strip() for taste in taste_content.split("\n") if taste.strip()]
            if taste_info:
                self.knowledge_graph.add_node(page_title.lower())
                for taste_sentence in taste_info:
                    taste_info = taste_sentence.split(" ")
                    for taste in taste_info:
                        if taste.lower() in self.flavor_list:
                            self.knowledge_graph.add_edge(page_title.lower(), taste.lower(), relation="tastes")
                            continue

        print(self.knowledge_graph.edges(data=True))

    def fuzzy_match(self, query, entities):
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
        return any(self.is_synonym(word, w) for w in word_list)

    def extract_colors(self, question):
        doc = self.nlp(question)
        colors = []
        fruit_colors = ['red', 'green', 'yellow', 'orange', 'blue', 'purple', 'pink']

        for token in doc:
            if token.text.lower() in fruit_colors or self.is_synonym_of_list(token.text.lower(), fruit_colors):
                colors.append(token.text.lower())

        return colors

    def get_color_relationships(self):
        color_relationships = {}
        for fruit in self.knowledge_graph.nodes:
            colors = [r[1].strip() for r in self.knowledge_graph.edges(fruit, data=True) if
                      r[2]['relation'] == 'is color']
            color_relationships[fruit] = colors
        return color_relationships

    def answer_color_question(self, fruit, colors):
        if len(colors) == 0:
            return f"{fruit} can have the color {self.color_relationships[fruit][0]}"

        if len(self.color_relationships[fruit]) > 0:
            for color in colors:
                if color in self.color_relationships[fruit] or self.is_synonym_of_list(color,
                                                                                       self.color_relationships[fruit]):
                    return f"{fruit} can have the color {color}"

        return f"{fruit} is not {colors[0]}"

    def is_color_question(self, question):
        return any(word in question for word in self.color_list) or any(
            self.is_synonym_of_list(word, self.color_list) for word in question.split())

    def is_grow_question(self, question):
        return any(word in question for word in self.grow_list) or any(
            self.is_synonym_of_list(word, self.grow_list) for word in question.split()) or any(
            word in question for word in self.location_list) or any(
            self.is_synonym_of_list(word, self.location_list) for word in question.split())

    def is_ingredient_question(self, question):
        return any(word in question for word in self.is_list) or any(
            self.is_synonym_of_list(word, self.is_list) for word in question.split())

    def is_taste_question(self, question):
        return any(word in question for word in self.tastes_list) or any(
            self.is_synonym_of_list(word, self.tastes_list) for word in question.split())

    def answer_grow_question(self, fruit):
        return f"A {fruit} grows {self.fruit_grow_info[fruit]}."

    def answer_ingredient_question(self, fruit, nutrient):
        relationships = self.knowledge_graph.edges(fruit, data=True)
        nutrient_relationships = [r for r in relationships if
                                  fuzz.partial_ratio(r[2]['relation'], "has") > 80 and nutrient in r[1]]

        if nutrient == "":
            nutrient = [r[1] for r in nutrient_relationships]
            nutrient = str(nutrient)[2:-2]
            return f"{fruit} contains {nutrient}."
        elif nutrient_relationships:
            return f"Yes, {fruit} contains {nutrient}."
        else:
            return f"No, I'm not aware of {fruit} containing {nutrient}."

    def answer_taste_question(self, fruit, taste):
        relationships = self.knowledge_graph.edges(fruit, data=True)
        # Find relationships matching the taste
        taste_relationships = [relation for relation in relationships if
                               fuzz.partial_ratio(relation[2]['relation'], "tastes") > 80 and taste in relation[1]]
        if taste_relationships:
            taste = [r[1] for r in taste_relationships]
            taste = str(taste)[2:-2]
            return f"{fruit} tastes {taste}."
        else:
            return f"No, I'm not aware of the taste of {fruit} being {taste}."

    def is_greeting(self, question):
        question = question.split()
        if any(word in question for word in self.greetings_list):
            return True
        else:
            return False




    def answer_question(self, question):
        if self.is_greeting(question):
            return "Hello! How can I assist you with fruits today?"

        fruit = self.get_fruit_type(question)
        print(fruit)
        colors = self.extract_colors(question)

        if fruit:
            if self.is_grow_question(question):
                return self.answer_grow_question(fruit)

            if self.is_ingredient_question(question):
                keywords = [word for word in self.is_list if word in question]
                if keywords:
                    nutrient = question.split(keywords[0])[1].strip()
                    return self.answer_ingredient_question(fruit, nutrient)
                else:
                    return "I'm sorry, I couldn't determine the nutrient in the question."

            if self.is_taste_question(question):
                # Extract the taste from the question
                keywords = [word for word in self.tastes_list if word in question]
                taste = question.split(keywords[0])[1].strip()
                return self.answer_taste_question(fruit, taste)

            if self.is_color_question(question):
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
