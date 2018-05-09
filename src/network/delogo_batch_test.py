import file_opr
from sklearn.metrics import precision_recall_fscore_support as score

def demo():
    predicted = [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0]
    y_test = [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1]

    precision, recall, fscore, support = score(y_test, predicted)

    print('precision: {}'.format(precision))
    print('recall: {}'.format(recall))
    print('fscore: {}'.format(fscore))
    print('support: {}'.format(support))

# load test result and labeled real result
def batch_test(test_result_path, real_result_path):
    test_result_files, tfn = file_opr.eachFile(test_result_path, ".json")
    real_result_files, rfn = file_opr.eachFile(test_result_path, ".txt")

    #calculate correct cover rate only for succecc detected logo
    metric_average_cover_rate_f = 0
    metric_average_cover_rate_b = 0

    y_true = []
    y_predict = []
    for test in test_result_files:
        #load test result
        delogo_res = file_opr.get_delogo_info_from_logfile(test)
        print delogo_res

        #load real result

        #cmp


    precision, recall, fscore, support = score(y_true, y_predict)

    print('precision: {}'.format(precision))
    print('recall: {}'.format(recall))
    print('fscore: {}'.format(fscore))
    print('support: {}'.format(support))

    pass


if __name__ == '__main__':
    #demo()
    true_res_path = "/Users/liuwen/Development/test/trans_lab/unique_output1000_1_true/"
    test_res_path = "/Users/liuwen/Development/test/trans_lab/unique_output1000_1/"
    batch_test(test_result_path, true_res_path)