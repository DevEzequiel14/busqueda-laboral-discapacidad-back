from django.forms import model_to_dict
from rest_framework.views import APIView
from django.http import HttpResponse
from .load_data import load_data
from .models import JobOffer, Responsibility, Requirement, Availability, Category, Mode
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import json
import numpy as np
tokenizer = BertTokenizer.from_pretrained('dccuchile/bert-base-spanish-wwm-uncased')
model = BertModel.from_pretrained('dccuchile/bert-base-spanish-wwm-uncased')


# Create your views here.
class Ping(APIView):
    """
    Test API Connection

    Return a text if the connection was successfully
    """

    def get(self, request):
        return HttpResponse(content="pong", status=200)


class TestExtract(APIView):

    def get(self, request):
        load_data()
        return HttpResponse(content='extract', status=200)


class Match(APIView):

    def post(self, request):
        body = request.body.decode('utf-8')
        data_user = json.loads(body)
        offers = get_offers()
        results = match_between_user_offers(offers, data_user)
        results_serializable = convert_to_serializable(results)
        data = [{'similitud': oferta['similitud'], 'oferta': (oferta['oferta'])} for oferta in results_serializable]
        return HttpResponse(json.dumps(data), status=200, content_type='application/json')


class TestAnalysisBd(APIView):

    def get(self, request):
        offers = get_offers()
        return HttpResponse(json.dumps(offers), status=200, content_type='application/json')


class TestFrontAnalysis(APIView):

    def post(self, request):
        body = request.body.decode('utf-8')
        data_user = json.loads(body)
        print(data_user)
        return HttpResponse(json.dumps(data_user), status=200, content_type='application/json')


def get_offers():
    offers = [model_to_dict(off) for off in JobOffer.objects.all()]
    for offer in offers:
        offer['tasks'] = list(Responsibility.objects.filter(job_offer_id=offer['id']).values_list('description',
                                                                                                  flat=True))
        offer['requirements'] = list(Requirement.objects.filter(job_offer_id=offer['id']).values_list('description',
                                                                                                      flat=True))
        offer['availability'] = list(Availability.objects.filter(job_offer_id=offer['id']).values_list('description',
                                                                                                       flat=True))
        offer['modality'] = Mode.objects.get(id=offer['mode']).name
        offer['category_name'] = Category.objects.get(id=offer['category']).name
    return offers


def match_between_user_offers(offers, user, affinity=0.62):
    results = []
    for offer in offers:
        similarity = calculate_similarity(offer, user, tokenizer, model)
        if similarity > affinity:
            results.append({'similitud': similarity, 'oferta': offer})
    sorted_results = sorted(results, key=lambda x: x['similitud'], reverse=True)
    return sorted_results


def calculate_similarity(offer, user, tokenizer, model):
    text_offer = " ".join([offer['description'], *offer['requirements'], *offer['tasks'], offer['category_name']])
    text_user = " ".join(user['experiences'] + user['skills'])
    if 'education' in user:
        text_user += " ".join([educacion['titulo'] for educacion in user['education']])
    if 'languages' in user:
        text_user += " ".join([languages['language'] for languages in user['languages']])
    inputs_offer = tokenizer(text_offer, return_tensors="pt", padding=True, truncation=True)
    inputs_user = tokenizer(text_user, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs_offer = model(**inputs_offer)
        outputs_user = model(**inputs_user)
    similarity_score = cosine_similarity(outputs_offer.last_hidden_state.mean(dim=1),
                                         outputs_user.last_hidden_state.mean(dim=1))
    return similarity_score[0][0]


def convert_to_serializable(element):
    if isinstance(element, np.float32):
        return float(element)
    elif isinstance(element, (list, tuple)):
        return [convert_to_serializable(item) for item in element]
    elif isinstance(element, dict):
        return {key: convert_to_serializable(value) for key, value in element.items()}
    else:
        return element