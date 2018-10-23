import json
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

with open("/Users/christopher/mesh_data.json", "r") as r:
    data = json.load(r)

def draw_mesh(vertices, edges, faces):
    tris, quads = split_into_tris_and_quads(faces)

    """glBegin(GL_QUADS)

    glColor3fv((1,0,0))

    for quad in quads:
        for vertex in quad:
            glVertex3fv(vertices[vertex])

    glEnd()"""

    """glBegin(GL_TRIANGLES)

    for tri in tris:
        for vertex in tri:
            glVertex3fv(vertices[vertex])

    glEnd()"""

    glBegin(GL_LINES)

    glColor3fv((1,1,0))

    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])

    glEnd()

def split_into_tris_and_quads(face_list):
    tris = []
    quads = []

    for face in face_list:
        if len(face) == 4:
            quads.append(face)
        elif len(face) == 3:
            tris.append(face)
        else:
            print("You have an ngon motherfucker")

    return tuple(tris), tuple(quads)

def main():
    max_distance = 100

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.0001, max_distance)

    glTranslatef(0.0,0.0,-3) #x,y,z

    glRotatef(0,0,0,0) #degrees, x, y, z

    finished = False

    x_move = 0
    y_move = 0
    z_move = 0

    obj_e = data['0']['Edges']
    obj_f = data['0']['Faces']
    obj_v = []
    for coordinate_set in data['0']['Vertices']: # [vertex_index, [co.x, co.y, co.z]]
        obj_v.append(tuple(coordinate_set[1]))
    obj_v = tuple(obj_v)

    while finished == False:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_move = 0.1
                if event.key == pygame.K_RIGHT:
                    x_move = -0.1

                if event.key == pygame.K_UP:
                    y_move = -0.1
                if event.key == pygame.K_DOWN:
                    y_move = 0.1

                if event.key == pygame.K_w:
                    z_move = 0.1
                if event.key == pygame.K_s:
                    z_move = -0.1

                if event.key == pygame.K_a:
                    glRotatef(2, 0.0, 1.0, 0.0)

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT) or (event.key == pygame.K_RIGHT):
                    x_move = 0
                if (event.key == pygame.K_UP) or (event.key == pygame.K_DOWN):
                    y_move = 0
                if (event.key == pygame.K_w) or (event.key == pygame.K_s):
                    z_move = 0 # Movement controls

        glTranslatef(x_move,y_move,z_move)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        draw_mesh(obj_v, obj_e, obj_f)

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()

main()
