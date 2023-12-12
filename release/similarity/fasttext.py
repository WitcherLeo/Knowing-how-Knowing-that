import sys
import time
import numpy as np
from gensim.models import KeyedVectors, FastText
from tool_models.sdgp_model.Sdgp.sdgp_tools.ltp4_complete import Ltp4
import torch


class FastTextTool(object):
    def __init__(self, vector_path=None, model_path=None):
        self.vector_path = vector_path
        self.model_path = model_path
        self.FASTTEXT = None
        if self.vector_path:
            t1 = time.time()
            self.FASTTEXT = KeyedVectors.load_word2vec_format(self.vector_path, binary=False)
            t2 = time.time()
            print('KeyedVectors 加载耗时：', t2 - t1)
        if self.model_path:
            t1 = time.time()
            self.FASTTEXT = FastText.load_fasttext_format(self.model_path).wv
            t2 = time.time()
            print('FastText 加载耗时：', t2 - t1, 's')
        self.ltp_tool = Ltp4()

    def find_longest_sub_token(self, token):
        for index in range(len(token), 0, -1):
            if token[:index] in self.FASTTEXT:
                return index
        return -1

    def token_seperate_for_OOV(self, token):
        tokens = []
        rest_token = token
        while len(rest_token) > 0:
            longest_sub_token_length = self.find_longest_sub_token(rest_token)
            if longest_sub_token_length == -1:
                break
            else:
                tokens.append(rest_token[:longest_sub_token_length])
                rest_token = rest_token[longest_sub_token_length:]
        if len(rest_token) > 0:
            print('OOV token 处理不了:', rest_token)
            sys.exit(1)

        return tokens

    def encode(self, text):
        analyse_out = self.ltp_tool.analyze(text)[0]
        words = analyse_out['words']
        word_vectors = []
        for word in words:
            if word in self.FASTTEXT:
                word_vectors.append(self.FASTTEXT[word])
            else:
                tokens = self.token_seperate_for_OOV(word)
                for token in tokens:
                    word_vectors.append(self.FASTTEXT[token])
        embedding = np.mean(word_vectors, axis=0)
        embedding = torch.tensor(embedding)
        return embedding

    def compute_similarity(self, text1, text2):
        embedding1 = self.encode(text1)
        embedding2 = self.encode(text2)
        similarity_score = torch.cosine_similarity(embedding1, embedding2, dim=0)

        return similarity_score


def test_some_samples():
    model_path = 'fasttext/cc/cc.zh.300.bin'
    fasttext = FastTextTool(vector_path=None, model_path=model_path)


if __name__ == '__main__':
    test_some_samples()
