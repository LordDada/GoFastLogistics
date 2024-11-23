from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load data
pincode_data = pd.read_csv('Pincodes List.csv')  # Ensure this file exists and is correct
rates_data = pd.read_excel('Go Fast Logistics Commercial.xlsx')  # Ensure this file exists and is correct

@app.route('/')
def home():
    return "GoFastLogistics API is working!"

@app.route('/check_rates', methods=['POST'])
def check_rates():
    try:
        data = request.json
        origin_pincode = data.get('origin_pincode')
        destination_pincode = data.get('destination_pincode')
        service_type = data.get('service_type')

        # Validate inputs
        if not origin_pincode or not destination_pincode or not service_type:
            return jsonify({"error": "Missing required fields: origin_pincode, destination_pincode, or service_type"}), 400

        # Lookup origin and destination
        origin = pincode_data[pincode_data['Pincode'] == int(origin_pincode)].squeeze()
        destination = pincode_data[pincode_data['Pincode'] == int(destination_pincode)].squeeze()

        if origin.empty or destination.empty:
            return jsonify({"error": "No service available for the entered pincodes"}), 404

        # Determine Zone
        if origin['City'] == destination['City']:
            zone = 'Zone A'
        elif origin['State'] == destination['State']:
            zone = 'Zone B'
        elif origin['Zone'] == destination['Zone']:
            zone = 'Zone C'
        elif origin['City'] in ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'] and destination['City'] in ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']:
            zone = 'Zone D'
        elif origin['State'] in ['Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Arunachal Pradesh', 'Assam', 'Jammu and Kashmir', 'Andaman and Nicobar'] or destination['State'] in ['Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Arunachal Pradesh', 'Assam', 'Jammu and Kashmir', 'Andaman and Nicobar']:
            zone = 'Zone F'
        else:
            zone = 'Zone E'

        # Get rate
        rate_row = rates_data[(rates_data['Zone'] == zone) & (rates_data['Service'] == service_type)]
        if rate_row.empty:
            return jsonify({"error": f"No rate found for Zone: {zone}, Service: {service_type}"}), 404

        rate = rate_row['Rate'].values[0]

        # Return response
        return jsonify({
            "origin_city": origin['City'],
            "destination_city": destination['City'],
            "zone": zone,
            "rate": rate
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
