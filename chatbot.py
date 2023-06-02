from fuzzywuzzy import fuzz
import networkx as nx


class FruitChatbot:
    def __init__(self):
        self.knowledge_graph = self.build_knowledge_graph()

    def build_knowledge_graph(self):
        graph = nx.Graph()

        fruits = ["apple", "banana", "orange"]
        graph.add_nodes_from(fruits)

        # Define relationships between fruits
        relationships = [
            ("apple", "is", "a fruit"),
            ("banana", "is", "a fruit"),
            ("orange", "is", "a fruit"),
            ("apple", "is", "red or green"),
            ("banana", "is", "yellow"),
            ("orange", "is", "orange"),
            ("apple", "has", "vitamin C"),
            ("banana", "has", "potassium"),
            ("orange", "has", "vitamin C and fiber")
        ]
        graph.add_edges_from((r[0], r[2], {'relation': r[1]}) for r in relationships)

        return graph

    def fuzzy_match(self, query, entities):
        best_match = None
        max_score = 0

        for entity in entities:
            score = fuzz.partial_ratio(query, entity)
            if score > max_score:
                max_score = score
                best_match = entity

        return best_match

    def answer_question(self, question):
        fruit = self.fuzzy_match(question, self.knowledge_graph.nodes())

        if fruit:
            relationships = self.knowledge_graph.edges(fruit, data=True)

            if relationships:
                if "has" in question:
                    nutrient = question.split("has")[1].strip()
                    nutrient_relationships = [r for r in relationships if
                                              r[2]['relation'] == "has" and nutrient in r[1]]
                    if nutrient_relationships:
                        return f"Yes, {fruit} contains {nutrient}."
                    else:
                        return f"No, I'm not aware of {fruit} containing {nutrient}."
                else:
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
