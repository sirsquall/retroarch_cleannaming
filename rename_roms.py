import os
import re
import json
import zlib
import sys
from Levenshtein import distance

# Load configuration from JSON file
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
with open(config_path, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Path to your ROM files
roms_path = os.path.dirname(os.path.realpath(__file__))

# Default closest distance
closest_distance_threshold = 10

# Parse command line arguments
for arg in sys.argv[1:]:
    if arg.startswith('-distance='):
        closest_distance_threshold = int(arg.split('=')[1])

def parse_dat_file(dat_file_path, filter_prefix):
    name_map = {}
    game_block = []
    in_game_block = False
    with open(dat_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'game (' in line:
                in_game_block = True
                game_block = [line]
            elif in_game_block:
                game_block.append(line)
                if ')' in line:
                    in_game_block = False
                    game_block_content = ''.join(game_block)
                    game_name_match = re.search(r'name "(.+?)"', game_block_content)
                    if game_name_match:
                        game_name = game_name_match.group(1)
                        if game_name.lower().startswith(filter_prefix.lower()):
                            name_map[game_name.lower().strip()] = game_name
    return name_map

def get_crc32(filepath):
    prev = 0
    with open(filepath, "rb") as file:
        for eachLine in file:
            prev = zlib.crc32(eachLine, prev)
    return "%08X" % (prev & 0xFFFFFFFF)

def arabic_to_roman(number):
    arabic_roman_map = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    roman_number = ''
    for (arabic, roman) in arabic_roman_map:
        while number >= arabic:
            roman_number += roman
            number -= arabic
    return roman_number

def correct_region_tag(name):
    name = name.replace('(FR)', '(Europe)')
    name = name.replace('(U)', '(USA)')
    name = name.replace('(E)', '(Europe)')
    name = name.replace('(EU)', '(Europe)')
    name = name.replace('(JP)', '(Japan)')
    return name

def normalize_name(name):
    # Specific handling for Final Fantasy titles
    final_fantasy_match = re.match(r'final fantasy (\d+)', name, re.IGNORECASE)
    if final_fantasy_match:
        number = int(final_fantasy_match.group(1))
        roman_number = arabic_to_roman(number)
        name = re.sub(r'final fantasy \d+', f'Final Fantasy {roman_number}', name, flags=re.IGNORECASE)
    
    # Apply general region fix
    name = correct_region_tag(name)

    # Change CD to Disc
    name = re.sub(r'CD(\d+)', r'Disc \1 of', name, flags=re.IGNORECASE)

    # Ensure the format matches the database entries
    disc_match = re.search(r'Disc (\d+) of', name)
    if disc_match:
        disc_number = disc_match.group(1)
        name = re.sub(r'Disc \d+ of', f'(Disc {disc_number} of )', name)
    
    # Return the normalized name
    return name.lower().strip()

def extract_number_from_name(name):
    match = re.search(r'\d+', name)
    if match:
        return match.group(0)
    return None

# Gather all files by extension
files_by_extension = {}
for filename in os.listdir(roms_path):
    filepath = os.path.join(roms_path, filename)
    if os.path.isfile(filepath):
        extension = filename.split('.')[-1].lower()
        if extension in config:
            if extension not in files_by_extension:
                files_by_extension[extension] = []
            files_by_extension[extension].append(filename)

# Process files by extension
for extension, filenames in files_by_extension.items():
    dat_file_path = os.path.join(roms_path, config[extension])
    
    # Process each file
    for filename in filenames:
        filepath = os.path.join(roms_path, filename)
        filter_prefix = filename[:3]  # Use the first three letters for filtering
        name_map = parse_dat_file(dat_file_path, filter_prefix)
        crc = get_crc32(filepath)
        if crc in name_map:
            new_name = f"{name_map[crc]}.{extension}"
            new_name = correct_region_tag(new_name)
            new_filepath = os.path.join(roms_path, new_name)
            if not os.path.exists(new_filepath):
                os.rename(filepath, new_filepath)
                print(f'Renamed {filename} to {new_name}')
            else:
                print(f'File {new_filepath} already exists, skipping renaming to avoid overwriting.')
        else:
            # If the exact CRC match is not found, use approximate matching
            closest_match = None
            closest_distance = float('inf')
            norm_filename = normalize_name(filename.rsplit('.', 1)[0])
            filename_number = extract_number_from_name(norm_filename)
            print(f"Normalized filename: {norm_filename}")

            for db_name in name_map.keys():
                db_name_number = extract_number_from_name(db_name)
                if filename_number and db_name_number and filename_number != db_name_number:
                    continue
                current_distance = distance(norm_filename, db_name)
                if current_distance < closest_distance:
                    closest_distance = current_distance
                    closest_match = name_map[db_name]

            if closest_match and closest_distance < closest_distance_threshold:  # Use the threshold from the command line or default
                new_name = f"{closest_match}.{extension}"
                new_name = correct_region_tag(new_name)
                new_filepath = os.path.join(roms_path, new_name)
                if not os.path.exists(new_filepath):
                    os.rename(filepath, new_filepath)
                    print(f'Approximately renamed {filename} to {new_name}')
                else:
                    print(f'File {new_filepath} already exists, skipping renaming to avoid overwriting.')
            else:
                print(f'No close match found for {filename}')
