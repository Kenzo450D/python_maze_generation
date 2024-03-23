import numpy as np
import sys
import cv2

index_map = {0:(-1,0), 1:(0,1), 2:(1,0), 3:(0,-1)}
index_fliped_map = {0:2, 1:3, 2:0, 3:1}

def print_array(arr):
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            print (arr[i,j], end="\t")
        print()
    return

def get_stating_position(n_rows: int, n_cols: int)->tuple:
    ''' Get a random position in the array to begin the maze from
    '''
    sr = np.random.randint(0,n_rows)
    sc = np.random.randint(0,n_cols)
    return (sr, sc)

def get_unvisited_random(r, c, visited):
    ''' Returns a possible unvisited neighbor the agent can go to
    If None is available, returns None 
    Steps: 
    1. Generates a list of unvisited neighbors
    2. Generates a random number within its length
    3. Returns the index
    '''
    ret_array = []
    if (r > 0 and visited[r-1,c] == False):
        ret_array.append(0)
    if (r < visited.shape[0]-1 and visited[r+1,c] == False):
        ret_array.append(2)
    if (c < visited.shape[1]-1 and visited[r,c+1] == False):
        ret_array.append(1)
    if (c > 0 and visited[r,c-1]== False):
        ret_array.append(3)
    if len(ret_array) == 0:
        return None # no available directions
    random_index = np.random.randint(0,len(ret_array))
    direction_index = ret_array[random_index]
    random_direction = index_map[ret_array[random_index]]
    print ("Ret array: ", ret_array)
    print ("Random index: ", random_index)
    print ("Random direction : ", random_direction)
    print ("Target coordinate: ", random_direction[0]+r, random_direction[1]+c)
    return (random_direction[0]+r, random_direction[1]+c, direction_index)

def update_walls(walls, sr, sc, tr, tc, target_direction):
    ''' Update the walls array to accomodate an edge 
    '''
    # -- change the wall to accomodate edge from source index to target index
    walls[(sr, sc)] -= 10**target_direction
    # -- change the wall to accomodate edge from target index to source index
    walls[(tr, tc)] -= 10**index_fliped_map[target_direction]
    # -- return
    return


def generate_maze(sr, sc, walls, visited):
    ''' Generates maze using recursive depth
    '''

    target = get_unvisited_random(sr, sc, visited) # target row and target column
    while target != None:
        # -- mark target as visited and visit target
        visited[(target[0],target[1])] = 1
        # -- change walls
        update_walls(walls, sr, sc, target[0],target[1], target[2])
        # -- print
        print_array(visited)
        print ()
        print_array(walls)
        print ("-"*100)
        # -- recursively call to generate maze
        generate_maze(target[0],target[1], walls, visited)
        target = get_unvisited_random(sr, sc, visited) # target row and target column
    # -- return if nothing is accessible
    return

def save_maze_to_image(walls, image_name):
    ''' saves the maze as an image file
    1. Initialize an image in OpenCV:
        a. Calculate image size
        b. Initialize color palette
    2. Draw walls:
        a. Draw periphery of the room
        b. For each wall tag in walls, draw a line on the image
    3. Each rooms is 100x100
    NOTE: OpenCV has flipped coordinates to access the image points (columns, rows)
    '''
    usize = 100 # unit size
    #-- calculate image height
    height = walls.shape[0]*usize
    width = walls.shape[1]*usize
    image = np.zeros((height, width, 3), np.uint8) # image starts as black image (pixel value 0)

    # -- initialize color palette
    color_white =  (255, 255, 255)
    color_black = (0, 0, 0)
    color_edge_gray = (70,70,70)
    graph_edge_line_width = 4
    wall_edge_line_width = 6

    # -- create the wall boundary
    x1 = 5
    y1 = 5
    x2 = width - 6 # openCV indices start from 0 and end at width-1
    y2 = height - 6 # openCV indices start from 0 and end at height-1
    cv2.rectangle(image, (x1, y1), (x2, y2), color_white, -1) # negative number means filled rectangle

    # -- Loop through all elements in the walls array, and draw full lines on either side
    count = 0
    for i in range(walls.shape[0]): #rows
        for j in range(walls.shape[1]): #columns
            wall_val = walls[i][j]
            print (f"Index: {count} :: row: {i} :: col: {j} :: Val: {wall_val}")
            # -- depending on the element draw the wall
            if wall_val % 10 == 1:
                # wall on the top
                x1 = j*usize #column
                y1 = i*usize
                x2 = x1+usize
                y2 = y1
                cv2.line(image, (x1,y1), (x2,y2), color_black, wall_edge_line_width)
                # print ("Make top line")
                # cv2.imwrite(f"rooms-colored_{count}_top.png", image)
            wall_val //= 10
            # print ("Wall val after dividing by 10: ", wall_val)
            # print ("Right Wall: ", wall_val%10)
            if wall_val % 10 == 1:
                # wall on the right
                x1 = (j+1)*usize #column
                y1 = i*usize # row
                x2 = x1
                y2 = y1 + usize
                cv2.line(image, (x1,y1), (x2,y2), color_black, wall_edge_line_width)
                # print ("Make right line")
                # cv2.imwrite(f"rooms-colored_{count}_rig.png", image)
            wall_val //= 10
            # print ("Wall val after dividing by 10: ", wall_val)
            # print ("Bottom Wall: ", wall_val%10)
            if wall_val % 10 == 1:
                # wall on the bottom
                x1 = j*usize #column
                y1 = (i+1)*usize # row
                x2 = x1+usize
                y2 = y1
                cv2.line(image, (x1,y1), (x2,y2), color_black, wall_edge_line_width)
                # print ("Make bottom line")
                # cv2.imwrite(f"rooms-colored_{count}_bot.png", image)
            wall_val //= 10
            # print ("Wall val after dividing by 10: ", wall_val)
            # print ("Left Wall: ", wall_val%10)
            if wall_val % 10 == 1:
                # wall on the left
                x1 = j*usize #column
                y1 = i*usize
                x2 = x1
                y2 = y1 + usize
                cv2.line(image, (x1,y1), (x2,y2), color_black, wall_edge_line_width)
                # print ("Make left line")
                # cv2.imwrite(f"rooms-colored_{count}_lef.png", image)
            cv2.imwrite(f"rooms-colored_{count}.png", image)
            count += 1
    return

