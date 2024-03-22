import numpy as np
import csv
import os
import time
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances
from scipy.spatial import distance
from itertools import islice
from sklearn.preprocessing import normalize


def listdir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append(file_path)


def get_similarity(ori, out):
    existnpy = []
    listdir('./dof', existnpy)
    j = 0
    Cos = []
    E = []
    M = []
    C = []
    exc = []

    reader = csv.reader(open(ori, 'r'))

    for r in reader:
        f1 = r[0].split('.java')[0]
        f2 = r[1].split('.java')[0]
        file1 = './dof\\' + f1 + '.npy'
        file2 = './dof\\' + f2 + '.npy'

        if file1 in existnpy and file2 in existnpy:
            matrix1 = np.load(file1)
            matrix1_1 = matrix1[:6,:]
            matrix1_2 = matrix1[6:11, :]
            matrix2 = np.load(file2)
            matrix2_1 = matrix2[:6, :]
            matrix2_2 = matrix2[6:11, :]
            cos1 = cosine_similarity(matrix1_1, matrix2_1)
            cos2 = cosine_similarity(matrix1_2, matrix2_2)
            euc1 = pairwise_distances(matrix1_1, matrix2_1)
            euc2 = pairwise_distances(matrix1_2, matrix2_2)
            man1 = pairwise_distances(matrix1_1, matrix2_1, metric='manhattan')
            man2 = pairwise_distances(matrix1_2, matrix2_2, metric='manhattan')
            che1 = pairwise_distances(matrix1_1, matrix2_1, metric='chebyshev')
            che2 = pairwise_distances(matrix1_2, matrix2_2, metric='chebyshev')
            canb1 = pairwise_distances(matrix1_1, matrix2_1, metric='canberra')
            canb1 = normalize(canb1, axis=0, norm='max')
            canb2 = pairwise_distances(matrix1_2, matrix2_2, metric='canberra')
            canb2 = normalize(canb2, axis=0, norm='max')
            cosine1 = []
            euclidean1 = []
            manhattan1 = []
            chebyshev1 = []
            canberra1 = []
            for i in range(len(cos1[0])):
                for m in range(len(cos1[1])):
                    cosine1.append(1 - cos1[i][m])
                    euclidean1.append(euc1[i][m])
                    # manhattan1.append(man1[i][m])
                    # chebyshev1.append(che1[i][m])
                    # canberra1.append(canb1[i][m])
            cosine2 = []
            euclidean2 = []
            manhattan2 = []
            chebyshev2 = []
            canberra2 = []
            for i in range(len(cos2[0])):
                for m in range(len(cos2[1])):
                    cosine2.append(1 - cos2[i][m])
                    euclidean2.append(euc2[i][m])
                    manhattan2.append(man2[i][m])
                    chebyshev2.append(che2[i][m])
                    canberra2.append(canb2[i][m])

            data = [f1, f2]
            data.extend(cosine1)
            data.extend(cosine2)
            data.extend(euclidean1)
            data.extend(euclidean2)
            data.extend(manhattan1)
            data.extend(manhattan2)
            data.extend(chebyshev1)
            data.extend(chebyshev2)
            data.extend(canberra1)
            data.extend(canberra2)

            co = [f1, f2]
            co.extend(cosine1)
            co.extend(cosine2)

            e = [f1, f2]
            e.extend(euclidean1)
            e.extend(euclidean2)

            m = [f1, f2]
            m.extend(manhattan1)
            m.extend(manhattan2)

            ch = [f1, f2]
            ch.extend(chebyshev1)
            ch.extend(chebyshev2)

            print(j)
            j += 1

            exc.append(data)
            Cos.append(co)
            E.append(e)
            M.append(m)
            C.append(ch)

    xx = exc
    print(len(exc[0]))

    with open(out + '_euc_dis.csv', 'w', newline='') as csvfile2:
        writer = csv.writer(csvfile2)
        for row in E:
            writer.writerow(row)


if __name__ == '__main__':
    get_similarity('./GCJ_clone.csv', './GCJ_clone')