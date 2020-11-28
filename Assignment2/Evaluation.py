# Evaluation.
#  Transforms the query to improve retrieval.
#  @author Inês Justo, 84804
#  @author Daniel Marques, 85070

import math
import statistics


def getResults(file, queries, scores, start, end):
    # Get queries information (query_id, cord_ui, relevance)
    f = open(file, "r")
    lines = f.read().splitlines()
    f.close()

    # Add document ID to its relevance dictionary
    #       |     0     |    1    |      2    |
    #       | query ID  |  doc ID | relevance |

    relevance_1 = dict()
    relevance_2 = dict()
    # Fill dict with query number
    for idx in range(1, len(queries)):
        relevance_1[idx] = dict()
        relevance_2[idx] = dict()
    for line in lines:
        column = line.split(' ')
        # If query relevance = 1 then add document ID to relevance_1 dict
        if column[2] == '1':
            relevance_1[int(column[0]) - 1][column[1]] = 0
        # If query relevance = 2 then add document ID to relevance_2 dict
        elif column[2] == '2':
            relevance_2[int(column[0]) - 1][column[1]] = 0

    # Time calculation
    time = [end[i] - start[i] for i in range(0, len(start))]

    # Metrics Calculation
    precision10, recall10, f_measure10, avg_precision10, ndcgain10 = getCalculation(relevance_1, relevance_2, scores,
                                                                                    queries, 10)  # Top 10
    precision20, recall20, f_measure20, avg_precision20, ndcgain20 = getCalculation(relevance_1, relevance_2, scores,
                                                                                    queries, 20)  # Top 20
    precision50, recall50, f_measure50, avg_precision50, ndcgain50 = getCalculation(relevance_1, relevance_2, scores,
                                                                                    queries, 50)  # Top 50

    # Print header
    dash = '-' * 168
    print(dash)
    print('|        Precision          |          Recall           |        F-measure          |     Average '
          'Precision     |           NDCG            |      Latency\nQuery # |  @10      @20      @50    |  @10      '
          '@20      @50    |  @10      @20      @50    |  @10      @20      @50    |  @10      @20      @50    | ')
    print(dash)

    # Print Calculations
    for idx, query in enumerate(queries):
        print('\n{:2.0f}    #'
              '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
              '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
              '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
              '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
              '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
              '    {:-10.2f}'.format(50,
                                     (precision10[idx] * 100), (precision20[idx] * 100), (precision50[idx] * 100),
                                     (recall10[idx] * 100), (recall20[idx] * 100), (recall50[idx] * 100),
                                     (f_measure10[idx] * 100), (f_measure20[idx] * 100), (f_measure50[idx] * 100),
                                     (avg_precision10[idx] * 100), (avg_precision20[idx] * 100),
                                     (avg_precision50[idx] * 100),
                                     (ndcgain10[idx] * 100), (ndcgain20[idx] * 100), (ndcgain50[idx] * 100),
                                     time[idx] * 1000))

    # Print Mean
    print('\nMean'
          '    {:-9.2f}   {:-6.2f}   {:-6.2f}'
          '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
          '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
          '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
          '    {:-6.2f}   {:-6.2f}   {:-6.2f}'
          '    {:-10.2f}'.format(50,
                                 (statistics.mean(precision10) * 100), (statistics.mean(precision20) * 100),
                                 (statistics.mean(precision50) * 100),
                                 (statistics.mean(recall10) * 100), (statistics.mean(recall20) * 100),
                                 (statistics.mean(recall50) * 100),
                                 (statistics.mean(f_measure10) * 100), (statistics.mean(f_measure20) * 100),
                                 (statistics.mean(f_measure50) * 100),
                                 (statistics.mean(avg_precision10) * 100), (statistics.mean(avg_precision20) * 100),
                                 (statistics.mean(avg_precision50) * 100),
                                 (statistics.mean(ndcgain10) * 100), (statistics.mean(ndcgain20) * 100),
                                 (statistics.mean(ndcgain50) * 100),
                                 (statistics.median(time) * 1000)))

    # Print Query Throughput
    print('\nQuery Throughput: {:-6.2f} Queries'.format(1 / (sum(time) / 50)))


def getCalculation(relevance_1, relevance_2, scores, queries, top):
    # Initialization
    precision = []
    recall = []
    f_measure = []
    avg_precision = []
    ndcgain = []

    for num, query in enumerate(queries):

        # High Scores List (top 10, top 20 or top 50)
        highScores = list(scores[num].keys())[:top]

        # For this query, the number of relevant documents
        relevant_docs_total = len(relevance_1[num]) + len(relevance_2[num])

        # Relevant and non relevant document counter in high scores (for metrics)
        relevant_scores = 0
        non_relevant_scores = 0
        mean = 0
        for doc in range(0, top):
            # If document ID is in relevance dictionaries
            if highScores[doc] in relevance_1[num] or highScores[doc] in relevance_2[num]:
                relevant_scores += 1
                mean += relevant_scores / (relevant_scores + non_relevant_scores)
            # If document ID isn't in relevance dictionaries (relevance = 0)
            else:
                non_relevant_scores += 1

        # Relevant document number not in high scores
        relevant_docs_left = relevant_docs_total - relevant_docs_scores

        # __________ METRICS __________

        # PRECISION
        if non_relevant_scores != 0 or relevant_scores != 0:
            precision.append(relevant_scores / (relevant_scores + non_relevant_scores))
        else:
            precision.append(0)

        # RECALL
        if relevant_docs_left != 0 or relevant_scores != 0:
            recall.append(relevant_scores / (relevant_scores + relevant_docs_left))
        else:
            recall.append(0)

        # F-MEASURE
        beta = 1  # beta
        if recall[num] != 0 or precision[num] != 0:
            f_measure.append(
                ((pow(beta, 2) + 1) * recall[num] * precision[num]) / (recall[num] + (pow(beta, 2) * precision[num])))
        else:
            f_measure.append(0)

        # AVERAGE PRECISION
        if relevant_scores != 0:
            avg_precision.append(mean / relevant_scores)
        else:
            avg_precision.append(0)

        # NORMALIZED DISCOUNTED CUMULATIVE GAIN
        rel = []  # graded relevance of the result
        for doc in range(0, top):
            if highScores[doc] in relevance_1[num]:
                rel.append(1)
            elif highScores[doc] in relevance_2[num]:
                rel.append(2)
            else:
                rel.append(0)

        rel_i = sorted(rel, reverse=True)  # Sort Rel list (descending order)

        dcg = rel[0]  # discounted cumulative gain
        idcg = rel_i[0]  # ideal discounted cumulative gain

        for i in range(1, top):  # Formulation
            dcg += rel[i] / math.log(i + 1, 2)
            idcg += rel_i[i] / math.log(i + 1, 2)

        if idcg != 0:
            ndcgain.append(dcg / idcg)
        else:
            ndcgain.append(0)

    return precision, recall, f_measure, avg_precision, ndcgain