def save_maze_as_graph(walls, filename_edge, filename_vertex_plot_map, filename_vertex_tag, vertex_start=0, edge_start=1):
    # -- go through the walls, for each vertex, get the edges to the right and the bottom
    # -- add edges to edge list
    # -- add vertex positions to vertex_pos_map
    # -- save the edge list and vertex positions to the file.
    edges_list = []
    vertex_map = []
    vertex_tag = []
    for i in range(walls.shape[0]): #rows
        for j in range(walls.shape[1]): #columns
            wall_val = walls[i][j]
            # -- get the bottom and the right values
            # bottom value is given by the 3rd digit from left
            # right value is given by the 2nd digit from the left
            right_val = (wall_val // 10) % 10
            bot_val = (wall_val // 100) % 10
            if right_val:
                edges_list.append((i*walls.shape[1] + j + edge_start, i*walls.shape[1] + j + 2, 2))
            if bot_val:
                edges_list.append((i*walls.shape[1] + j + edge_start, (i+1)*walls.shape[1] + j + 1, 2))
            # -- add the vertex to the plot map
            vertex_map.append((i*walls.shape[1] + j + vertex_start, (i*100) + 50, (j*100) + 50))
            # -- add the vertex to the tag map
            vertex_tag.append((i*walls.shape[1] + j + vertex_start, 'corridor'))

    # -- save the edge list in the file
    edge_count = len(edges_list)
    with open(filename_edge, 'w') as f:
        f.write(f'{edge_count} {walls.shape[0]} {walls.shape[1]}\n')
        for e in edges_list:
            f.write(f"{e[0]} {e[1]} {e[2]}\n")
    
    # -- save the vertex plot map
    with open(filename_vertex_plot_map, 'w') as f:
        for vm in vertex_map:
            f.write(f"{vm[0]} {vm[1]} {vm[2]}")
    
    # -- save the vertex tag
    with open(filename_vertex_tag, 'w') as f:
        for vt in vertex_tag:
            f.write(f"{vt[0]} {vt[1]}")



def main(n_rows:int, n_cols:int)->None:
    print (n_rows, n_cols)
    # -- generate an empty array
    walls = np.ones((n_rows, n_cols), dtype=np.int32)* 1111
    print_array(walls)

    # -- get an initial starting position
    (sr, sc) = get_stating_position(n_rows=n_rows, n_cols=n_cols)
    if not (isinstance(sr, int) and isinstance(sc, int)):
        print ("Starting row or starting column in not an int.")
        sys.exit(-1)
    print ("Starting coordinates: (row, col): ", sr, sc)

    # -- initialize a visited array
    visited = np.zeros_like(walls,dtype=bool)
    # mark the starting position as visited
    sr = 1
    sc = 1
    visited[sr, sc] = 1
    # visited[sr-1, sc] = 1
    # visited[sr+1, sc] = 1
    # visited[sr, sc - 1] = 1
    # visited[sr, sc + 1] = 1
    print_array(visited)

    # -- generate_maze_recursively(sr, sc, walls, visited)
    generate_maze(sr, sc, walls, visited)
    # -- save as image
    save_maze_to_image(walls, 'test.png')




    


def help():
    print ("Usage:")
    print ("python3 maze_generation.py <n_rows> <n_cols>")
    # print ("Exit.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ("Inadequate number of arguments. Needs 3")
        help()
        sys.exit(-1)
    n_rows = int(sys.argv[1])
    n_cols = int(sys.argv[2])
    main(n_rows, n_cols)

