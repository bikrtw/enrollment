import json
import urllib.parse

from django.test import TestCase, Client

from ..models import ShopUnit


class TestUrls(TestCase):
    def setUp(self):
        self.client = Client()

        self.date_ok = "2022-05-28T21:12:01.000Z"
        self.offer_uuid = "3fa85f64-5717-4562-b3fc-2c963f66a445"
        self.offer = {
            "id": self.offer_uuid,
            "name": "Оффер",
            "price": 2,
            "type": "OFFER"
        }

    def test_imports(self):
        data = {
            "items": [self.offer],
            "updateDate": self.date_ok,
        }
        response = self.client.post(
            '/imports',
            data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        obj = ShopUnit.objects.create(**self.offer, date=self.date_ok)
        obj.save()

        response = self.client.delete(f"/delete/{self.offer_uuid}")
        self.assertEqual(response.status_code, 200)

    def test_nodes(self):
        obj = ShopUnit.objects.create(**self.offer, date=self.date_ok)
        obj.save()

        response = self.client.get(f"/nodes/{self.offer_uuid}",
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_sales(self):
        params = urllib.parse.urlencode({
            "date": "2022-02-04T00:00:00.000Z"
        })
        response = self.client.get(f"/sales?{params}",
                                   json_response=True)
        self.assertEqual(response.status_code, 200)

    def test_statistic(self):
        obj = ShopUnit.objects.create(**self.offer, date=self.date_ok)
        obj.save()

        response = self.client.get(f"/node/{self.offer_uuid}/statistic",
                                   json_response=True)
        self.assertEqual(response.status_code, 200)
