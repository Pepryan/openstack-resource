from flask import render_template, request, jsonify, session
from flask_login import login_required
import json
import os
import google.generativeai as genai
from datetime import datetime
from routes import ai_chat_bp
import config

# Configure Gemini AI
def configure_gemini(api_key):
    """Configure Gemini AI with API key"""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return False

def get_gemini_api_key():
    """Get Gemini API key from file"""
    api_key_file = os.path.join(config.DATA_DIR, 'gemini_api_key.txt')
    try:
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}")
    return None

def save_gemini_api_key(api_key):
    """Save Gemini API key to file"""
    api_key_file = os.path.join(config.DATA_DIR, 'gemini_api_key.txt')
    try:
        with open(api_key_file, 'w') as f:
            f.write(api_key)
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False

def get_openstack_context():
    """Get comprehensive OpenStack data context for AI analysis"""
    context = {
        'instances': [],
        'flavors': [],
        'volumes': [],
        'allocation': {},
        'reserved': {},
        'volume_stats': {},
        'ceph_storage': '',
        'placement_diff': [],
        'instance_ids_check': [],
        'ratio_config': [],
        'summary': {}
    }
    
    try:
        # Load instances data (AIO CSV)
        aio_path = os.path.join(config.DATA_DIR, 'aio.csv')
        if os.path.exists(aio_path):
            import pandas as pd
            df = pd.read_csv(aio_path, delimiter='|')
            context['instances'] = df.to_dict('records')
        
        # Load flavors data
        flavors_path = os.path.join(config.DATA_DIR, 'flavors.csv')
        if os.path.exists(flavors_path):
            import pandas as pd
            df = pd.read_csv(flavors_path, delimiter='|')
            context['flavors'] = df.to_dict('records')
        
        # Load volumes data
        volumes_path = os.path.join(config.DATA_DIR, 'volumes.json')
        if os.path.exists(volumes_path):
            with open(volumes_path, 'r') as f:
                volumes_data = json.load(f)
                context['volumes'] = volumes_data if isinstance(volumes_data, list) else []
        
        # Load allocation data (compute node resources)
        allocation_path = os.path.join(config.DATA_DIR, 'allocation.txt')
        if os.path.exists(allocation_path):
            with open(allocation_path, 'r') as f:
                allocation_lines = f.readlines()
                allocation_data = []
                for line in allocation_lines:
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        allocation_data.append({
                            'node_id': parts[0],
                            'hostname': parts[1],
                            'type': parts[2],
                            'ip': parts[3],
                            'status': parts[4],
                            'vcpu_used': int(parts[5]),
                            'vcpu_total': int(parts[6]),
                            'memory_used_mb': int(parts[7]) if len(parts) > 7 else 0,
                            'memory_total_mb': int(parts[8]) if len(parts) > 8 else 0
                        })
                context['allocation'] = allocation_data
        
        # Load reserved resources
        reserved_path = os.path.join(config.DATA_DIR, 'reserved.json')
        if os.path.exists(reserved_path):
            with open(reserved_path, 'r') as f:
                context['reserved'] = json.load(f)
        
        # Load volume statistics
        volume_stats_path = os.path.join(config.DATA_DIR, 'volume_stats.json')
        if os.path.exists(volume_stats_path):
            with open(volume_stats_path, 'r') as f:
                context['volume_stats'] = json.load(f)
        
        # Load Ceph storage information
        ceph_path = os.path.join(config.DATA_DIR, 'cephdf.txt')
        if os.path.exists(ceph_path):
            with open(ceph_path, 'r') as f:
                context['ceph_storage'] = f.read()
        
        # Load placement differences
        placement_path = os.path.join(config.DATA_DIR, 'placement_diff.json')
        if os.path.exists(placement_path):
            with open(placement_path, 'r') as f:
                context['placement_diff'] = json.load(f)
        
        # Load instance ID checks
        instance_check_path = os.path.join(config.DATA_DIR, 'instance_ids_check.json')
        if os.path.exists(instance_check_path):
            with open(instance_check_path, 'r') as f:
                context['instance_ids_check'] = json.load(f)
        
        # Load ratio configuration
        ratio_path = os.path.join(config.DATA_DIR, 'ratio.txt')
        if os.path.exists(ratio_path):
            with open(ratio_path, 'r') as f:
                ratio_lines = f.readlines()
                ratio_data = []
                for line in ratio_lines:
                    parts = line.strip().split(', ')
                    if len(parts) >= 3:
                        ratio_data.append({
                            'hostname': parts[0],
                            'cpu_ratio': float(parts[1]),
                            'memory_ratio': float(parts[2])
                        })
                context['ratio_config'] = ratio_data
        
        # Generate summary statistics
        context['summary'] = {
            'total_instances': len(context['instances']),
            'total_flavors': len(context['flavors']),
            'total_volumes': len(context['volumes']),
            'total_compute_nodes': len(context['allocation']) if isinstance(context['allocation'], list) else 0,
            'projects': list(set([inst.get('Project', 'unknown') for inst in context['instances']])),
            'active_instances': len([inst for inst in context['instances'] if inst.get('Status') == 'ACTIVE']),
            'shutoff_instances': len([inst for inst in context['instances'] if inst.get('Status') == 'SHUTOFF'])
        }
                
    except Exception as e:
        print(f"Error loading OpenStack context: {e}")
    
    return context

