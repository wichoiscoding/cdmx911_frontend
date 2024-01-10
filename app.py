from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# update with name and details
model = joblib.load('emergency_call_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    # get data with POST and convert to dataframe
    data = request.get_json(force=True)
    input_data = pd.DataFrame([data])


    # make and return prediction
    prediction = model.predict(input_data)
    return jsonify(prediction.tolist())

if __name__ == '__main__':
    app.run(debug=True)
