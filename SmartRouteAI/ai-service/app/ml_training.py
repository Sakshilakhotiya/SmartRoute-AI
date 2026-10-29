"""Train/evaluate a travel-time regressor from a real user-provided CSV.
Expected numeric columns: distance_km, hour, day_of_week, and target travel_time_min.
No synthetic dataset is generated and no trained model is bundled by default.
"""
import argparse, json
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from joblib import dump

def train(csv_path: str, output_path: str='models/travel_time.joblib'):
    df=pd.read_csv(csv_path)
    features=['distance_km','hour','day_of_week']; target='travel_time_min'
    missing=[c for c in features+[target] if c not in df.columns]
    if missing: raise ValueError('Dataset is missing required columns: '+', '.join(missing))
    df=df[features+[target]].dropna()
    if len(df)<20: raise ValueError('Provide at least 20 valid, real observations for a meaningful train/test split.')
    X_train,X_test,y_train,y_test=train_test_split(df[features],df[target],test_size=.2,random_state=42)
    model=RandomForestRegressor(n_estimators=200,random_state=42,min_samples_leaf=2,n_jobs=-1);model.fit(X_train,y_train)
    pred=model.predict(X_test); metrics={'rows':len(df),'test_rows':len(y_test),'mae_minutes':float(mean_absolute_error(y_test,pred)),'rmse_minutes':float(mean_squared_error(y_test,pred)**.5),'features':features,'target':target,'dataset':str(Path(csv_path).resolve())}
    out=Path(output_path);out.parent.mkdir(parents=True,exist_ok=True);dump(model,out);out.with_suffix('.metrics.json').write_text(json.dumps(metrics,indent=2));return metrics
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--output',default='models/travel_time.joblib');args=p.parse_args();print(json.dumps(train(args.csv,args.output),indent=2))
