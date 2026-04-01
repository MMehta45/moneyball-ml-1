import networkx as nx
import matplotlib.pyplot as plt
import json

def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

        # Converting list format into dictionary format for the create graph function
        data = {}
        for course in json_data["classes"]:
            data[course["course_id"]]  = {
                "name": course["name"],
                "credit_hours": course["credit_hours"],
                "prereqs": course["prereqs"],
                "is_transferable": course["is_transferable"],
                "availability": course["availability"],
                "difficulty": course["difficulty"],
                "expected_gpa": course["expected_gpa"]
            }
        
        return data

def create_graph(data):
    degree_flow = nx.DiGraph()
    for course in data:
        info = data[course]
        degree_flow.add_node(course, name=info['name'], credit_hours=info['credit_hours'], is_transferable=info['is_transferable'],difficulty=info['difficulty'], expected_gpa=info["expected_gpa"])        
        for prereq_course in info["prereqs"]:
           degree_flow.add_edge(prereq_course, course)
    return degree_flow
           

data = load_data_from_json('classes.json')
sample_graph = create_graph(data)

position = nx.spring_layout(sample_graph)
nx.draw_networkx_nodes(sample_graph, position, node_color='lightblue', node_size=2000)
nx.draw_networkx_edges(sample_graph, position, arrowstyle='->', arrowsize=20)
nx.draw_networkx_labels(sample_graph, position, font_size=10, font_weight='bold')

plt.title("Degree Plan Graph")
plt.axis('off')
plt.show()


