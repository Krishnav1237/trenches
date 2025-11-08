"""
Flask API for serving agent personality data
Run on port 8081 alongside the Go backend on 8080
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_personality_service import get_agent_service

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize service
service = get_agent_service()

@app.route('/api/agents/<agent_id>/personality', methods=['GET'])
def get_agent_personality(agent_id):
    """Get detailed personality for a specific agent"""
    personality = service.get_agent_summary(agent_id)
    if personality:
        return jsonify(personality)
    return jsonify({'error': 'Agent not found'}), 404

@app.route('/api/agents/<agent_id>/full', methods=['GET'])
def get_agent_full(agent_id):
    """Get complete agent data including all fields"""
    agent = service.get_agent_personality(agent_id)
    if agent:
        return jsonify(agent)
    return jsonify({'error': 'Agent not found'}), 404

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all agents with optional filtering"""
    archetype = request.args.get('archetype')
    search = request.args.get('search')

    if search:
        agents = service.search_agents(search)
    elif archetype:
        agents = [service.get_agent_summary(a['id']) for a in service.get_agents_by_archetype(archetype)]
    else:
        agents = [service.get_agent_summary(a['id']) for a in service.get_all_agents()]

    return jsonify({
        'agents': agents,
        'count': len(agents)
    })

@app.route('/api/archetypes', methods=['GET'])
def list_archetypes():
    """Get list of all agent archetypes"""
    archetypes = service.get_archetype_list()
    return jsonify({
        'archetypes': archetypes,
        'count': len(archetypes)
    })

@app.route('/api/agents/recommendations/<agent_id>', methods=['GET'])
def get_recommendations(agent_id):
    """Get agent recommendations based on similarity"""
    agent = service.get_agent_personality(agent_id)
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404

    # Get agents from same ecosystem or classification
    ecosystem = agent.get('ecosystem')
    classification = agent.get('classification')

    recommendations = []
    all_agents = service.get_all_agents()

    for other in all_agents:
        if other['id'] == agent_id:
            continue

        score = 0
        # Same ecosystem = +3 points
        if other.get('ecosystem') == ecosystem:
            score += 3
        # Same classification = +2 points
        if other.get('classification') == classification:
            score += 2
        # Similar bullish level = +1 point
        if abs(other.get('bullish_level', 0.5) - agent.get('bullish_level', 0.5)) < 0.2:
            score += 1

        if score > 0:
            recommendations.append({
                **service.get_agent_summary(other['id']),
                'similarity_score': score
            })

    # Sort by score and return top 5
    recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)

    return jsonify({
        'agent_id': agent_id,
        'recommendations': recommendations[:5],
        'count': len(recommendations[:5])
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agents_loaded': len(service.get_all_agents())
    })

if __name__ == '__main__':
    print(f"🤖 Agent Personality API starting...")
    print(f"📊 Loaded {len(service.get_all_agents())} agents")
    print(f"🔧 Archetypes: {', '.join(service.get_archetype_list()[:5])}...")
    app.run(host='0.0.0.0', port=8081, debug=True)
