
# RetroArch CleanNaming
This is a simple scripts, that help you to rename the ROMs with the right naming 

# Requirement
```
git clone https://github.com/libretro/libretro-database.git
pip install python-Levenshtein
```

# Config
You can update the config.json

Just add the new extensions you want, and the libretro dataset you want to use
```
{
  "smc": "libretro-database/metadat/No-Intro/Nintendo - Super Nintendo Entertainment System.dat",
  "sfc": "libretro-database/metadat/No-Intro/Nintendo - Super Nintendo Entertainment System.dat",
  "gb": "libretro-database/metadat/No-Intro/Nintendo - Game Boy.dat",
  "gbc": "libretro-database/metadat/No-Intro/Nintendo - Game Boy Color.dat",
  "md": "libretro-database/metadat/No-Intro/Sega - Mega Drive - Genesis.dat",
  "nes": "libretro-database/metadat/No-Intro/Nintendo - Nintendo Entertainment System.dat",
  "32x": "libretro-database/metadat/No-Intro/Sega - 32X.dat",
  "n64": "libretro-database/metadat/No-Intro/Nintendo - Nintendo 64.dat",
  "v64": "libretro-database/metadat/No-Intro/Nintendo - Nintendo 64.dat",
  "nds": "libretro-database/metadat/No-Intro/Nintendo - Nintendo DS.dat",
  "iso": "libretro-database/metadat/No-Intro/Sony - PlayStation Portable.dat"
}
```

# Usage
Put all the ROMs in the current directory, and run the scripts

# Run
```
python3 rename_roms.py
```
# parameters
You can change the matching distance by adding this parameter and change the value, more the number is higher more the approx will be
```
python3 rename_roms.py -distance=10
```

# Results
The ROMs will be renamed according to the database of libretro

# RetroArch
Then you simply have to scan the directory and everything will be recognized well
