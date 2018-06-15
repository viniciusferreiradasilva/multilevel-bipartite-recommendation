import numpy as np
from collections import defaultdict
import csv
import operator
import os
# Generates the output data for analysis of the algorithms.
dirs = ["2layers", "itemlayer", "userlayer"]

start = 100
end = 10000
step = 200
codes = {"2layers": "01", "userlayer": "0", "itemlayer": "1"}
# For each directory in the list...
for directory in dirs:
    for output_file in sorted(os.listdir(directory)):
        output_file_name = output_file.split("l.")[0] + "_" + codes[directory]
        ofile  = open(("output/"+output_file_name+'.csv'), 'wb')
        writer = csv.writer(ofile, delimiter=',')
        writer.writerow(("L", "MEAN PR", "STD PR", "MEAN AUC", "STD AUC", "MEAN TIME", "STD TIME"))

        # Builds the path for the csv file.
        path = directory + "/" + output_file
        columns = defaultdict(list)
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                for (k,v) in row.items():
                    columns[k].append(float(v))

        for par in range(start, end, step):
            pr_key = "pr"+str(par)
            # Gets the precision.
            mean_pr = np.mean(columns[pr_key])
            std_pr = np.std(columns[pr_key])

            auc_key = "AUC"+str(par)
            # Gets the AUC.
            mean_auc = np.mean(columns[auc_key])
            std_auc = np.std(columns[(auc_key)])

            # Gets the Time.
            time_key = "time"
            mean_time = np.mean(columns[time_key])
            std_time = np.std(columns[time_key])
            # Writer the row in the file.
            writer.writerow((par, mean_pr, std_pr, mean_auc, std_auc, mean_time, std_time))
        f.close()
ofile.close()
