from fastapi.testclient import TestClient
from app.main import app, normalize
client=TestClient(app)
def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'
def test_single_route_scores_100():
    r=client.post('/optimize/score',json={'routes':[{'distance_km':10,'duration_min':20}]})
    assert r.status_code==200; data=r.json(); assert data['recommended_index']==0; assert data['routes'][0]['score']==100
    assert data['routes'][0]['metrics']['accessibility_score'] is None
def test_multi_objective_prefers_shorter_for_shortest():
    r=client.post('/optimize/score',json={'preference':'shortest','routes':[{'distance_km':20,'duration_min':20},{'distance_km':10,'duration_min':35}]})
    assert r.status_code==200; assert r.json()['recommended_index']==1
def test_reject_invalid_route():
    r=client.post('/optimize/score',json={'routes':[{'distance_km':0,'duration_min':20}]}); assert r.status_code==422
def test_normalize_equal_values(): assert normalize([3,3])==[1.0,1.0]
