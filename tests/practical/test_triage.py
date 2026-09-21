import copy
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from practical.engine import review_policy, Engine
from practical.server import create_app


def answers():
    return {'department': {'choice':'billing','confidence':.9,'probabilities':{'billing':.9,'technical':.04,'sales':.03,'other':.03}},
            'urgency':{'score':1.8}, 'churn_risk':{'noul':.9}, 'refund_requested':{'noul':.95}}

class PolicyTests(unittest.TestCase):
    def test_high_confidence_never_authorizes_money(self):
        p=review_policy(answers());self.assertTrue(p['needs_review']);self.assertFalse(p['automated_action_executed']);self.assertEqual(p['action'],'human_review')
    def test_low_confidence_reason(self):
        a=answers();a['department']['confidence']=.2
        self.assertTrue(any('limiar' in r for r in review_policy(a)['reasons']))
    def test_invalid_distribution(self):
        a=answers();a['department']['probabilities']['billing']=.1
        with self.assertRaises(ValueError):review_policy(a)
    def test_nonfinite_rejected(self):
        a=answers();a['churn_risk']['noul']=float('nan')
        with self.assertRaises(ValueError):review_policy(a)
    def test_invalid_choice(self):
        a=answers();a['department']['choice']='sales'
        with self.assertRaises(ValueError):review_policy(a)
    def test_threshold_bounds(self):
        with self.assertRaises(ValueError):Engine(threshold=2)
    def test_empty_input_before_loading(self):
        e=Engine()
        with self.assertRaises(ValueError):e.predict('  ')
        self.assertIsNone(e.router)
    def test_size_before_loading(self):
        with self.assertRaises(ValueError):Engine().predict('a'*12001)
    def test_policy_does_not_mutate_model_output(self):
        a=answers();original=copy.deepcopy(a);review_policy(a);self.assertEqual(a,original)

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.engine=MagicMock();self.engine.router=None
        self.client=TestClient(create_app(self.engine))
    def test_health_no_model_load(self):
        r=self.client.get('/api/health');self.assertFalse(r.json()['model_loaded']);self.engine.predict.assert_not_called()
    def test_validation(self):
        for body in [{'message':''},{'message':'x','threshold':0},{'message':'x'*12001}]:
            self.assertEqual(self.client.post('/api/triage',json=body).status_code,422)
        self.engine.predict.assert_not_called()
    def test_engine_failure_visible(self):
        self.engine.predict.side_effect=RuntimeError('download unavailable')
        self.assertEqual(self.client.post('/api/triage',json={'message':'Teste'}).status_code,503)
    def test_token_limit_is_422(self):
        self.engine.predict.side_effect=ValueError('Texto excede tokens')
        self.assertEqual(self.client.post('/api/triage',json={'message':'Teste'}).status_code,422)
    def test_result_is_engine_result(self):
        self.engine.predict.return_value={'answers':answers(),'policy':review_policy(answers())}
        data=self.client.post('/api/triage',json={'message':'Cobrança'}).json()
        self.assertTrue(data['policy']['needs_review']);self.engine.predict.assert_called_once_with('Cobrança','')

if __name__=='__main__':unittest.main()
