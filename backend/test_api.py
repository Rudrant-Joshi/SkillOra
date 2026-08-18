import urllib.request, json, sys

def api(method, path, data=None, token=None):
    url = f'http://127.0.0.1:8001{path}'
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if data is not None:
        data = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return f'HTTP {e.code}: {body}'

# 1. Login as candidate
resp = api('POST', '/api/auth/login', {'email': 'candidate@skillgraph.dev', 'password': 'candidate123'})
if isinstance(resp, str):
    print(f'Login failed: {resp}')
    sys.exit(1)
token = resp['access_token']
print(f'Login OK: role={resp["role"]}, user_id={resp["user_id"]}')

# 2. List assessments
assessments = api('GET', '/api/assessments/', token=token)
if isinstance(assessments, str):
    print(f'Assessments error: {assessments}')
    sys.exit(1)
print(f'\nAssessments ({len(assessments)}):')
for a in assessments:
    print(f'  {a["id"]}: {a["title"]} - skills={a["skills"]} - adaptive={a["is_adaptive"]}')

# 3. Start an assessment
a_id = assessments[0]['id']
attempts = api('POST', f'/api/assessments/{a_id}/start', token=token)
print(f'\nStart assessment {a_id}: attempt_id={attempts["attempt_id"]}, duration={attempts["duration_minutes"]}min')

# 4. Get questions
questions = api('GET', f'/api/assessments/{a_id}/questions?attempt_id={attempts["attempt_id"]}', token=token)
if isinstance(questions, str):
    print(f'Questions error: {questions}')
    sys.exit(1)
print(f'\nQuestions ({len(questions["questions"])}):')
for q in questions['questions']:
    print(f'  Q{q["id"]}: [{q["question_type"]}] {q["prompt"][:60]}... skills={q["skills"]} diff={q["difficulty"]}')

# 5. Submit answers (auto-answer based on options)
answers = []
for q in questions['questions']:
    if q['question_type'] == 'mcq':
        # Try to guess the right answer by picking index 1 for known MCQs
        answers.append({
            'question_id': q['id'],
            'question_type': q['question_type'],
            'submitted_options': [1],  # just submit something
            'submitted_code': '',
            'submitted_answer': '',
            'test_results': [],
            'time_limit_exceeded': False,
            'memory_limit_exceeded': False,
            'compiled': True,
            'time_spent_seconds': 30.0,
        })
    elif q['question_type'] in ('coding', 'sql'):
        answers.append({
            'question_id': q['id'],
            'question_type': q['question_type'],
            'submitted_options': [],
            'submitted_code': q.get('starter_code', ''),
            'submitted_answer': '',
            'test_results': [{'name': 'test1', 'passed': True, 'hidden': False}, {'name': 'test2', 'passed': True, 'hidden': True}],
            'time_limit_exceeded': False,
            'memory_limit_exceeded': False,
            'compiled': True,
            'time_spent_seconds': 300.0,
        })
    elif q['question_type'] == 'short_answer':
        answers.append({
            'question_id': q['id'],
            'question_type': q['question_type'],
            'submitted_options': [],
            'submitted_code': '',
            'submitted_answer': 'INNER JOIN returns only matching rows while LEFT JOIN returns all rows from the left table.',
            'test_results': [],
            'time_limit_exceeded': False,
            'memory_limit_exceeded': False,
            'compiled': True,
            'time_spent_seconds': 60.0,
        })

result = api('POST', f'/api/attempts/{attempts["attempt_id"]}/submit', {'answers': answers}, token=token)
if isinstance(result, str):
    print(f'\nSubmit error: {result}')
    sys.exit(1)

print(f'\n=== Result ===')
print(f'Overall score: {result["overall_score"]}')
print(f'Raw score: {result["raw_score"]}')
print(f'ML score: {result["ml_score"]}')
print(f'Questions scored: {result["questions_count"]}')
print(f'Dimension scores: {result["dimension_scores"]}')
print(f'Skills:')
for skill, data in result["skills"].items():
    print(f'  {skill}: level={data["level"]:.4f}, confidence={data["confidence"]:.4f}, evidence={data["evidence_count"]}')
print(f'\nEvidence: {result["evidence"]}')
