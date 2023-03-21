import os
import json
from scipy.io import savemat
path = 'johannas_files/json/'
fileslist = os.listdir(path)
for file in fileslist:
    filename = file.replace('_', ',').replace('.', ',').split(',')
    sub, run = 'sub-' + filename[1][:-1], 'run' + filename[1][-1]
    dic = json.load(open(path + file))
    dic['names'][0] = ' '.join(dic['names'][0])
    #dic['names'] = [' '.join(name) for name in dic['names']]
    print(dic['pmod'])
    matfilename = 'johannas_files/mat/johannas-' + sub +  '_' + run + '.mat'
    savemat(matfilename, dic)
