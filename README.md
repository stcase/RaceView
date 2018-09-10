# RaceView
This is a tool to visualize race data from Seattle's MFG and Cross Revolution cyclocross races in Tableau.

# How to Use:
## MFG
Note that these instructions are roughly how I used it in 2017, but it seemed that every year things changed slightly, and some tweaks to the code were needed.
- For each race time in webscorer for a race day, select Download results for edit > Tab-delimited TXT file
- Save those files into the folder Data/Raw/MFG [year]/MFG[Race #]
- Process data with Python 3 using the command (on windows this works best in command line rather than power shell) ```python process_mfg.py -r "MFG [Race #] - [Race Name]" "data\raw\MFG [year]\MFG [Race #]" data\consumable\[year]\MFG1.csv```
- Open Analysis.twb with Tableau Professional
- Switch to the Data Source tab and union your new file above in the consumable folder to the current data source

## Cross Revolution
- To be added later
