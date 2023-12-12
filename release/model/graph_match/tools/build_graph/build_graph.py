import json
import sys
from tqdm import tqdm

from tool_models.sdgp_model.Sdgp.sdgp_tools.ltp4_complete import Ltp4
from tool_models.sdgp_model.Sdgp.solution import SdgpSolution
from boundary_predict import get_boundaries
from samples2graph import construct_graph


def save_extraction_result(extraction_result, output_dir, model_name, boundary_strategy):
    output_file_path = output_dir + str(
        boundary_strategy) + '/' + model_name + '/' + model_name + '.json'
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(extraction_result, f, ensure_ascii=False)
        print('save extraction result to:', output_file_path)


def load_model(model_name, boundary_strategy):
    if model_name == 'Sdgp':
        return True, SdgpSolution(boundary_strategy)
    return False, None


def read_sp_entities(sp_entities_file):
    with open(sp_entities_file, 'r', encoding='utf-8') as f:
        entities = f.read().split('\n')
    return entities


def extraction_framework(read_data_path, sp_entities_path, extraction_save_results_dir,
                         save_extraction=False):
    with open(read_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sp_entities = read_sp_entities(sp_entities_path)
    ltp_tool = Ltp4()
    samples_extraction_results_per_document = []

    boundary_strategy = 'kh'
    load_success, model = load_model('Sdgp', boundary_strategy)
    if not load_success:
        sys.exit()

    t = tqdm(total=len(data))
    t.set_description('抽取进度：')
    for document_data in data:
        document_id = document_data['document_id']
        source_sentences = ltp_tool.sent_split_ltp(document_data['document_text'])
        samples_extraction_results_this_document = model.predicts(source_sentences)

        predictions_this_document = {
            'document_id': document_id,
            'samples_extraction_results': samples_extraction_results_this_document,
            'source_sentences': source_sentences,
            'question': document_data['question'],
        }
        samples_extraction_results_per_document.append(predictions_this_document)
        t.update(1)

    samples_with_boundary_labels_per_document = get_boundaries(samples_extraction_results_per_document)
    graph_data_all_documents = construct_graph(samples_with_boundary_labels_per_document, sp_entities, ltp_tool)

    if save_extraction:
        save_extraction_result(graph_data_all_documents, extraction_save_results_dir, 'Sdgp',
                               boundary_strategy)


if __name__ == '__main__':
    dataset_path = 'test_dataset.json'
    sp_entities_file_path = 'entities_extraction_no_fre.txt'

    save_model_extraction_results_dir = '/'

    extraction_framework(dataset_path, sp_entities_file_path, save_model_extraction_results_dir,
                         save_extraction=False)
