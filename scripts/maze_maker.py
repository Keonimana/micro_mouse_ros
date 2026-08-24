import sys
from pathlib import Path

# Official IEEE Micromouse dimensions (in meters)
CELL_SIZE = 0.18
WALL_THICKNESS = 0.012
WALL_HEIGHT = 0.05
POST_SIZE = 0.012

# Writing to SDF.XACRO, maintain xacro macros
FILE_HEADER = """<?xml version="1.0" ?>
<sdf version="1.8" xmlns:xacro="http://www.ros.org/wiki/xacro">

    <!-- Templatizing Wall Parameters -->
	<xacro:property name="cell_size" 	 value="0.18"/>
	<xacro:property name="wall_thick"  	 value="0.012"/>
	<xacro:property name="wall_height" 	 value="0.05"/>
	<xacro:property name="post_size"     value="1.44"/>
	<xacro:property name="rotate_90" 	 value="1.5708"/>

	<!-- Wall Macro -->
	<xacro:macro name="wall" params="name x y yaw:=0">
    	<link name="${name}">
			<pose>${x} ${y} ${wall_height / 2} 0 0 ${yaw}</pose>
			<collision name="col">
				<geometry><box><size>${cell_size} ${wall_thick} ${wall_height}</size></box></geometry>
			</collision>
			<visual name="vis">
				<geometry><box><size>${cell_size} ${wall_thick} ${wall_height}</size></box></geometry>
				<material><ambient>0.8 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>
			</visual>
		</link>
	</xacro:macro>

    <!-- Pillar Macro -->
    <xacro:macro name="pillar" params="name x y">
        <link name="${name}">
            <pose>${x} ${y} ${wall_height / 2} 0 0 0</pose>
            <collision name="col">
                <geometry><box><size>${wall_thick} ${wall_thick} ${wall_height}</size></box></geometry>
            </collision>
            <visual name="vis">
                <geometry><box><size>${wall_thick} ${wall_thick} ${wall_height}</size></box></geometry>
                <material><ambient>0.8 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>
            </visual>
        </link>
    </xacro:macro>

	<!-- Locate Physics Engine -->
	<xacro:include filename="$(find micro_mouse)/mouse_sim/worlds/empty_macro.sdf.xacro"/>
"""

FILE_FOOTER = """
            </link>
		</model>
	</world>
</sdf>
"""

def generate_wall(wall_count, x, y, rotate):
    pose_str = f"<pose>{x} {y} " + "${wall_height / 2} 0 0 " + ("${rotate_90}" if rotate else "0") + "</pose>"
    material_str = "<material><ambient>0.8 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>"
    geometry_str = "<geometry><box><size>${cell_size} ${wall_thick} ${wall_height}</size></box></geometry>"
    visual_str = f"""<visual name="wall_vis_{hex(wall_count)}">{pose_str + geometry_str + material_str}</visual>"""
    collision_str = f"""<collision name="wall_col_{hex(wall_count)}">{pose_str + geometry_str}</collision>"""
    return "\t" * 4 + visual_str + collision_str

def generate_pillar(pillar_count, x, y):    
    pose_str = f"<pose>{x} {y} " + "${wall_height / 2} 0 0 0</pose>"
    material_str = "<material><ambient>0.9 0.1 0.1 1</ambient><diffuse>0.8 0.1 0.1 1</diffuse></material>"
    geometry_str = "<geometry><box><size>${wall_thick} ${wall_thick} ${wall_height}</size></box></geometry>"
    visual_str = f"""<visual name="pillar_vis_{hex(pillar_count)}">{pose_str + geometry_str + material_str}</visual>"""
    collision_str = f"""<collision name="pillar_col_{hex(pillar_count)}">{pose_str + geometry_str}</collision>"""
    return "\t" * 4 + visual_str + collision_str

def translate_maze(file_name, maze_number):

    # Retrieve maze identity number to complete boiler-plate xml
    sub_header = f"""
    <!-- World Definition -->
	<world name="maze_world_{maze_number}">
		<xacro:empty_world/>

		<!-- Maze Layout -->
		<model name="mouse_maze_{maze_number}">
			<static>true</static>

            <!-- Generated Maze Structure -->
            <link name="maze_structure">
                <pose>0 0 0 0 0 0</pose>

                <!-- Pillars -->"""

    # Retrive the path to input_maze
    script_dir = Path(__file__).resolve().parent
    package_root = script_dir.parent
    file_path = package_root / "mouse_sim" / "worlds" / "input_mazes" / file_name

    with open(file_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip()]

    # Get accurate number of rows/cols for maze layout
    # NOTE: we don't care about the number of cells, we care about the number of WALLS
    row_count, col_count = 0, 0
    for row in lines:
        row_count = row.count('o')
    for c in lines[0]:
        if c != "o": continue
        col_count += 1

    wall_count = 0
    pillar_count = 0
    sdf_world = [FILE_HEADER, sub_header]

    for r in range(row_count):
        for c in range(col_count):
            x = (r - row_count // 2) * CELL_SIZE
            y = (c - col_count // 2) * CELL_SIZE
            pillar_count += 1
            pillar_str = generate_pillar(pillar_count, x, y)
            sdf_world.append(pillar_str)

    sdf_world.append("\n" + "\t" * 4 + "<!-- Walls -->")
    
    for r, line in enumerate(lines):
        offset = 0 if r % 2 != 0 else 1
        columns = [line[i] for i in range(offset, len(line), 4)]

        for c, col in enumerate(columns):
            if col == " ":
                continue

            if (offset):
                x = (r//2 - row_count // 2) * CELL_SIZE
                y = (c - col_count // 2) * CELL_SIZE + (CELL_SIZE / 2)
            else:
                x = (r//2 - row_count // 2) * CELL_SIZE + (CELL_SIZE / 2)
                y = (c - col_count // 2) * CELL_SIZE

            wall_count += 1
            wall_str = generate_wall(wall_count, x, y, offset)
            sdf_world.append(wall_str)

    # Don't forget xml file ending
    sdf_world.append(FILE_FOOTER)

    # Build Output Path
    output_dir = package_root / "mouse_sim" / "worlds"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"maze_world_{maze_number}.sdf.xacro"

    # Write output file directly to mouse_sim/worlds/
    with open(output_file, 'w') as f:
        f.write("\n".join(sdf_world))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 maze_builder.py <input_maze.txt>")
    else:
        file_name = sys.argv[1]
        file_name = file_name.strip()

        if ((not file_name.endswith('.txt')) or ("_" not in file_name)) :
            print("Usage: expects a \".txt\" file as source in the format maze_<number>.txt")
        else:
            maze_number = file_name.split("_")[-1][0:-4] # retrieves unique maze identity
            translate_maze(file_name, maze_number)