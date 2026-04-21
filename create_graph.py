import networkx as nx
import matplotlib.pyplot as plt
import json

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

        # Converting list format into dictionary format for the create graph function
        data = {}
        for course_id, course in json_data.items(): # changed from json_data["classes"] to json_data because the file is changed from classes.json to data.json
            # handle inconsistent key names
            difficulty = course.get("difficulty_score", course.get("difficulty_Score"))

            data[course_id]  = {
                "name": course["name"],
                "credit_hours": course["credit_hours"],
                "prereqs": course["prereqs"],
                "is_transferable": course["is_transferable"],
                "availability": course["availability"],
                "difficulty_Score": difficulty,
                "expected_gpa": course["expected_gpa"]
            }
        
        return data

def create_graph(data):
    degree_flow = nx.DiGraph()
    for course in data:
        info = data[course]
        difficulty = info.get("difficulty_score", info.get("difficulty_Score"))
        degree_flow.add_node(course, name=info['name'], credit_hours=info['credit_hours'], is_transferable=info['is_transferable'],difficulty=difficulty, expected_gpa=info["expected_gpa"])        
        for prereq_course in info["prereqs"]:
           degree_flow.add_edge(prereq_course, course)
    return degree_flow
           

data = load_data_from_json('data.json')
sample_graph = create_graph(data)

position = nx.spring_layout(sample_graph)
nx.draw_networkx_nodes(sample_graph, position, node_color='lightblue', node_size=2000)
nx.draw_networkx_edges(sample_graph, position, arrowstyle='->', arrowsize=20)
nx.draw_networkx_labels(sample_graph, position, font_size=10, font_weight='bold')

plt.title("Degree Plan Graph")
plt.axis('off')
plt.show()