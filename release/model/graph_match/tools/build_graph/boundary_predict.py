
def sample_type_jungle(sample_extraction):
    list_of_action_terms = ['用户', '参与者']
    subject = sample_extraction['subject']
    object_text = sample_extraction['object']
    for action_term in list_of_action_terms:
        if action_term in subject or action_term in object_text:
            return 'action'
    return 'attr'


def get_boundary_labels(samples_extraction_results):
    last_sentence = ''

    links = []
    current_link = []
    attrs = []
    for sample_extraction_result in samples_extraction_results:
        text_type = sample_extraction_result['label']['text_type']
        if text_type == 'attribute':
            attrs.append(sample_extraction_result)
            continue
        if sample_extraction_result['sentence'] == last_sentence:
            current_link.append(sample_extraction_result)
            continue
        if len(current_link) > 0:
            links.append(current_link)
        current_link = [sample_extraction_result]
        last_sentence = sample_extraction_result['sentence']
    if len(current_link) > 0:
        links.append(current_link)
    return links, attrs


def get_boundaries(samples_extraction_results_per_document):
    documents_data_wo_dup = []
    for document_data in samples_extraction_results_per_document:
        document_id = document_data['document_id']
        question = document_data['question']
        samples_extraction_results = document_data['samples_extraction_results']
        samples_extraction_results_wo_dup = []
        sentences_this_document = []
        for sample_extraction_result in samples_extraction_results:
            sentence = sample_extraction_result['sentence']
            if len(samples_extraction_results_wo_dup) == 0:
                for sample_extracted in sample_extraction_result['label']:
                    samples_extraction_results_wo_dup.append({
                        'sentence': sentence,
                        'label': sample_extracted
                    })
                sentences_this_document.append(sentence)
                continue
            if sentence in sentences_this_document:
                continue
            for sample_extracted in sample_extraction_result['label']:
                samples_extraction_results_wo_dup.append({
                    'sentence': sentence,
                    'label': sample_extracted
                })
            sentences_this_document.append(sentence)
        documents_data_wo_dup.append({
            'document_id': document_id,
            'question': question,
            'samples_extraction_results': samples_extraction_results_wo_dup,
            'source_sentences': document_data['source_sentences']
        })

    samples_with_boundary_labels_per_document = []
    for document_data in documents_data_wo_dup:
        document_id = document_data['document_id']
        question = document_data['question']
        samples_extraction_results = document_data['samples_extraction_results']
        links, attrs = get_boundary_labels(samples_extraction_results)
        samples_with_boundary_labels_per_document.append({
            'document_id': document_id,
            'question': question,
            'graph_prediction': {
                'links': links,
                'attrs': attrs
            },
            'source_sentences': document_data['source_sentences']
        })

    return samples_with_boundary_labels_per_document
