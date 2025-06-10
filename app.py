""" Flask application for the website
"""
# app.py
from flask import Flask, render_template, request, jsonify
from champ_placement import plaza
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/results', methods=['POST'])
def get_results():
    try:
        data = request.json
        height = data.get('height')
        jumping_url = data.get('jumping_url')
        agility_url = data.get('agility_url')
        
        # Validate height
        if not height:
            return jsonify({'success': False, 'error': 'Height selection is required'})
        
        # Create plaza instance
        champ = plaza(
            height=height,
            JUMPING_url=jumping_url if jumping_url else None,
            AGILITY_url=agility_url if agility_url else None
        )
        
        # Get results
        top_20, all_results = champ.overall_results()
        
        # Convert DataFrame to dict for JSON response
        # Reset index to include 'place' as a column
        results_dict = all_results.reset_index().to_dict('records')
        
        return jsonify({'success': True, 'data': results_dict})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)