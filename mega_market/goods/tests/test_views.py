import copy
import json
import urllib.parse

from django.test import TestCase, Client

E400 = {'status': 400, 'message': 'Validation Failed'}
E404 = {'status': 404, 'message': 'Item not found'}


class TestImports(TestCase):

    def setUp(self):
        self.guest_client = Client()

        self.date_ok = "2022-05-28T21:12:01.000Z"
        self.date_bad = "2022-05-12T21:"

        self.parent_category_uuid = "3fa85f64-5717-4562-b3fc-2c963f66a440"
        self.category_uuid = "3fa85f64-5717-4562-b3fc-2c963f66a441"
        self.offer_uuid = "3fa85f64-5717-4562-b3fc-2c963f66a445"

        self.offer = {
            "id": self.offer_uuid,
            "name": "Оффер",
            "price": 2,
            "type": "OFFER"
        }
        self.category = {
            "id": self.category_uuid,
            "name": "Категория",
            "price": None,
            "type": "CATEGORY"
        }
        self.parent_category = {
            "id": self.parent_category_uuid,
            "name": "Родительская категория",
            "price": None,
            "type": "CATEGORY"
        }
        self.child_offer = {
            "id": self.offer_uuid,
            "parentId": self.category_uuid,
            "name": "Оффер",
            "price": 2,
            "type": "OFFER"
        }

    def test_import_ok(self):
        data = {
            "items": [self.parent_category, self.category, self.child_offer],
            "updateDate": self.date_ok,
        }
        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_import_fail_bad_item_price(self):
        offer_bad_price = copy.deepcopy(self.offer)
        offer_bad_price['price'] = -1
        data = {
            "items": [offer_bad_price],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_bad_category_price(self):
        category_bad_price = copy.deepcopy(self.category)
        category_bad_price['price'] = 1
        data = {
            "items": [category_bad_price],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_bad_date(self):
        data = {
            "items": [self.offer],
            "updateDate": self.date_bad,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_item_type(self):
        offer_bad_type = copy.deepcopy(self.offer)
        offer_bad_type['type'] = "BAD_TYPE"
        data = {
            "items": [offer_bad_type],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_item_parent_id(self):
        offer_bad_parent_id = copy.deepcopy(self.offer)
        offer_bad_parent_id['parentId'] = "BAD_ID"
        data = {
            "items": [offer_bad_parent_id],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_item_parent_id_not_found(self):
        offer_bad_parent_id = copy.deepcopy(self.offer)
        offer_bad_parent_id['parentId'] = self.category_uuid
        data = {
            "items": [offer_bad_parent_id],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_item_parent_id_not_category(self):
        bad_category = copy.deepcopy(self.category)
        bad_category['type'] = "OFFER"
        data = {
            "items": [bad_category, self.child_offer],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_import_fail_duplicate_id(self):
        data = {
            "items": [self.offer, self.offer],
            "updateDate": self.date_ok,
        }

        response = self.client.post(
            '/imports/', json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class TestSales(TestCase):
    def test_sales(self):
        params = urllib.parse.urlencode({
            "date": "2022-02-04T00:00:00.000Z"
        })
        status, response = self.client.get(f"/sales?{params}",
                                           json_response=True)
        assert status == 200, f"Expected HTTP status code 200, got {status}"
        print("Test sales passed.")
