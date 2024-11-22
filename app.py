from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the data from your files
try:
    pincode_data = pd.read_csv('Pincodes List.csv')  # Adjust the file name if needed
    rates_data = pd.read_excel('Go Fast Logistics Commercial.xlsx')
except Exception as e:
    print(f"Error loading data: {e}")
    pincode_data = pd.DataFrame()  # Empty DataFrame for safety
    rates_data = pd.DataFrame()

# Root route for health check
@app.route('/')
def home():
    return "GoFastLogistics API is working!"

# Endpoint to check rates
@app.route('/check_rates', methods=['POST'])
def check_rates():
    try:
        data = request.json
        origin_pincode = data.get('origin_pincode')
        destination_pincode = data.get('destination_pincode')
        service_type = data.get('service_type')

        # Validate input
        if not all([origin_pincode, destination_pincode, service_type]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Find origin and destination city/state based on pincodes
        origin = pincode_data[pincode_data['Pincode'] == int(origin_pincode)].squeeze()
        destination = pincode_data[pincode_data['Pincode'] == int(destination_pincode)].squeeze()

        if origin.empty or destination.empty:
            return jsonify({"error": "No service available for the entered pincodes"}), 404

        # Logic to determine zone and rate
        zone = 'Zone E'  # Example logic; adjust this to match your rate calculations
        matching_rate = rates_data[
            (rates_data['Zone'] == zone) & (rates_data['Service'] == service_type)
        ]

        if matching_rate.empty:
            return jsonify({"error": "No rates found for the given service type"}), 404

        rate = matching_rate['Rate'].values[0]

        return jsonify({
            "origin_city": origin['City'],
            "destination_city": destination['City'],
            "zone": zone,
            "rate": rate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
