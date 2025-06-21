# app.py
from flask import Flask, render_template, request, jsonify
from champ_placement import plaza
import pandas as pd
import traceback
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/results', methods=['POST'])
def get_results():
    try:
        print("=== API CALL RECEIVED ===")
        data = request.json
        print(f"Received data: {data}")
        
        height = data.get('height')
        jumping_url = data.get('jumping_url')
        agility_url = data.get('agility_url')
        
        print(f"Height: {height}")
        print(f"Jumping URL: {jumping_url}")
        print(f"Agility URL: {agility_url}")
        
        # Validate inputs based on whether URLs are provided
        has_urls = jumping_url and agility_url
        
        if has_urls:
            print("Using provided URLs - height not required")
            # When URLs are provided, height can be None
            # But we still need to pass something to plaza, so use a default
            height_to_use = height if height else "Lge"  # Default to Large if not specified
        else:
            # No URLs provided - height is required
            if not height:
                return jsonify({'success': False, 'error': 'Height selection is required when not using URLs'})
            height_to_use = height
        
        print(f"Using height: {height_to_use}")
        
        print("Creating plaza instance...")
        # Create plaza instance
        champ = plaza(
            height=height_to_use,
            JUMPING_url=jumping_url if jumping_url else None,
            AGILITY_url=agility_url if agility_url else None
        )
        
        print("Getting overall results...")
        # Get results
        top_20, all_results = champ.overall_results()
        print(champ.round_1_winner, type(champ.round_1_winner))
        print(f"Results shape: {all_results.shape}")
        print(f"Results columns: {all_results.columns.tolist()}")
        print(f"First few rows:\n{all_results.head()}")
        
        # Convert DataFrame to dict for JSON response
        # Reset index to include 'place' as a column
        results_dict = all_results.reset_index().to_dict('records')
        
        print(f"Converted to dict, length: {len(results_dict)}")
        print(f"First record: {results_dict[0] if results_dict else 'No records'}")
        
        return jsonify({'success': True, 'data': results_dict})
    
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"=== ERROR OCCURRED ===")
        print(f"Error: {error_msg}")
        print(f"Traceback:\n{traceback_str}")
        return jsonify({'success': False, 'error': error_msg})

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify API is working"""
    return jsonify({
        'success': True, 
        'message': 'API is working!',
        'data': [
            {'place': 1, 'Pairing': ['John Doe', 'Rex'], 'Points': 2, 'Round 1': 1, 'Round 2': 1},
            {'place': 2, 'Pairing': ['Jane Smith', 'Buddy'], 'Points': 4, 'Round 1': 2, 'Round 2': 2}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))