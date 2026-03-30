import networkx as nx

dummy_data = {
    "CS1336": {"name": "Intro to CS", "prereqs": [], "difficulty": 0.5},
    "CS1337": {"name": "Computer Science I", "prereqs": ["CS1336"], "difficulty": 0.8},
    "CS2336": {"name": "Computer Science II", "prereqs": ["CS1337"], "difficulty": 0.9},
    "ARTS1301": {"name": "Art Appreciation", "prereqs": [], "difficulty": 0.2}
}
def create_graph(data):
    degree_flow = nx.DiGraph()
    for course in data:
        info = data[course]
        degree_flow.add_node(course, name=info['name'], difficulty=info['difficulty'])        
        for prereq_course in info["prereqs"]:
           degree_flow.add_edge(prereq_course, course)
    return degree_flow
           

