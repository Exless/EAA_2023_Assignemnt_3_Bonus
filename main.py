#!/usr/bin/env python3
from random import randint, sample
from random import choice as random_choice
from enum import Enum
from sys import exit


class VertexColoringState(Enum):
    COLOR_ACCEPTED = 1
    COLOR_REJECTED = 2


VertexId = int
VertexColor = int
Neighbor = tuple[VertexColor, VertexColoringState]
Neighbors = dict[VertexId, Neighbor]


class Vertex:
    def __init__(self, idx: int):
        self.id = idx
        self.neighbors: Neighbors = {}
        self.candidates = []
        self.coloring_state = VertexColoringState.COLOR_REJECTED

    def choose_random_color(self, delta: int):
        # we want delta + 1 choices, so we can choose a color from 0 to delta
        # as the 2nd argument of randint is inclusive
        self.chosen_color: VertexColor = randint(0, delta)

    def update_neighbor(
        self,
        neighbor_id: VertexId,
        neighbor_color: VertexColor,
        neighbor_coloring_state: VertexColoringState,
    ):
        if (self.coloring_state == VertexColoringState.COLOR_ACCEPTED 
            and neighbor_coloring_state == VertexColoringState.COLOR_ACCEPTED
            and self.chosen_color == neighbor_color):
            print(f"Vertex {self.id} has accepted color {self.chosen_color} but neighbor {neighbor_id} has the same color")
            exit(1)

        self.neighbors[neighbor_id] = (neighbor_color, neighbor_coloring_state)

    def decide_if_color_accept(self, vertices: list):
        # if our color is the same as any of our neighbors, we reject it
        # otherwise we accept it
        if self.coloring_state == VertexColoringState.COLOR_ACCEPTED:
            return

        for neighbors_color, _ in self.neighbors.values():
            if neighbors_color == self.chosen_color:
                return
        
        self.coloring_state = VertexColoringState.COLOR_ACCEPTED

    def coloring_round(self, delta):
        if self.coloring_state == VertexColoringState.COLOR_ACCEPTED:
            return
        # 2nd elemnt of range is exclusive, thats why we do the delta + 1
        # to have delta + 1 choices as the color candidate set
        color_candidate_set: list[VertexColor] = list(range(0, delta + 1))

        # remove colors of our neighbors which have accepted their color
        # the color candidate set
        # as we cannot choose those colors
        for neighbors_color, neighbors_coloring_state in self.neighbors.values():
            if neighbors_coloring_state == VertexColoringState.COLOR_ACCEPTED:
                color_candidate_set = list(
                    filter(lambda x: x != neighbors_color, color_candidate_set)
                )

        if len(color_candidate_set) == 0:
            print("color candidate set is empty, we screwed up somewhere")
            exit(1)

        # pick a random color from the color candidate set
        self.chosen_color = random_choice(color_candidate_set)


def pick_n_neighbor_indicies(
    n: int, verticies: list[VertexId], current_vertex: VertexId
) -> list[VertexId]:
    # filter out the current vertex from the neighbor choices
    neighbor_choices = list(filter(lambda x: x != current_vertex, verticies))

    return sample(neighbor_choices, n)

def sanity_check_neighbors(vertices: list[Vertex]):
    for vertex in vertices:
        for neighbor_id, (neighbor_color, neighbor_coloring_state) in vertex.neighbors.items():
            neighbor = vertices[neighbor_id]

            if vertex.id not in neighbor.neighbors.keys():
                print(f"Vertex {neighbor_id} doesn't have {vertex.id} as a neighbor")
                exit(1)
    print("Neighborhood sanity check passed")


def generate_graph(n: int, delta: int) -> list[Vertex]:
    vertices: list[Vertex] = []
    for i in range(n):
        v = Vertex(i)
        v.choose_random_color(delta)
        vertices.append(v)

    # Each vertex has delta neighbors
    for vertex_id in range(len(vertices)):
        # Random |delta| many neighbors
        vertex = vertices[vertex_id]
        neighbors = pick_n_neighbor_indicies(delta, list(range(n)), vertex.id)
        for neighbor in neighbors:
            vertex_neighbor = vertices[neighbor]
            # Update the neighbors of both vertices
            if len(vertex_neighbor.neighbors) >= delta or len(vertex.neighbors) >= delta:
                # print(f"Skipping neighbor {neighbor} neighbors: {len(vertex_neighbor.neighbors)} for vertex {vertex.id}: {len(vertex.neighbors)}")
                continue

            vertex.update_neighbor(
                neighbor, vertex_neighbor.chosen_color, vertex_neighbor.coloring_state
            )
            vertex_neighbor.update_neighbor(
                vertex.id, vertex.chosen_color, vertex.coloring_state
            )

    sanity_check_neighbors(vertices)
    return vertices


def message_passing(vertices: list[Vertex]):
    # in a distributed setting this would obviously happen in parallel and each vertex
    # would pass this by itself, but here it's only emulated since we're only emulating
    # a distributed setting
    for vertex in vertices:
        for neighbor_vertex_id in vertex.neighbors.keys():
            neighbor_vertex = vertices[neighbor_vertex_id]
            neighbor_vertex.update_neighbor(
                vertex.id, vertex.chosen_color, vertex.coloring_state
            )

def decide_if_color_accept(vertices: list[Vertex]):
    for vertex in vertices:
        vertex.decide_if_color_accept(vertices)

def coloring_round(vertices: list[Vertex], delta: int, round_idx: int = 0):
    for vertex in vertices:
        vertex.coloring_round(delta)


## Main loop (note to tutor: you can change the number of verticies and delta here)
number_of_verticies = 500
delta = 20
graph = generate_graph(number_of_verticies, delta)

def get_done_verticies(graph):
    done_verticies = 0
    for vertex in graph:
        if vertex.coloring_state == VertexColoringState.COLOR_ACCEPTED:
            done_verticies += 1

    return done_verticies

iteration = 0
while get_done_verticies(graph) != len(graph):
    decide_if_color_accept(graph)
    coloring_round(graph, delta, iteration)
    message_passing(graph)

    iteration += 1
    print(f"Iteration: {iteration} Colored Verticies {get_done_verticies(graph)} out of {len(graph)}")

print(f"Done in {iteration} iterations")


## Checking correctness
def sanity_check_coloring(graph):
    for vertex in graph:
        for neighbor_id in vertex.neighbors.keys():
            neighbor = graph[neighbor_id]

            if not (vertex.chosen_color >= 0 and vertex.chosen_color <= delta):
                print(f"Vertex {vertex.id} has invalid color {vertex.chosen_color}")
                exit(1)

            if vertex.chosen_color == neighbor.chosen_color:
                print(f"Vertex {vertex.id} has the same color as neighbor {neighbor_id}")
                exit(1)
    print("Coloring sanity check passed")

sanity_check_coloring(graph)