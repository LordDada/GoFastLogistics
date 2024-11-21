from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the data from your files
try:
    pincode_data = pd.read_csv('Pincodes List.csv')  # Adjust the file name if needed
    rates_data = pd.read_excel('Go Fast Logistics Commercial.xlsx')  # Ensure openpyxl is installed
except Exception as e:
    # Return a 500 error if files cannot be read
    app.logger.error(f"Error loading data: {str(e)}")
    exit("Error loading data files")

@app.route('/check_rates', methods=['POST'])
def check_rates():
    data = request.json
    origin_pincode = data.get('origin_pincode')
    destination_pincode = data.get('destination_pincode')
    service_type = data.get('service_type')

    # Validate that all necessary data is provided
    if not origin_pincode or not destination_pincode or not service_type:
        return jsonify({"error": "Missing required parameters"}), 400

    # Find origin and destination city/state based on pincodes
    origin = pincode_data[pincode_data['Pincode'] == int(origin_pincode)].squeeze()
    destination = pincode_data[pincode_data['Pincode'] == int(destination_pincode)].squeeze()

    if origin.empty or destination.empty:
        return jsonify({"error": "No service available for the entered pincodes"}), 404

    # Example zone logic (replace with actual logic for zone calculation)
    zone = 'Zone E'  # This is an example, adjust based on your logic
    rate = rates_data[(rates_data['Zone'] == zone) & (rates_data['Service'] == service_type)]['Rate'].values

    if rate.size == 0:
        return jsonify({"error": "Rate not found for the provided service type and zone"}), 404

    return jsonify({
        "origin_city": origin['City'],
        "destination_city": destination['City'],
        "zone": zone,
        "rate": rate[0]
    })

if __name__ == '__main__':
    # Bind the app to 0.0.0.0 for external access and specify the port (5000)
    app.run(host="0.0.0.0", port=5000, debug=True)
