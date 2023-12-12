import math
from nltk.translate.bleu_score import sentence_bleu

from tool_models.sdgp_model.Sdgp.sdgp_tools.ltp4_complete import Ltp4


def compute_bleu_score_single(answers_label, answer_prediction):
    # 1-gram
    bleu_1 = sentence_bleu(answers_label, answer_prediction, weights=(1, 0, 0, 0))
    bleu_1 = 0 if bleu_1 < math.exp(-10) else bleu_1
    # 2-gram
    bleu_2 = sentence_bleu(answers_label, answer_prediction, weights=(0, 1, 0, 0))
    bleu_2 = 0 if bleu_2 < math.exp(-10) else bleu_2
    # 3-gram
    bleu_3 = sentence_bleu(answers_label, answer_prediction, weights=(0, 0, 1, 0))
    bleu_3 = 0 if bleu_3 < math.exp(-10) else bleu_3
    # 4-gram
    bleu_4 = sentence_bleu(answers_label, answer_prediction, weights=(0, 0, 0, 1))
    bleu_4 = 0 if bleu_4 < math.exp(-10) else bleu_4

    bleu_score = (bleu_1 + bleu_2 + bleu_3 + bleu_4) / 4
    return bleu_score


class BleuMetric(object):
    def __init__(self):
        self.__name__ = 'BleuMetric'

        self.precision_total_score = 0
        self.recall_total_score = 0
        self.precision_total_num = 0
        self.recall_total_num = 0

        self.ltp_tool = Ltp4()

    def clear(self):
        self.precision_total_score = 0
        self.recall_total_score = 0
        self.precision_total_num = 0
        self.recall_total_num = 0

    def update(self, answers_label, answers_prediction):
        # tokenize
        answers_label = [self.ltp_tool.analyze(item)['words'] for item in answers_label]
        answers_prediction = [self.ltp_tool.analyze(item)['words'] for item in answers_prediction]

        for answer_prediction in answers_prediction:
            score_this_prediction = compute_bleu_score_single(answers_label, answer_prediction)
            self.precision_total_score += score_this_prediction
            self.precision_total_num += 1
        for answer_label in answers_label:
            if len(answers_prediction) > 0:
                score_this_label = compute_bleu_score_single(answers_prediction, answer_label)
            else:
                score_this_label = 0
            self.recall_total_score += score_this_label
            self.recall_total_num += 1

    def get_final_score(self, round_num=4):
        precision = self.precision_total_score / self.precision_total_num if self.precision_total_num > 0 else 0
        recall = self.recall_total_score / self.recall_total_num if self.recall_total_num > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
        return round(precision, round_num), round(recall, round_num), round(f1, round_num)


if __name__ == '__main__':
    pass
