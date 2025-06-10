""" Flask application for the website
"""
# app.py
from flask import Flask, render_template, request, jsonify
from champ_placement import plaza
import pandas as pd
import traceback

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
        
        # Validate height
        if not height:
            return jsonify({'success': False, 'error': 'Height selection is required'})
        
        print("Creating plaza instance...")
        # Create plaza instance
        champ = plaza(
            height=height,
            JUMPING_url=jumping_url if jumping_url else None,
            AGILITY_url=agility_url if agility_url else None
        )
        
        print("Getting overall results...")
        # Get results
        top_20, all_results = champ.overall_results()
        
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

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)