from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the data from your files
pincode_data = pd.read_csv('Pincodes List.csv')  # Adjust the file name if needed
rates_data = pd.read_excel('Go Fast Logistics Commercial.xlsx')

@app.route('/check_rates', methods=['POST'])
def check_rates():
    data = request.json
    origin_pincode = data.get('origin_pincode')
    destination_pincode = data.get('destination_pincode')
    service_type = data.get('service_type')

    # Find origin and destination city/state based on pincodes
    origin = pincode_data[pincode_data['Pincode'] == int(origin_pincode)].squeeze()
    destination = pincode_data[pincode_data['Pincode'] == int(destination_pincode)].squeeze()

    if origin.empty or destination.empty:
        return jsonify({"error": "No service available for the entered pincodes"}), 404

    zone = 'Zone E'  # Example logic; adjust this to match your rate calculations
    rate = rates_data[(rates_data['Zone'] == zone) & (rates_data['Service'] == service_type)]['Rate'].values[0]

    return jsonify({
        "origin_city": origin['City'],
        "destination_city": destination['City'],
        "zone": zone,
        "rate": rate
    })

if __name__ == '__main__':
    app.run(debug=True)
