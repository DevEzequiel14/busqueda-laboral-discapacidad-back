from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


# Create your tests here.
class MatchTestCase(TestCase):

    @patch('core.views.get_offers')
    def test_valid_data_user(self):
        # Simulamos una petición POST con datos válidos para data_user
        data_user = {'some_key': 'some_value'}
        response = self.client.post(reverse('Match'), data=data_user)

        # Verificamos que la respuesta sea un código 200 OK
        self.assertEqual(response.status_code, 200)

        # Verificamos que los datos enviados en la respuesta coincidan con los datos recibidos
        self.assertDictEqual(response.json(), [{'similitud': 'some_value', 'oferta': 'some_offer'}])

    @patch('core.views.get_offers')
    def test_offers_from_get_offers(self, mock_get_offers):
        # Mockeamos la función get_offers para devolver datos de ejemplo
        mock_get_offers.return_value = [{'offer_key': 'offer_value'}]

        # Simulamos una petición POST
        response = self.client.post(reverse('Match'), data={})

        # Verificamos que la variable offers se haya llenado con datos retornados de get_offers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'similitud': 'offer_value', 'oferta': 'some_offer'}])

    @patch('core.views.get_offers')
    @patch('core.views.match_between_user_offers')
    @patch('core.views.convert_to_serializable')
    def test_match_post(self, mock_convert_to_serializable, mock_match_between_user_offers, mock_get_offers):
        # Mockeamos las funciones llamadas dentro de la vista para controlar su comportamiento
        mock_get_offers.return_value = [{'offer_key': 'offer_value'}]
        mock_match_between_user_offers.return_value = [{'similitud': 'similarity_value', 'oferta': 'some_offer'}]
        mock_convert_to_serializable.return_value = [{'similitud': 'similarity_value', 'oferta': 'some_offer'}]

        # Simulamos una petición POST
        response = self.client.post(reverse('Match'), data={})

        # Verificamos que la vista funcione correctamente
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'similitud': 'similarity_value', 'oferta': 'some_offer'}])
