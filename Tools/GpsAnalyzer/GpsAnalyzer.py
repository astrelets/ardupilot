import argparse
import time
from datetime import datetime
import DataflashLog
import matplotlib.pyplot as plt
import numpy as np


def plot(logdata):
    if "GPS" not in logdata.channels:
        raise ValueError("No GPS data")

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    gps = logdata.channels['GPS']
    # reshaping without listData line numbers
    status = np.array(gps['Status'].listData)[:, 1]
    mask = status >= 3  # get only messages with GPS 3D fix
    lat = np.array(gps['Lat'].listData)[:, 1][mask]
    long = np.array(gps['Lng'].listData)[:, 1][mask]
    alt = np.array(gps['Alt'].listData)[:, 1][mask]
    spd = np.array(gps['Spd'].listData)[:, 1][mask]
    # vertical velocity available
    if 'GPA' in logdata.channels and logdata.channels['GPA']['VV'].max() > 0:
        vz = np.array(gps['VZ'].listData)[:, 1][mask]
        speed = np.sqrt(np.square(spd) + np.square(vz))
    else:
        speed = spd
        

    ax.plot(lat, long, alt, color='grey')

    scatter = ax.scatter(lat, long, alt, c=speed, cmap='jet')
    colorbar = fig.colorbar(scatter)
    colorbar.set_label('speed (m/s)')

    ax.invert_xaxis()
    ax.set_xlabel('lat')
    ax.set_ylabel('long')
    ax.set_zlabel('alt (m)')

    plt.show()
    
    
def csv(logdata, outfile):
    if "GPS" not in logdata.channels:
        raise ValueError("No GPS data")
    gps = logdata.channels['GPS']
    # reshaping without listData line numbers
    time = np.array(gps['TimeUS'].listData, dtype=np.uint64)[:, 1]
    lat = np.array(gps['Lat'].listData)[:, 1]
    long = np.array(gps['Lng'].listData)[:, 1]
    alt = np.array(gps['Alt'].listData)[:, 1]
    
    # calculating GMT time
    gwk = np.array(gps['GWk'].listData, dtype=np.uint64)[:, 1]
    gms = np.array(gps['GMS'].listData, dtype=np.uint64)[:, 1]
    leaps = 18 #TODO: use GRXH.leapS
    gms_epoch = int((datetime(1980, 1, 5) - datetime(1970, 1, 1)).total_seconds() * 1000)
    gmt = (gms_epoch + gwk * 604800000 + gms - leaps * 1000).astype('datetime64[ms]')
    
    
    #TODO: use pandas
    res = np.rec.fromarrays((gmt.astype(np.uint64), time, lat, long, alt), 
                                    dtype=[("GMT", np.uint64),
                                         ("TimeUS", np.uint64), 
                                         ("Lat", np.float64), 
                                         ("Lng", np.float64),
                                         ("Alt", np.float64)])
    np.savetxt(outfile, res, delimiter=',', 
               fmt=['%u','%u','%.7f','%.7f','%.1f'], 
               header=','.join(res.dtype.names))
    

def main():
    # deal with command line arguments
    parser = argparse.ArgumentParser(description='Analyze Dataflash log GPS data')
    parser.add_argument('logfile', type=argparse.FileType('r'), help='path to Dataflash log file (or - for stdin)')
    parser.add_argument(
        '-f',
        '--format',
        metavar='',
        type=str,
        action='store',
        choices=['bin', 'log', 'auto'],
        default='auto',
        help='log file format: \'bin\',\'log\' or \'auto\'',
    )
    parser.add_argument(
        '-s', '--skip_bad', metavar='', action='store_const', const=True, help='skip over corrupt dataflash lines'
    )
    
    parser.add_argument('command', choices=['plot', 'csv'], help='what to do with logfile')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default='-', help='output file (or - for stdout)')
    
    parser.add_argument('-v', '--verbose', metavar='', action='store_const', const=True, help='verbose output')
    args = parser.parse_args()

    # load the log
    startTime = time.time()
    logdata = DataflashLog.DataflashLog(args.logfile.name, format=args.format, 
                                        ignoreBadlines=args.skip_bad)  # read log
    endTime = time.time()
    if args.verbose:
        print("Log file read time: %.2f seconds" % (endTime - startTime))

    if args.command == 'plot':
        plot(logdata)
    elif args.command == 'csv':          
        csv(logdata, args.outfile)
    

if __name__ == "__main__":
    main()
