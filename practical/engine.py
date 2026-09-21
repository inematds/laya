"""Typed support triage with explicit PT routing and conservative review policy."""
import json
import math
import threading
import time
from copy import deepcopy
from pathlib import Path

QUESTIONS = {
    'department': {'type': 'choice', 'instructions': 'Which department should handle this customer message?',
                   'criteria': {'billing': 'invoices, charges, payments, refunds',
                                'technical': 'bugs, outages, login errors, broken features',
                                'sales': 'pricing, new purchases, contracts, product demos',
                                'other': 'greetings, unrelated requests, insufficient information'}},
    'urgency': {'type': 'score', 'instructions': 'How urgent is the customer issue?',
                'criteria': ['normal request, no deadline', 'time-sensitive request', 'service blocked or immediate deadline']},
    'churn_risk': {'type': 'noul', 'instructions': 'Does the customer explicitly threaten to cancel or leave?'},
    'refund_requested': {'type': 'noul', 'instructions': 'Does the customer explicitly request money back?'}
}


def number(value, low=0, high=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Resposta contém número inválido ou fora da escala.')
    return float(value)


def review_policy(answers, threshold=.85):
    """No action execution: threshold is a triage signal, never authorization."""
    number(threshold)
    dep = answers['department']
    probs = dep['probabilities']
    if set(probs) != set(QUESTIONS['department']['criteria']):
        raise ValueError('Distribuição de departamentos incompleta.')
    for p in probs.values(): number(p)
    if abs(sum(probs.values()) - 1) > .002: raise ValueError('Probabilidades não somam 1.')
    if dep['choice'] not in probs or probs[dep['choice']] < max(probs.values()):
        raise ValueError('Departamento não corresponde à distribuição.')
    confidence = number(dep['confidence'])
    urgency = number(answers['urgency']['score'], 0, 2)
    churn = number(answers['churn_risk']['noul'])
    refund = number(answers['refund_requested']['noul'])
    reasons = ['Probabilidades ainda não validadas no seu domínio; revisão humana obrigatória.']
    if confidence < threshold: reasons.append('Confiança abaixo do limiar de triagem configurado.')
    if urgency >= 1.5: reasons.append('Possível urgência elevada.')
    if churn >= .5: reasons.append('Possível ameaça de cancelamento.')
    if refund >= .5: reasons.append('Pedido de reembolso exige conferência humana.')
    if dep['choice'] == 'other': reasons.append('Categoria residual; confirme o destino.')
    return {'destination': dep['choice'], 'needs_review': True,
            'action': 'human_review', 'automated_action_executed': False,
            'threshold': threshold, 'reasons': reasons}


class Engine:
    def __init__(self, device='cpu', threshold=.85, model_path=None):
        number(threshold)
        self.device, self.threshold, self.model_path = device, threshold, model_path
        self.router = None
        self.lock = threading.Lock()

    def _load(self):
        if self.router is None:
            from laya import Router
            models = {'multilingual': self.model_path} if self.model_path else None
            router = Router(device=self.device, models=models, max_loaded=1)
            router.preload(['multilingual'])
            self.router = router
        return self.router

    def predict(self, message, subject=''):
        if not isinstance(message, str) or not message.strip(): raise ValueError('Escreva uma mensagem.')
        if not isinstance(subject, str): raise ValueError('Assunto deve ser texto.')
        if len(message) > 12000 or len(subject) > 200: raise ValueError('Mensagem ou assunto excede o limite.')
        state = {'subject': subject.strip(), 'message': message.strip()}
        with self.lock:
            router = self._load()
            agent = router.load('multilingual')
            # Upstream silently truncates state: reject any loss before inference.
            from laya.common import build_sequence, serialize_state
            state_tokens = agent.tok(serialize_state(state).replace(agent.tok.mask_token, ' '), add_special_tokens=False)['input_ids']
            budget = min(agent.cfg.get('max_len', 1024) - len(build_sequence(
                agent.tok, '', agent._to_internal(q), agent.cfg.get('max_len', 1024),
                agent.cfg.get('head_max_len', 256))[0]) for q in QUESTIONS.values())
            if len(state_tokens) > budget:
                raise ValueError(f'Texto tem {len(state_tokens)} tokens; limite deste esquema: {budget}. Reduza o texto sem perder fatos relevantes.')
            started = time.perf_counter()
            result = router.predict(state, deepcopy(QUESTIONS), model='multilingual', lang='pt')
            elapsed = (time.perf_counter() - started) * 1000
            policy = review_policy(result['answers'], self.threshold)
            return {**result, 'policy': policy, 'runtime': {
                'inference_ms': round(elapsed, 2), 'device': str(agent.device),
                'state_tokens': len(state_tokens), 'state_token_budget': budget,
                'calibration': 'not_validated_for_customer_domain', 'simulation': False}}


def evaluate(engine, path):
    rows = [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
    if not rows: raise ValueError('Dataset vazio.')
    results, bins = [], [[] for _ in range(10)]
    labels = list(QUESTIONS['department']['criteria'])
    for row in rows:
        if row.get('expected_department') not in labels: raise ValueError('Rótulo inválido.')
        out = engine.predict(row['message'], row.get('subject', ''))
        a = out['answers']['department']; correct = a['choice'] == row['expected_department']
        top_p = a['probabilities'][a['choice']]
        bins[min(int(top_p * 10), 9)].append((top_p, int(correct)))
        brier = sum((a['probabilities'][k] - int(k == row['expected_department'])) ** 2 for k in labels)
        results.append({'id': row['id'], 'expected': row['expected_department'], 'predicted': a['choice'],
                        'correct': correct, 'brier': brier, 'result': out})
    n = len(rows)
    ece = sum(abs(sum(p for p,y in b)/len(b)-sum(y for p,y in b)/len(b))*len(b)/n for b in bins if b)
    return {'samples': n, 'accuracy': sum(r['correct'] for r in results)/n,
            'majority_baseline': max(sum(r['expected_department']==k for r in rows) for k in labels)/n,
            'brier_multiclass_sum': sum(r['brier'] for r in results)/n,
            'ece_top_probability_10_bins': ece, 'results': results,
            'limitations': 'Amostra didática pequena e sintética. Não é validação de produção nem calibração.'}