@ai_chat_bp.route('/ai-chat')
@login_required
def ai_chat():
    """AI Chat page"""
    api_key = get_gemini_api_key()
    return render_template('ai_chat.html', has_api_key=bool(api_key))

@ai_chat_bp.route('/api/ai-chat/send', methods=['POST'])
@login_required
def send_message():
    """Send message to AI"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get API key
        api_key = get_gemini_api_key()
        if not api_key:
            return jsonify({'error': 'Gemini API key not configured'}), 400
        
        # Configure Gemini
        if not configure_gemini(api_key):
            return jsonify({'error': 'Failed to configure Gemini AI'}), 500
        
        # Get OpenStack context
        openstack_context = get_openstack_context()
        
        # Create comprehensive system prompt with OpenStack context
        system_prompt = f"""
You are an AI assistant specialized in OpenStack infrastructure management and analysis.
You have access to comprehensive OpenStack environment data from a production cloud infrastructure.

=== ENVIRONMENT OVERVIEW ===
Summary: {json.dumps(openstack_context['summary'], indent=2)}

=== COMPUTE RESOURCES ===
Instances (Running VMs): {json.dumps(openstack_context['instances'], indent=2)}

Flavors (VM Templates): {json.dumps(openstack_context['flavors'], indent=2)}

Compute Node Allocation: {json.dumps(openstack_context['allocation'], indent=2)}

Reserved Resources: {json.dumps(openstack_context['reserved'], indent=2)}

CPU/Memory Ratios: {json.dumps(openstack_context['ratio_config'], indent=2)}

=== OVERCOMMIT RATIO EXPLANATION ===
Dalam environment production ini, overcommit ratio yang berbeda digunakan secara strategis:
- **1:1 Ratio**: Digunakan untuk instance production yang membutuhkan resource besar dan performa tinggi
- **1:4 Ratio**: Digunakan untuk instance campuran (mixed workload) dengan kebutuhan resource sedang
- **1:8 Ratio**: Digunakan untuk instance development/testing yang tidak memerlukan resource penuh

Ini adalah praktik normal untuk mengoptimalkan penggunaan resource hardware. Overcommit memungkinkan:
- Efisiensi resource yang lebih baik
- Penghematan biaya infrastruktur
- Fleksibilitas dalam alokasi resource berdasarkan kebutuhan workload

Ketika menganalisis data ratio.txt, perhatikan bahwa variasi ratio ini adalah by design, bukan masalah.

=== STORAGE RESOURCES ===
Volumes: {json.dumps(openstack_context['volumes'][:20], indent=2)}...

Volume Statistics: {json.dumps(openstack_context['volume_stats'], indent=2)}

Ceph Storage Status:
{openstack_context['ceph_storage']}

=== MONITORING & HEALTH ===
Placement Differences: {json.dumps(openstack_context['placement_diff'], indent=2)}

Instance ID Checks: {json.dumps(openstack_context['instance_ids_check'], indent=2)}

=== DATA INTERPRETATION GUIDE ===
1. Allocation Data Format: node_id hostname type ip status vcpu_used vcpu_total memory_used_mb memory_total_mb
2. Flavors: Complete specifications with RAM (MB), VCPUs, and Disk (GB)
3. Instances: Active workloads with their resource consumption
4. Ceph Storage: Raw storage capacity and pool utilization
5. Placement Diff: Discrepancies between placement service and actual allocation
6. Reserved Resources: Planned or reserved capacity for specific purposes

=== ANALYSIS CAPABILITIES ===
Provide detailed analysis for:
- **Resource Utilization**: Calculate actual CPU, RAM, and storage usage percentages
- **Capacity Planning**: Predict future resource needs and identify bottlenecks
- **Cost Optimization**: Identify over-provisioned resources and optimization opportunities
- **Performance Analysis**: Detect resource contention and performance issues
- **Infrastructure Health**: Monitor placement accuracy and resource consistency
- **Migration Planning**: Suggest optimal instance placement and consolidation
- **Storage Management**: Analyze Ceph utilization and volume distribution
- **Project Analysis**: Compare resource usage across different projects/tenants

=== RESPONSE GUIDELINES ===
- Always calculate specific percentages and metrics from the actual data
- Provide concrete recommendations with quantified benefits
- Identify specific hosts, instances, or resources when making suggestions
- Include both current state analysis and future planning recommendations
- Reference actual data points to support your analysis
- Consider the Indonesian context where applicable (some reserved resources have Indonesian descriptions)

Analyze the provided data comprehensively and provide actionable insights based on the actual infrastructure state.
"""
        
        # Create model and send message
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser Question: {message}"
        
        response = model.generate_content(full_prompt)
        
        return jsonify({
            'response': response.text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in AI chat: {e}")
        return jsonify({'error': f'AI service error: {str(e)}'}), 500

@ai_chat_bp.route('/api/ai-chat/save-api-key', methods=['POST'])
@login_required
def save_api_key():
    """Save Gemini API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        if save_gemini_api_key(api_key):
            return jsonify({'success': True, 'message': 'API key saved successfully'})
        else:
            return jsonify({'error': 'Failed to save API key'}), 500
            
    except Exception as e:
        print(f"Error saving API key: {e}")
        return jsonify({'error': f'Error saving API key: {str(e)}'}), 500

@ai_chat_bp.route('/api/ai-chat/check-api-key', methods=['GET'])
@login_required
def check_api_key():
    """Check if API key is configured"""
    api_key = get_gemini_api_key()
    return jsonify({'has_api_key': bool(api_key)})