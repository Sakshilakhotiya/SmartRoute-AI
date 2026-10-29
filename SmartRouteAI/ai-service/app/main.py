from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
import os, math, httpx
app=FastAPI(title="SmartRoute AI Optimization Service",version="1.0.0",description="Transparent multi-objective route scoring and cost estimation")
class Route(BaseModel):
    distance_km: float=Field(gt=0,le=50000)
    duration_min: float=Field(gt=0,le=100000)
    geometry: Optional[dict]=None
    source: Optional[str]=None
class Weights(BaseModel):
    time: float=Field(default=35,ge=0,le=100); distance: float=Field(default=25,ge=0,le=100); cost: float=Field(default=20,ge=0,le=100); accessibility: float=Field(default=10,ge=0,le=100); risk: float=Field(default=10,ge=0,le=100)
class ScoreRequest(BaseModel):
    routes:list[Route]=Field(min_length=1,max_length=10)
    vehicle:Literal['motorcycle','car','van','truck']='car'
    priority:Literal['standard','urgent','critical']='standard'
    preference:Literal['balanced','fastest','shortest','lowest_cost','safest']='balanced'
    fuel_efficiency_km_per_l:float=Field(default=15,gt=0,le=100)
    fuel_price_inr_per_l:float=Field(default=105,gt=0,le=1000)
    weights:Optional[Weights]=None
@app.get('/health')
def health(): return {'status':'ok','service':'smartroute-optimizer','ml_model':'not configured; training workflow available'}
def normalize(values, lower_is_better=True):
    lo,hi=min(values),max(values)
    if math.isclose(lo,hi): return [1.0]*len(values)
    return [((hi-v)/(hi-lo) if lower_is_better else (v-lo)/(hi-lo)) for v in values]
def route_cost(distance,efficiency,price): return (distance/efficiency)*price
@app.post('/optimize/score')
async def score(req:ScoreRequest):
    routes=req.routes
    if not routes: raise HTTPException(400,'At least one route is required')
    times=[r.duration_min for r in routes]; distances=[r.distance_km for r in routes]; costs=[route_cost(r.distance_km,req.fuel_efficiency_km_per_l,req.fuel_price_inr_per_l) for r in routes]
    tnorm=normalize(times); dnorm=normalize(distances); cnorm=normalize(costs)
    # No authoritative accessibility or incident dataset is bundled. Do not imply verified road suitability/safety.
    access=[0.5 for _ in routes]; risk=[0.5 for _ in routes]
    if req.weights:
        w=req.weights.model_dump()
    else: w={'time':35,'distance':25,'cost':20,'accessibility':10,'risk':10}
    if req.preference=='fastest': w={'time':80,'distance':10,'cost':5,'accessibility':3,'risk':2}
    elif req.preference=='shortest': w={'time':10,'distance':80,'cost':5,'accessibility':3,'risk':2}
    elif req.preference=='lowest_cost': w={'time':10,'distance':10,'cost':75,'accessibility':3,'risk':2}
    elif req.preference=='safest': w={'time':10,'distance':10,'cost':5,'accessibility':25,'risk':50}
    if req.priority=='urgent': w['time']*=1.5
    elif req.priority=='critical': w['time']*=2
    total=sum(w.values())
    if total<=0: raise HTTPException(400,'At least one optimization weight must be greater than zero')
    w={k:v/total for k,v in w.items()}
    results=[]
    for i,r in enumerate(routes):
        components={'time':tnorm[i],'distance':dnorm[i],'cost':cnorm[i],'accessibility':access[i],'risk':1-risk[i]}
        score_value=100*sum(w[k]*components[k] for k in w)
        km_l=r.distance_km/req.fuel_efficiency_km_per_l
        cost=costs[i]
        # A relative score, not a probability or safety certification.
        explain=[]
        if w['time']>=max(w['distance'],w['cost']): explain.append('travel time has the highest selected weight')
        elif w['distance']>=w['cost']: explain.append('distance is prioritized in your selected weights')
        else: explain.append('estimated fuel cost has the strongest practical influence')
        if i==0 and len(routes)==1: explain=['only one route alternative was returned by the provider']
        results.append({'distance_km':r.distance_km,'duration_min':r.duration_min,'geometry':r.geometry,'source':r.source or 'Routing provider','score':round(score_value,1),'metrics':{'estimated_fuel_l':round(km_l,2),'estimated_cost_inr':round(cost,2),'accessibility_score':None,'accessibility_label':'Unknown — road attribute data unavailable','risk_score':None,'risk_label':'Unverified — incident/risk data unavailable','score_components':{k:round(v*100,1) for k,v in components.items()},'normalized_weights':{k:round(v,3) for k,v in w.items()}},'explanation':f"This alternative is scored at {score_value:.0f}/100 because {explain[0]}. Accessibility and risk remain unknown without reliable supporting datasets."})
    idx=max(range(len(results)),key=lambda i:results[i]['score'])
    weather=None
    try:
        # Context-only weather at destination is supplied by API in a separate enhancement when coordinates are known.
        weather=None
    except Exception: pass
    warnings=['Public OSRM routing estimates do not represent verified live traffic.','Fuel cost is estimated from the configured fuel efficiency and fuel price.','Accessibility and risk are unknown because verified road attributes and incident data are not configured.','Scores are relative to the candidate routes returned for this request.']
    return {'routes':results,'recommended_index':idx,'explanation':f"Route {idx+1} is recommended because it has the highest normalized multi-objective score under your selected preferences. {results[idx]['explanation']}",'warnings':warnings,'weather':weather,'scoring_method':'weighted normalized utility score; lower time/distance/cost is better; accessibility/risk remain neutral and explicitly unknown without data'}
