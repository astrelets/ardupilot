# GpsAnalyzer

Commandline script for GPS data manipulation


## Usage
```commandline
usage: GpsAnalyzer.py [-h] [-f] [-s] [-o OUTFILE] [-v] logfile {plot,csv}

Analyze Dataflash log GPS data

positional arguments:
  logfile               path to Dataflash log file (or - for stdin)
  {plot,csv}            what to do with logfile

options:
  -h, --help            show this help message and exit
  -f , --format         log file format: 'bin','log' or 'auto'
  -s, --skip_bad        skip over corrupt dataflash lines
  -o OUTFILE, --outfile OUTFILE
                        output file (or - for stdout)
  -v, --verbose         verbose output
```

## Plot
show 3D GPS track
```commandline
python GpsAnalyzer.py fpv01.log plot
```

## CSV
export GPS data to CSV file
```commandline
python GpsAnalyzer.py fpv01.log csv --outfile=fpv01.csv
```
