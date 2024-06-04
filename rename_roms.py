import os
import re
from Levenshtein import distance
import zlib

# Configuration mapping extensions to DAT files
config = {
    'smc': 'libretro-database/metadat/No-Intro/Nintendo - Super Nintendo Entertainment System.dat',
    'sfc': 'libretro-database/metadat/No-Intro/Nintendo - Super Nintendo Entertainment System.dat',
    'gb': 'libretro-database/metadat/No-Intro/Nintendo - Game Boy.dat',
    'gbc': 'libretro-database/metadat/No-Intro/Nintendo - Game Boy Color.dat',
    'md': 'libretro-database/metadat/No-Intro/Sega - Mega Drive - Genesis.dat',
    'nes': 'libretro-database/metadat/No-Intro/Nintendo - Nintendo Entertainment System.dat',
    '32x': 'libretro-database/metadat/No-Intro/Sega - 32X.dat',
    'n64': 'libretro-database/metadat/No-Intro/Nintendo - Nintendo 64.dat',
    'v64': 'libretro-database/metadat/No-Intro/Nintendo - Nintendo 64.dat',
    'nds': 'libretro-database/metadat/No-Intro/Nintendo - Nintendo DS.dat'
}

# Path to your ROM files
roms_path = os.path.dirname(os.path.realpath(__file__))

def parse_dat_file(dat_file_path):
    name_map = {}
    with open(dat_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        games = re.findall(r'game \(\s*name "(.+?)".+?crc ([0-9A-Fa-f]{8})', content, re.DOTALL)
        for name, crc in games:
            name_map[crc.upper()] = name
    return name_map

def get_crc32(filepath):
    prev = 0
    for eachLine in open(filepath, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%08X" % (prev & 0xFFFFFFFF)

def normalize_name(name):
    # Remove version information, special characters, and region tags
    name = re.sub(r'-\s*Version\s*\d+(\.\d+)?', '', name)  # Remove version info
    name = re.sub(r'\(.*?\)', '', name)  # Remove anything in parentheses
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)  # Remove special characters
    return name.lower().strip()

def correct_region_tag(name):
    name = name.replace('(U)', '(USA)')
    name = name.replace('(E)', '(Europe)')
    return name

# Process files
for filename in os.listdir(roms_path):
    filepath = os.path.join(roms_path, filename)
    if os.path.isfile(filepath):  # Ensure it's a file, not a directory
        extension = filename.split('.')[-1].lower()
        if extension in config:
            dat_file_path = os.path.join(roms_path, config[extension])
            name_map = parse_dat_file(dat_file_path)
            
            crc = get_crc32(filepath)
            
            if crc in name_map:
                new_name = f"{name_map[crc]}.{extension}"
                new_name = correct_region_tag(new_name)
                new_filepath = os.path.join(roms_path, new_name)
                os.rename(filepath, new_filepath)
                print(f'Renamed {filename} to {new_name}')
            else:
                # If the exact CRC match is not found, use approximate matching
                closest_match = None
                closest_distance = float('inf')
                norm_filename = normalize_name(filename.rsplit('.', 1)[0])
                
                for db_crc, db_name in name_map.items():
                    norm_db_name = normalize_name(db_name)
                    current_distance = distance(norm_filename, norm_db_name)
                    if current_distance < closest_distance:
                        closest_distance = current_distance
                        closest_match = db_name

                if closest_match and closest_distance < 10:  # Lower threshold for approximate match
                    new_name = f"{closest_match}.{extension}"
                    new_name = correct_region_tag(new_name)
                    new_filepath = os.path.join(roms_path, new_name)
                    os.rename(filepath, new_filepath)
                    print(f'Approximately renamed {filename} to {new_name}')
                else:
                    print(f'No close match found for {filename}')
