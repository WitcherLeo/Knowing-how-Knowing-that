import tqdm
import util_box

from metrics.bleu_metrics import BleuMetric
from model.graph_match.GraphMatchBased import GraphMatchQA


def load_model(model_name, graph_data, sp_entities):
    if model_name == 'TARA':
        return GraphMatchQA(False, graph_data, sp_entities, parsing_model='Sdgp')


def run_single_baseline(qa_data, qa_class, metric_class, recall_constraint):
    metric_class.clear()

    t = tqdm.tqdm(range(len(qa_data)))
    for qa_pair in qa_data:
        t.update(1)
        document_id = int(qa_pair['document_id'])
        question = qa_pair['question']
        answers_label = qa_pair['answers']
        answers_prediction, question_type, _ = qa_class.single_predict(question, document_id=document_id,
                                                                       debug=False, show_parsing=False,
                                                                       show_reasoning_path=False,
                                                                       match_score_threshold=0)
        # Recall@n
        if recall_constraint > 0 and type(recall_constraint) == int:
            answers_prediction = answers_prediction[:recall_constraint]
        metric_class.update(answers_label, answers_prediction)

    precision, recall, f1 = metric_class.get_final_score()

    if recall_constraint > 0 and type(recall_constraint) == int:
        print('\n\nRecall@%d' % recall_constraint)

    print('\n')
    print('Precision:', precision)
    print('Recall:', recall)
    print('F1:', f1)

    return precision, recall, f1


def eva_single_with_model(qa_class, qa_data, recall_constraint, metric_class):
    print('当前评价指标:', metric_class.__name__)
    precision, recall, f1 = run_single_baseline(qa_data, qa_class, metric_class, recall_constraint)
    return precision, recall, f1


def eva_single(model_name, qa_data, graph_data, sp_entities, recall_constraint, metric_class):
    print('当前预测模型:', model_name)
    print('当前评价指标:', metric_class.__name__)
    print('开始评估:', model_name, '...')
    qa_class = load_model(model_name, graph_data, sp_entities)
    precision, recall, f1 = run_single_baseline(qa_data, qa_class, metric_class, recall_constraint)
    print(model_name, ':评估结束')
    return precision, recall, f1


def main(recall_constraint):
    graph_data_path = 'Sdgp.json'
    qa_data_path = 'test_dataset.json'
    sp_entities_file_path = 'entities_extraction_no_fre.txt'

    graph_data = util_box.read_json(graph_data_path)
    qa_data = util_box.read_json(qa_data_path)

    sp_entities = util_box.read_txt(sp_entities_file_path).split('\n')

    metric_class = BleuMetric()

    model_name = 'TARA'

    eva_single(model_name, qa_data, graph_data, sp_entities, recall_constraint, metric_class)


if __name__ == '__main__':
    # @recall
    recall_constraint_num = int(-1)
    main(recall_constraint_num)
